"""Read-only GitHub inventory. CI evidence is not merge or production approval."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

OWNER = "98erickgarcia-maker"
REPOS = ("ebt-platform", "app-mail", "grupo-vikings-sst", "site-nutricao", "crm-casst-web")
REQUIRED = {
    13: (377961540, 377978392, 376713726),
    15: (377961540, 377978392, 376713726),
    16: (377961540, 377978392, 376713726),
    20: (379479309, 376713726),
    21: (376713726,),
    22: (377961540, 377978392, 376713726),
}
MAX_PAGES = 10


class AuditError(Exception):
    """Sanitized failure; never include response bodies or credentials."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AuditError("redirect_refused")


class GitHubReadOnly:
    def __init__(self, token: str = "") -> None:
        self.token = token
        self.opener = build_opener(NoRedirect)

    def get(self, repo: str, resource: str, **params):
        if repo not in REPOS or not re.fullmatch(r"[A-Za-z0-9_./-]+", resource):
            raise AuditError("invalid_endpoint")
        if ".." in resource or resource.startswith("/"):
            raise AuditError("invalid_endpoint")
        url = f"https://api.github.com/repos/{OWNER}/{repo}/{resource}"
        if params:
            url += "?" + urlencode(params)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "EBT-PR-Audit",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            with self.opener.open(Request(url, headers=headers, method="GET"), timeout=20) as response:
                raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise AuditError("response_too_large")
            return json.loads(raw)
        except HTTPError as exc:
            raise AuditError(f"github_http_{exc.code}") from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise AuditError("github_transport_or_json_error") from None

    def pages(self, repo: str, resource: str, key: str | None = None, **params) -> list:
        result = []
        for page in range(1, MAX_PAGES + 1):
            data = self.get(repo, resource, per_page=100, page=page, **params)
            rows = data.get(key) if key and isinstance(data, dict) else data
            if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows):
                raise AuditError("invalid_collection")
            result.extend(rows)
            if len(rows) < 100:
                if key and isinstance(data.get("total_count"), int) and data["total_count"] > len(result):
                    raise AuditError("incomplete_collection")
                return result
        raise AuditError("pagination_limit_not_complete")


def clean(value, limit: int = 300) -> str:
    return " ".join(str(value or "").split())[:limit]


def summarize_runs(runs: list[dict], sha: str, required=()) -> tuple[str, list[dict]]:
    latest = {}
    for run in runs:
        if run.get("head_sha") != sha or run.get("event") != "pull_request":
            continue
        wid = run.get("workflow_id")
        if type(wid) is not int or type(run.get("id")) is not int:
            raise AuditError("invalid_workflow_identity")
        rank = (int(run.get("run_number", 0)), int(run.get("run_attempt", 1)), run["id"])
        if wid not in latest or rank > latest[wid][0]:
            latest[wid] = (rank, run)
    evidence = [{k: r.get(k) for k in ("id", "workflow_id", "name", "head_sha", "event", "status", "conclusion", "run_attempt")}
                for _, r in sorted(latest.values(), key=lambda item: item[1]["workflow_id"])]
    if not evidence:
        return "NOT_RUN", evidence
    if any(r.get("status") == "completed" and r.get("conclusion") not in ("success", "skipped", "neutral") for r in evidence):
        return "FAIL", evidence
    if any(r.get("status") != "completed" for r in evidence):
        return "WAITING_CI", evidence
    if required and not set(required).issubset(latest):
        return "MISSING_REQUIRED_WORKFLOW", evidence
    if any(r.get("conclusion") != "success" for r in evidence):
        return "NOT_PROVEN", evidence
    return ("PASS_CONFIGURED_CI" if required else "OBSERVED_CI_SUCCESS"), evidence


def summarize_reviews(reviews: list[dict], sha: str, author: str) -> str:
    latest = {}
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login")
        if not login or login == author or user.get("type") == "Bot":
            continue
        if review.get("state") in ("PENDING", "COMMENTED"):
            continue
        rank = (str(review.get("submitted_at") or ""), int(review.get("id", 0)))
        if login not in latest or rank > latest[login][0]:
            latest[login] = (rank, review)
    if any(r.get("state") == "CHANGES_REQUESTED" for _, r in latest.values()):
        return "CHANGES_REQUESTED"
    if any(r.get("state") == "APPROVED" and r.get("commit_id") == sha for _, r in latest.values()):
        return "APPROVAL_OBSERVED_THREADS_NOT_CHECKED"
    return "REVIEW_PENDING"


