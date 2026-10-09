"""EBT 24x7 read-only operational monitors, independent of the runtime branch."""
import argparse
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib import error, parse, request

ORIGIN = "https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io"
REPO = "98erickgarcia-maker/ebt-platform"
ISSUE_MARKER = "<!-- ebt-ops-watch-v1 -->"


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def url_for(path):
    if not path.startswith("/") or path.startswith("//"):
        raise ValueError("unapproved_target")
    url = parse.urljoin(ORIGIN + "/", path)
    if (parse.urlsplit(url).scheme, parse.urlsplit(url).netloc) != (
            parse.urlsplit(ORIGIN).scheme, parse.urlsplit(ORIGIN).netloc):
        raise ValueError("unapproved_target")
    return url


def get(path):
    req = request.Request(url_for(path), headers={"User-Agent": "EBT-Watch/1"})
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=10) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read(65536)
    except error.HTTPError as ex:
        return ex.code, ex.headers.get("Content-Type", ""), b""
    except (error.URLError, OSError, TimeoutError):
        return None, "", b""


def row(agent, name, response, passed, reason):
    code = response[0]
    return {"agent": agent, "check": name, "state":
            "INCONCLUSIVE" if code in (None, 429) else "PASS" if passed else "FAIL",
            "http": code, "reason": "network_uncertain" if code is None else
            "rate_limited" if code == 429 else reason}


def health(fetch=get):
    rows, versions = [], []
    for path, expected in (("/health/live", "alive"), ("/health/ready", "ready")):
        response = fetch(path)
        try:
            body = json.loads(response[2])
        except (ValueError, UnicodeError):
            body = None
        passed = (response[0] == 200 and "json" in response[1].lower()
                  and isinstance(body, dict) and body.get("status") == expected
                  and isinstance(body.get("version"), str) and bool(body["version"]))
        rows.append(row("Disponibilidade", path, response, passed, "health_contract"))
        versions.append(body["version"] if passed else None)
    if all(versions):
        rows.append(row("Releases", "live_ready_version", (200, "", b""),
                        versions[0] == versions[1], "version_mismatch"))
    return rows


def security(fetch=get):
    rows = []
    for path in ("/api/auth/me", "/api/platform/v1/applications"):
        response = fetch(path)
        rows.append(row("Seguranca", path, response, response[0] in (401, 403),
                        "unauthenticated_access_must_be_denied"))
    return rows


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "script" and attrs.get("type") == "module" and attrs.get("src"):
            self.paths.append(("js", attrs["src"]))
        if tag == "link" and attrs.get("rel") == "stylesheet" and attrs.get("href"):
            self.paths.append(("css", attrs["href"]))


def frontend(fetch=get):
    response = fetch("/")
    html = response[2].decode("utf-8", "replace")
    passed = (response[0] == 200 and "text/html" in response[1].lower()
              and "EBT" in html and 'id="root"' in html)
    checks = [row("Frontend", "react_entry", response, passed, "html_entry")]
    if not passed:
        return checks
    assets = Assets()
    assets.feed(html)
    if not any(kind == "js" for kind, _ in assets.paths):
        checks.append(row("Frontend", "module_script", (200, "", b""), False, "missing_js"))
    for kind, path in assets.paths[:4]:
        try:
            if not parse.urlsplit(url_for(path)).path.startswith("/assets/"):
                raise ValueError("unsafe_asset")
        except ValueError:
            checks.append(row("Frontend", kind, (200, "", b""), False, "unsafe_asset"))
            continue
        response = fetch(path)
        mimetype = "javascript" if kind == "js" else "text/css"
        checks.append(row("Frontend", kind, response, response[0] == 200
                          and bool(response[2]) and mimetype in response[1].lower(), "asset_contract"))
    return checks


def check_all():
    with ThreadPoolExecutor(max_workers=3) as pool:
        groups = list(pool.map(lambda f: f(), (health, security, frontend)))
    return [item for group in groups for item in group]


