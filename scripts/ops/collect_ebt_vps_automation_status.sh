#!/usr/bin/env bash
set -Eeuo pipefail

[[ "$EUID" -eq 0 ]] || { echo "Run with sudo/root." >&2; exit 1; }

python3 - <<'PY'
import json
import pathlib
import subprocess

TIMERS = [
    "ebt-schedule-watchdog.timer",
    "ebt-production-watch-vps.timer",
    "ebt-engineering-runner.timer",
    "ebt-engineering-watch.timer",
]

def systemctl(command, unit):
    result = subprocess.run(["systemctl", command, unit], text=True, capture_output=True, timeout=10)
    return {"rc": result.returncode, "value": (result.stdout or result.stderr).strip()[:120]}

report = {"timers": {unit: {
    "enabled": systemctl("is-enabled", unit),
    "active": systemctl("is-active", unit),
} for unit in TIMERS}}

workspace = pathlib.Path("/var/lib/ebt-engineering/workspace")
if (workspace / ".git").exists():
    branch = subprocess.run(["git", "-C", str(workspace), "branch", "--show-current"],
                            text=True, capture_output=True, timeout=10)
    head = subprocess.run(["git", "-C", str(workspace), "rev-parse", "HEAD"],
                          text=True, capture_output=True, timeout=10)
    report["flow_workspace"] = {
        "branch": branch.stdout.strip() if branch.returncode == 0 else "UNAVAILABLE",
        "head": head.stdout.strip() if head.returncode == 0 else "UNAVAILABLE",
    }

def selected_json(path, keys):
    p = pathlib.Path(path)
    if not p.exists():
        return {"state": "MISSING"}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"state": "INVALID_JSON"}
    return {k: data.get(k) for k in keys if k in data}

report["engineering_checkpoint"] = selected_json(
    "/var/lib/ebt-engineering/state/checkpoint.json",
    ["status","current_task","completed","source_commit","synced_sha","sync_task","sync_error","blocked_reason","updated_at"],
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

print(json.dumps(report, indent=2, ensure_ascii=True))
PY