def audit_pr(client, repo: str, number: int) -> dict:
    if type(number) is not int or number < 1:
        raise AuditError("invalid_pr_number")
    resource = f"pulls/{number}"
    before = client.get(repo, resource)
    head, base = before["head"]["sha"], before["base"]["sha"]
    runs = client.pages(repo, "actions/runs", "workflow_runs", head_sha=head, event="pull_request")
    reviews = client.pages(repo, resource + "/reviews")
    files = client.pages(repo, resource + "/files")
    after = client.get(repo, resource)
    def fingerprint(p):
        return (p["head"]["sha"], p["base"]["sha"], p["base"]["ref"], p["state"], p.get("draft"))
    stable = fingerprint(before) == fingerprint(after)
    status, evidence = summarize_runs(runs, head, REQUIRED.get(number, ()) if repo == "ebt-platform" else ())
    filenames = sorted({f["filename"] for f in files})
    if len(files) != before.get("changed_files") or len(filenames) != len(files):
        raise AuditError("changed_files_incomplete")
    return {"repository": f"{OWNER}/{repo}", "number": number, "title": clean(before.get("title")),
            "url": f"https://github.com/{OWNER}/{repo}/pull/{number}",
            "head_sha": head, "base_sha": base, "head_ref": before["head"]["ref"], "base_ref": before["base"]["ref"],
            "draft": before.get("draft"), "mergeable": after.get("mergeable"),
            "snapshot_stable": stable, "ci": status if stable else "HEAD_OR_BASE_MOVED",
            "review": summarize_reviews(reviews, head, before["user"]["login"]),
            "workflows": evidence, "files": filenames, "merge_authorized": False,
            "limits": ["No diff review", "Review threads, check-runs, commit statuses and rulesets not checked",
                       "No production or visual acceptance", "PR CI only; push and dispatch evidence excluded",
                       "Run merge-base context and concurrent new reviews/reruns require revalidation"]}


def inventory(client, repos: list[str]) -> dict:
    repos = list(dict.fromkeys(repos))
    report = {"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
              "complete": True, "pull_requests": [], "errors": [], "overlaps": [], "schedule_runs": []}
    for repo in repos:
        try:
            entries = client.pages(repo, "pulls", state="open")
            numbers = [p["number"] for p in entries]
            if len(numbers) != len(set(numbers)):
                raise AuditError("duplicate_pr_in_listing")
            for number in numbers:
                try:
                    row = audit_pr(client, repo, number)
                    report["pull_requests"].append(row)
                    if not row["snapshot_stable"]:
                        report["complete"] = False
                        report["errors"].append({"repo": repo, "pr": number, "code": "snapshot_moved"})
                except (AuditError, KeyError, TypeError, ValueError, AttributeError) as exc:
                    report["complete"] = False
                    report["errors"].append({"repo": repo, "pr": number, "code": str(exc) if isinstance(exc, AuditError) else "invalid_pr_schema"})
            if set(numbers) != {p["number"] for p in client.pages(repo, "pulls", state="open")}:
                report["complete"] = False
                report["errors"].append({"repo": repo, "code": "pr_list_moved"})
        except (AuditError, KeyError, TypeError, ValueError, AttributeError) as exc:
            report["complete"] = False
            report["errors"].append({"repo": repo, "code": str(exc) if isinstance(exc, AuditError) else "invalid_repo_schema"})
    rows = report["pull_requests"]
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            overlap = sorted(set(a["files"]) & set(b["files"]))
            if a["repository"] == b["repository"] and overlap:
                report["overlaps"].append({"repository": a["repository"], "prs": [a["number"], b["number"]],
                                           "files": overlap, "interpretation": "overlap_not_proven_conflict"})
    if "ebt-platform" in repos:
        try:
            data = client.get("ebt-platform", "actions/runs", event="schedule", per_page=100)
            report["schedule_total_count"] = data["total_count"]
            report["schedule_runs"] = [{k: r.get(k) for k in ("id", "run_attempt", "event", "path", "head_branch", "head_sha", "created_at", "status", "conclusion")}
                                       for r in data["workflow_runs"]]
            report["schedule_limit"] = "Latest 100 repository schedule runs; not full history"
        except (AuditError, KeyError, TypeError, AttributeError) as exc:
            report["complete"] = False
            report["errors"].append({"repo": "ebt-platform", "code": str(exc) if isinstance(exc, AuditError) else "invalid_schedule_schema"})
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    return report


def write_report(path: Path, report: dict) -> None:
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temp = Path(stream.name)
            json.dump(report, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", choices=REPOS)
    parser.add_argument("--output", type=Path, default=Path("pr-audit.json"))
    args = parser.parse_args()
    report = inventory(GitHubReadOnly(os.environ.get("GH_TOKEN", "")), args.repo or list(REPOS))
    try:
        write_report(args.output, report)
    except OSError:
        print("audit_output_write_failed", file=sys.stderr)
        return 3
    print(json.dumps({"complete": report["complete"], "prs_observed": len(report["pull_requests"]),
                      "errors": len(report["errors"]), "merge_authorized": False}))
    return 0 if report["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
