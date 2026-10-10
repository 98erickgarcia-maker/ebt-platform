#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

SOURCE_ROOT="${SOURCE_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)}"
EXPECTED_SOURCE_SHA="${EXPECTED_SOURCE_SHA:-}"
APP_DIR="/opt/ebt-production-watch"
SERVICE="/etc/systemd/system/ebt-production-watch-vps.service"
TIMER="/etc/systemd/system/ebt-production-watch-vps.timer"
STATE_DIR="/var/lib/ebt-production-watch"
SERVICE_USER="ebt-watch"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"; }

[[ "$EUID" -eq 0 ]] || fail "Run with sudo/root."
for binary in git python3 systemctl install useradd id; do need "$binary"; done
[[ -d /run/systemd/system ]] || fail "systemd is not running on this host."
[[ -d "$SOURCE_ROOT/.git" ]] || fail "SOURCE_ROOT must be a Git checkout."
[[ "$EXPECTED_SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]] || fail "Set EXPECTED_SOURCE_SHA to the reviewed branch SHA."
actual_source="$(git -C "$SOURCE_ROOT" rev-parse HEAD)"
[[ "$actual_source" == "$EXPECTED_SOURCE_SHA" ]] || fail "SOURCE_ROOT SHA differs from EXPECTED_SOURCE_SHA."
[[ -z "$(git -C "$SOURCE_ROOT" status --porcelain --untracked-files=all)" ]] || fail "SOURCE_ROOT must be clean."

for path in   "$SOURCE_ROOT/scripts/ops/production_watch.py"   "$SOURCE_ROOT/tests/ops/test_production_watch.py"   "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.service"   "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.timer"; do
  [[ -f "$path" && ! -L "$path" ]] || fail "Missing or unsafe source file: $path"
done

/usr/bin/python3 -m py_compile "$SOURCE_ROOT/scripts/ops/production_watch.py"
/usr/bin/python3 -m unittest discover -s "$SOURCE_ROOT/tests/ops" -p 'test_production_watch.py' -v

grep -Fq 'Environment=EBT_NOTIFY=false' "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.service"   || fail "Service must keep notifications disabled."
grep -Fq 'User=ebt-watch' "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.service"   || fail "Unexpected service user."
grep -Fq 'OnUnitActiveSec=15min' "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.timer"   || fail "Unexpected timer interval."

if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi

install -d -o root -g root -m 0755 "$APP_DIR"
install -o root -g root -m 0644 "$SOURCE_ROOT/scripts/ops/production_watch.py" "$APP_DIR/production_watch.py"
install -o root -g root -m 0644 "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.service" "$SERVICE"
install -o root -g root -m 0644 "$SOURCE_ROOT/templates/systemd/ebt-production-watch-vps.timer" "$TIMER"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$SERVICE" "$TIMER"
fi

systemctl daemon-reload
systemctl enable --now ebt-production-watch-vps.timer
systemctl is-enabled --quiet ebt-production-watch-vps.timer || fail "Timer is not enabled."
systemctl is-active --quiet ebt-production-watch-vps.timer || fail "Timer is not active."

set +e
systemctl start ebt-production-watch-vps.service
service_rc=$?
set -e

[[ -f "$STATE_DIR/report.json" ]] || fail "Monitor did not produce a report."
/usr/bin/python3 - "$STATE_DIR/report.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("origin") != "https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io":
    raise SystemExit("unexpected origin")
if data.get("notification") != "disabled":
    raise SystemExit("notification must remain disabled")
if data.get("scope") != "read_only_external_checks_not_full_production_acceptance":
    raise SystemExit("unexpected monitor scope")
if not isinstance(data.get("checks"), list) or not data["checks"]:
    raise SystemExit("missing checks")
print(json.dumps({
    "observed_at": data.get("observed_at"),
    "healthy_in_scope": data.get("healthy_in_scope"),
    "notification": data.get("notification"),
    "check_count": len(data["checks"]),
}, separators=(",", ":")))
PY

printf '\nINSTALLED: VPS product monitor timer is ACTIVE and ENABLED.\n'
printf 'Source SHA: %s\n' "$EXPECTED_SOURCE_SHA"
printf 'Initial service exit: %s (0=healthy in scope; non-zero can be a detected incident).\n' "$service_rc"
printf 'Timer: sudo systemctl list-timers --all ebt-production-watch-vps.timer --no-pager\n'
printf 'Logs: sudo journalctl -u ebt-production-watch-vps.service -n 50 --no-pager\n'
printf 'Report: sudo cat /var/lib/ebt-production-watch/report.json\n'
printf 'Stop only this monitor: sudo systemctl disable --now ebt-production-watch-vps.timer\n'
