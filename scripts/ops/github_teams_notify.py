"""Notify a Microsoft Teams Workflow when important EBT GitHub events occur.

No third-party dependencies, no untrusted PR code, no secret or webhook URL in logs.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib import error, parse, request

REPO = "98erickgarcia-maker/ebt-platform"
BASE_URL = "https://github.com/" + REPO
ALLOWED_WEBHOOK_DOMAINS = ("logic.azure.com", "api.powerplatform.com", "powerautomate.com")
INCIDENT_PREFIX = "[EBT OPS]"
MAX_EVENT_BYTES = 1_000_000


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def clean(value, limit=160):
    """Keep event text short, single-line and safe for Teams formatting."""
    normalized = re.sub(r"[\x00-\x1f\x7f]+", " ", str(value or ""))
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:limit]


def _int_or_none(value):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def event_message(name, event):
    """Return a short user-facing notification or None for low-value events."""
    if not isinstance(event, dict):
        return None
    if name == "workflow_dispatch":
        return "[EBT] Integração GitHub → Teams: teste solicitado manualmente.\n" + BASE_URL + "/actions"
    if name == "push":
        if event.get("ref") != "refs/heads/main":
            return None
        sha = str(event.get("after") or "")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            return None
        summary = clean((event.get("head_commit") or {}).get("message"), 130)
        return f"[EBT] Novo commit na main: {sha[:8]}\n{summary}\n{BASE_URL}/commit/{sha}"
    if name == "pull_request_target":
        action = event.get("action")
        if action not in {"opened", "reopened", "synchronize", "ready_for_review", "closed"}:
            return None
        pr = event.get("pull_request") or {}
        number = _int_or_none(pr.get("number") or event.get("number"))
        if number is None:
            return None
        status = "integrado" if action == "closed" and pr.get("merged") is True else (
            "fechado sem integração" if action == "closed" else {
                "opened": "aberto", "reopened": "reaberto", "synchronize": "atualizado",
                "ready_for_review": "pronto para revisão"
            }[action])
        title = clean(pr.get("title"), 150)
        return f"[EBT] PR #{number} {status}: {title}\n{BASE_URL}/pull/{number}"
    if name == "workflow_run":
        run = event.get("workflow_run") or {}
        if event.get("action") != "completed":
            return None
        conclusion = str(run.get("conclusion") or "")
        if conclusion not in {"failure", "timed_out", "startup_failure", "action_required", "cancelled"}:
            return None
        run_id = _int_or_none(run.get("id"))
        if run_id is None:
            return None
        title = clean(run.get("name"), 120)
        branch = clean(run.get("head_branch"), 60)
        return f"[EBT] Falha de automação ({conclusion}): {title}\nBranch: {branch}\n{BASE_URL}/actions/runs/{run_id}"
    if name == "issues":
        action = event.get("action")
        issue = event.get("issue") or {}
        if action not in {"opened", "reopened", "closed"}:
            return None
        if not str(issue.get("title") or "").startswith(INCIDENT_PREFIX):
            return None
        if (issue.get("user") or {}).get("login") != "github-actions[bot]":
            return None
        number = _int_or_none(issue.get("number"))
        if number is None:
            return None
        state = "resolvido" if action == "closed" else "detectado"
        return f"[EBT] Incidente {state}: #{number} {clean(issue.get('title'), 120)}\n{BASE_URL}/issues/{number}"
    return None


def webhook_is_allowed(url):
    try:
        uri = parse.urlsplit(url)
        host = (uri.hostname or "").lower()
        return (uri.scheme == "https" and uri.port in (None, 443)
                and "/workflows/" in uri.path and bool(host) and not uri.username and not uri.password
                and not uri.fragment and any(host == domain or host.endswith("." + domain)
                                         for domain in ALLOWED_WEBHOOK_DOMAINS))
    except ValueError:
        return False


def send_to_teams(url, message, opener=None, pause=time.sleep):
    """POST a Teams Workflows 'text' message, retrying rate limits and server errors."""
    if not webhook_is_allowed(url):
        raise ValueError("invalid_teams_workflows_webhook_url")
    payload = json.dumps({"text": message}, ensure_ascii=False).encode("utf-8")
    client = opener or request.build_opener(NoRedirect())
    for attempt in range(3):
        req = request.Request(url, data=payload, method="POST", headers={
            "Content-Type": "application/json; charset=utf-8", "User-Agent": "EBT-GitHub-Teams/1"
        })
        try:
            with client.open(req, timeout=12) as resp:
                if not 200 <= resp.status < 300:
                    raise RuntimeError("teams_webhook_non_2xx_response")
                resp.read(4096)
                return
        except error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < 2:
                pause(2 ** attempt)
                continue
            raise RuntimeError("teams_webhook_http_" + str(exc.code)) from None
        except (error.URLError, OSError, TimeoutError):
            if attempt < 2:
                pause(2 ** attempt)
                continue
            raise RuntimeError("teams_webhook_network_error") from None
    raise RuntimeError("teams_webhook_retry_exhausted")


def report_message(report, run_id):
    """Report only incident transitions from the 15-minute operational watcher.

    GitHub_TOKEN-created issues do not normally trigger other Actions workflows,
    so the monitor itself sends Teams messages when an incident changes.
    """
    transition = report.get("notification")
    if transition not in {"create", "update", "close"}:
        return None
    checks = report.get("checks") or []
    failures = sum(row.get("state") == "FAIL" for row in checks)
    uncertain = sum(row.get("state") == "INCONCLUSIVE" for row in checks)
    description = {"create": "novo incidente", "update": "incidente atualizado", "close": "incidente encerrado"}[transition]
    action_url = BASE_URL + "/actions/runs/" + str(run_id) if _int_or_none(run_id) else BASE_URL + "/actions"
    return (f"[EBT] Monitor de produção: {description}.\n"
            f"Falhas: {failures} | Inconclusivos: {uncertain}\n{action_url}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--production-report")
    args = parser.parse_args(argv if argv is not None else [])
    if os.getenv("GITHUB_REPOSITORY") != REPO:
        print("SKIPPED: repository not approved")
        return 0
    if args.production_report:
        if os.getenv("GITHUB_REF") != "refs/heads/main":
            print("SKIPPED: operational reports only notify from main")
            return 0
        try:
            path = Path(args.production_report)
            if path.stat().st_size > MAX_EVENT_BYTES:
                raise ValueError("report_too_large")
            report = json.loads(path.read_text(encoding="utf-8"))
            message = report_message(report, os.getenv("GITHUB_RUN_ID", ""))
        except (OSError, ValueError, UnicodeError, TypeError):
            print("ERROR: invalid production watch report", file=sys.stderr)
            return 1
    else:
        path = os.getenv("GITHUB_EVENT_PATH")
        if not path:
            print("ERROR: GITHUB_EVENT_PATH missing", file=sys.stderr)
            return 1
        try:
            if Path(path).stat().st_size > MAX_EVENT_BYTES:
                raise ValueError("event_too_large")
            event = json.loads(Path(path).read_text(encoding="utf-8"))
            message = event_message(os.getenv("GITHUB_EVENT_NAME", ""), event)
        except (OSError, ValueError, UnicodeError):
            print("ERROR: invalid GitHub event data", file=sys.stderr)
            return 1
    if not message:
        print("SKIPPED: event does not require notification")
        return 0
    webhook = os.getenv("TEAMS_WORKFLOWS_WEBHOOK_URL", "")
    if not webhook:
        print("PENDING: configure repository secret TEAMS_WORKFLOWS_WEBHOOK_URL")
        return 0
    try:
        send_to_teams(webhook, message)
    except (ValueError, RuntimeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    print("SENT: Teams webhook accepted notification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