def fingerprint(checks):
    failed = sorted((r["agent"], r["check"], r["state"], str(r["http"]))
                    for r in checks if r["state"] != "PASS")
    return hashlib.sha256(json.dumps(failed).encode()).hexdigest()[:20]


def incident_transition(checks, existing):
    if not checks:
        return "none"
    if all(r["state"] == "PASS" for r in checks):
        return "close" if existing else "none"
    if not existing:
        return "create"
    return "none" if "<!-- state:" + fingerprint(checks) + " -->" in (existing.get("body") or "") else "update"


def github(method, path, token, payload=None):
    if not path.startswith("/repos/" + REPO + "/issues"):
        raise ValueError("unsafe_github_write_target")
    req = request.Request("https://api.github.com" + path, method=method,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json",
                 "Accept": "application/vnd.github+json", "User-Agent": "EBT-Watch/1"})
    with request.build_opener(NoRedirect()).open(req, timeout=15) as response:
        return json.load(response)


def notify(report, token):
    base = "/repos/" + REPO + "/issues"
    existing = None
    for page in range(1, 11):
        issues = github("GET", base + "?state=open&per_page=100&page=" + str(page), token)
        existing = next((item for item in issues
                         if not item.get("pull_request") and
                         item.get("user", {}).get("login") == "github-actions[bot]" and
                         ISSUE_MARKER in (item.get("body") or "")), None)
        if existing or len(issues) < 100:
            break
    else:
        raise RuntimeError("issue_listing_incomplete")
    action = incident_transition(report["checks"], existing)
    run_url = "https://github.com/" + REPO + "/actions/runs/" + os.getenv("GITHUB_RUN_ID", "")
    body = "\n".join([
        ISSUE_MARKER, "<!-- state:" + fingerprint(report["checks"]) + " -->",
        "# EBT Enterprise - monitoramento externo", "Verificado: " + report["observed_at"],
        "", "| Agente | Verificacao | Estado | HTTP |", "|---|---|---|---|",
        *["| {agent} | {check} | {state} | {http} |".format(**r) for r in report["checks"]],
        "", "Execucao: " + run_url,
        "INCONCLUSIVE nao comprova queda do servidor.",
        "Monitoramento nao realiza deploy, SQL, envios ou reinicios."
    ])
    if action == "create":
        github("POST", base, token, {"title": "[EBT OPS] Incidente em verificacao externa", "body": body})
    elif action == "update":
        github("PATCH", base + "/" + str(existing["number"]), token, {"body": body})
    elif action == "close":
        github("POST", base + "/" + str(existing["number"]) + "/comments", token,
               {"body": "Verificacoes deste escopo retornaram a PASS: " + run_url})
        github("PATCH", base + "/" + str(existing["number"]), token, {"state": "closed"})
    return action


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="production-watch.json")
    args = parser.parse_args()
    attempts = [check_all()]
    if any(r["state"] != "PASS" for r in attempts[-1]):
        time.sleep(3)
        attempts.append(check_all())
    checks = attempts[-1]
    report = {"observed_at": datetime.now(timezone.utc).isoformat(),
              "origin": ORIGIN, "checks": checks, "attempts": attempts,
              "healthy_in_scope": bool(checks) and all(r["state"] == "PASS" for r in checks),
              "notification": "disabled",
              "scope": "read_only_external_checks_not_full_production_acceptance"}
    if os.getenv("EBT_NOTIFY") == "true":
        if os.getenv("GITHUB_REPOSITORY") != REPO or os.getenv("GITHUB_REF") != "refs/heads/main":
            raise RuntimeError("notification_not_authorized_for_branch")
        try:
            report["notification"] = notify(report, os.environ["GH_TOKEN"])
        except Exception as exc:
            report["notification"] = "failed:" + type(exc).__name__
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = "\n".join("- {agent}: {check} = {state} ({http})".format(**r) for r in checks)
    summary += "\nNotificacao: " + report["notification"] + "\n"
    print(summary)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as log:
            log.write("## EBT Production Watch\n\n" + summary)
    return 0 if report["healthy_in_scope"] and not report["notification"].startswith("failed:") else 1


if __name__ == "__main__":
    raise SystemExit(main())
