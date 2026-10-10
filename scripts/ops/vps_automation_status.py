#!/usr/bin/env python3
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

TIMERS = (
    "ebt-schedule-watchdog.timer",
    "ebt-production-watch-vps.timer",
    "ebt-engineering-runner.timer",
    "ebt-engineering-watch.timer",
)
EXPECTED_BRANCH = "codex/flow-history-proposal-vps-20261009"
INITIAL_PROPOSAL_SHA = "0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0"
EXPECTED_REMOTE = "git@github.com:98erickgarcia-maker/ebt-platform.git"
EXPECTED_PRODUCT_ORIGIN = "https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io"
EXPECTED_PRODUCT_SCOPE = "read_only_external_checks_not_full_production_acceptance"
WORKSPACE = Path("/var/lib/ebt-engineering/workspace")
CONTROLLER_ENV = Path("/etc/ebt-engineering-controller.env")


def run(argv, timeout=10):
    result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    return {"rc": result.returncode, "value": (result.stdout or result.stderr).strip()[:160]}


def selected_json(path, keys):
    p = Path(path)
    if not p.exists():
        return {"state": "MISSING"}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"state": "INVALID_JSON"}
    if not isinstance(data, dict):
        return {"state": "INVALID_JSON"}
    return {k: data.get(k) for k in keys if k in data}


def root_private(path):
    try:
        info = Path(path).stat()
    except OSError:
        return False
    return (
        stat.S_ISREG(info.st_mode)
        and info.st_uid == 0
        and (stat.S_IMODE(info.st_mode) in (0o400, 0o600))
        and not Path(path).is_symlink()
    )


def parse_controller_paths():
    result = {"env_root_private": root_private(CONTROLLER_ENV)}
    try:
        lines = CONTROLLER_ENV.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    values = {}
    for line in lines:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in ("EBT_ENGINEERING_GIT_KEY", "EBT_ENGINEERING_KNOWN_HOSTS"):
            values[key] = value
    key = values.get("EBT_ENGINEERING_GIT_KEY")
    known = values.get("EBT_ENGINEERING_KNOWN_HOSTS")
    result["git_key_root_private"] = bool(key and root_private(key))
    result["known_hosts_root_private"] = bool(known and root_private(known))
    if key:
        result["agent_cannot_read_git_key"] = run(["runuser", "-u", "ebt-scout", "--", "test", "-r", key])["rc"] != 0
    if known:
        result["agent_cannot_read_known_hosts"] = run(["runuser", "-u", "ebt-scout", "--", "test", "-r", known])["rc"] != 0
    return result


def collect():
    report = {
        "timers": {
            unit: {"enabled": run(["systemctl", "is-enabled", unit]), "active": run(["systemctl", "is-active", unit])}
            for unit in TIMERS
        }
    }

    if (WORKSPACE / ".git").exists():
        report["flow_workspace"] = {
            "branch": run(["git", "-C", str(WORKSPACE), "branch", "--show-current"])["value"],
            "head": run(["git", "-C", str(WORKSPACE), "rev-parse", "HEAD"])["value"],
            "remote": run(["git", "-C", str(WORKSPACE), "remote", "get-url", "--push", "origin"])["value"],
            "agent_cannot_read_git": run(
                ["runuser", "-u", "ebt-scout", "--", "test", "-r", str(WORKSPACE / ".git/config")]
            )["rc"] != 0,
        }
    else:
        report["flow_workspace"] = {"state": "MISSING"}

    report["controller_transport"] = parse_controller_paths()
    report["engineering_checkpoint"] = selected_json(
        "/var/lib/ebt-engineering/state/checkpoint.json",
        ["status","current_task","completed","source_commit","sync_sha","synced_sha","sync_task","sync_error","blocked_reason","updated_at"],
    )
    report["engineering_heartbeat"] = selected_json(
        "/var/lib/ebt-engineering/state/heartbeat.json",
        ["status","task","module_id","source_commit","updated_at","progress_at","blocked_reason"],
    )
    report["product_watch"] = selected_json(
        "/var/lib/ebt-production-watch/report.json",
        ["observed_at","origin","healthy_in_scope","notification","scope"],
    )
    report["schedule_watchdog"] = selected_json(
        "/var/lib/ebt-watch/state.json",
        ["signature","last_observation","last_valid_observation"],
    )
    return report


def evaluate(report):
    failures = []
    for unit in TIMERS:
        state = report.get("timers", {}).get(unit, {})
        if state.get("enabled", {}).get("value") != "enabled":
            failures.append(f"{unit}:not_enabled")
        if state.get("active", {}).get("value") != "active":
            failures.append(f"{unit}:not_active")

    workspace = report.get("flow_workspace", {})
    if workspace.get("branch") != EXPECTED_BRANCH:
        failures.append("flow_workspace:wrong_branch")
    if workspace.get("remote") != EXPECTED_REMOTE:
        failures.append("flow_workspace:wrong_remote")
    if workspace.get("agent_cannot_read_git") is not True:
        failures.append("flow_workspace:agent_git_access")

    transport = report.get("controller_transport", {})
    for key in (
        "env_root_private",
        "git_key_root_private",
        "known_hosts_root_private",
        "agent_cannot_read_git_key",
        "agent_cannot_read_known_hosts",
    ):
        if transport.get(key) is not True:
            failures.append(f"controller_transport:{key}")

    product = report.get("product_watch", {})
    if product.get("origin") != EXPECTED_PRODUCT_ORIGIN:
        failures.append("product_watch:unexpected_origin")
    if product.get("notification") != "disabled":
        failures.append("product_watch:notification_not_disabled")
    if product.get("scope") != EXPECTED_PRODUCT_SCOPE:
        failures.append("product_watch:unexpected_scope")

    watchdog = report.get("schedule_watchdog", {})
    if watchdog.get("state") in ("MISSING", "INVALID_JSON") or "last_observation" not in watchdog:
        failures.append("schedule_watchdog:missing_observation")

    checkpoint = report.get("engineering_checkpoint", {})
    heartbeat = report.get("engineering_heartbeat", {})
    engineering_status = heartbeat.get("status") or checkpoint.get("status") or "PENDING_FIRST_CYCLE"

    expected_head = (
        checkpoint.get("synced_sha")
        or checkpoint.get("sync_sha")
        or checkpoint.get("source_commit")
        or INITIAL_PROPOSAL_SHA
    )
    actual_head = workspace.get("head")
    head_consistent = actual_head == expected_head
    if not head_consistent:
        failures.append("flow_workspace:head_checkpoint_mismatch")

    last_schedule = watchdog.get("last_observation") if isinstance(watchdog.get("last_observation"), dict) else {}
    product_health = (
        "HEALTHY" if product.get("healthy_in_scope") is True
        else "UNHEALTHY" if product.get("healthy_in_scope") is False
        else "UNKNOWN"
    )
    schedule_health = last_schedule.get("status", "UNKNOWN")

    return {
        "installation_integrity": "PASS" if not failures else "FAIL",
        "integrity_failures": failures,
        "observed_health": {
            "product": product_health,
            "github_schedule": schedule_health,
            "engineering": engineering_status,
            "workspace_head_consistent": head_consistent,
        },
        "controller_consistency": {
            "expected_head": expected_head,
            "actual_head": actual_head,
        },
        "evidence": report,
    }


def main():
    if os.geteuid() != 0:
        print("Run with sudo/root.", file=sys.stderr)
        return 1
    result = evaluate(collect())
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["installation_integrity"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
