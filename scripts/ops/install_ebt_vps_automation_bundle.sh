#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

REPOSITORY="98erickgarcia-maker/ebt-platform"
PUBLIC_REPO="https://github.com/${REPOSITORY}.git"

FLOW_SOURCE_BRANCH="codex/enterprise-blocks-15min-20261009"
FLOW_SOURCE_SHA="9dc3b5ff647aa2453e18cc3148f13d1364145741"
FLOW_PROPOSAL_BRANCH="codex/flow-history-proposal-vps-20261009"
FLOW_PROPOSAL_SHA="0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0"

WATCHDOG_BRANCH="ops/ebt-watchdog-vps-bootstrap-20261009"
WATCHDOG_HEAD_SHA="e6a112f4db0d0bec02f623c968c579116b7dfe9c"
WATCHDOG_SOURCE_SHA="56a659ac1fc7597f7e453bd7e39042742e8f408e"

PRODUCT_BRANCH="ops/ebt-production-watch-vps-20261010"
PRODUCT_SHA="3820d0edd5126ae416ea569b3dc30b5b0ce1a215"

GIT_KEY_PATH="${GIT_KEY_PATH:-/etc/ebt-engineering/controller_ed25519}"
KNOWN_HOSTS_PATH="${KNOWN_HOSTS_PATH:-/etc/ebt-engineering/known_hosts}"
BUNDLE_ROOT="${BUNDLE_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)}"
EXPECTED_BUNDLE_SHA="${EXPECTED_BUNDLE_SHA:-}"
HELPER_DIR="/opt/ebt-vps-automation"
STATUS_COMMAND="/usr/local/sbin/ebt-vps-automation-status"
DISABLE_COMMAND="/usr/local/sbin/ebt-vps-automation-disable"
CHECK_ONLY=0
INSTALL_STARTED=0
TARGET_TIMERS=(
  ebt-schedule-watchdog.timer
  ebt-production-watch-vps.timer
  ebt-engineering-runner.timer
  ebt-engineering-watch.timer
)

if [[ "${1:-}" == "--check-only" ]]; then
  CHECK_ONLY=1
elif [[ $# -gt 0 ]]; then
  printf 'ERROR: unknown argument: %s\n' "$1" >&2
  exit 2
fi

fail(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need(){ command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"; }

root_private_file(){
  local path="$1"
  [[ "$path" = /* && -f "$path" && ! -L "$path" ]] || fail "Missing or unsafe root-only file: $path"
  [[ "$(stat -c %u "$path")" == "0" ]] || fail "File must be owned by root: $path"
  local mode
  mode="$(stat -c %a "$path")"
  [[ "$mode" == "600" || "$mode" == "400" ]] || fail "File must be mode 0600 or 0400: $path"
}

[[ "$EUID" -eq 0 ]] || fail "Run with sudo/root."
[[ -d /run/systemd/system ]] || fail "systemd is not running on this host."
for binary in git bash python3 systemctl stat mktemp grep id runuser install; do need "$binary"; done
[[ -d "$BUNDLE_ROOT/.git" ]] || fail "BUNDLE_ROOT must be a Git checkout."
[[ "$EXPECTED_BUNDLE_SHA" =~ ^[0-9a-f]{40}$ ]] || fail "Set EXPECTED_BUNDLE_SHA to the reviewed bootstrap SHA."
bundle_head="$(git -C "$BUNDLE_ROOT" rev-parse HEAD)"
[[ "$bundle_head" == "$EXPECTED_BUNDLE_SHA" ]] || fail "Bootstrap checkout SHA differs from EXPECTED_BUNDLE_SHA."
[[ -z "$(GIT_OPTIONAL_LOCKS=0 git -C "$BUNDLE_ROOT" status --porcelain --untracked-files=all)" ]] || fail "Bootstrap checkout must be clean."
id ebt-scout >/dev/null 2>&1 || fail "Required user ebt-scout is missing."
[[ -d /var/lib/ebt-scout/.codex ]] || fail "Codex profile /var/lib/ebt-scout/.codex is missing."
root_private_file "$GIT_KEY_PATH"
root_private_file "$KNOWN_HOSTS_PATH"

STAGING="$(mktemp -d /var/tmp/ebt-vps-bootstrap.XXXXXX)"
on_exit(){
  local rc=$?
  trap - EXIT
  if (( rc != 0 && INSTALL_STARTED == 1 )); then
    printf 'Installation failed; disabling EBT automation timers from this clean-host bootstrap.\n' >&2
    for unit in "${TARGET_TIMERS[@]}"; do
      systemctl disable --now "$unit" >/dev/null 2>&1 || true
    done
  fi
  rm -rf -- "$STAGING"
  exit "$rc"
}
trap on_exit EXIT

for unit in "${TARGET_TIMERS[@]}"; do
  if systemctl is-enabled --quiet "$unit" 2>/dev/null || systemctl is-active --quiet "$unit" 2>/dev/null; then
    fail "$unit already active/enabled; use the individual diagnostic/recovery path instead of clean-host bootstrap."
  fi
done

clone_pinned(){
  local name="$1" branch="$2" sha="$3"
  local destination="$STAGING/$name"
  git -c core.hooksPath=/dev/null clone --quiet --depth 1 --no-tags --single-branch --branch "$branch" "$PUBLIC_REPO" "$destination"
  local actual
  actual="$(git -C "$destination" rev-parse HEAD)"
  [[ "$actual" == "$sha" ]] || fail "$name branch moved: expected $sha, got $actual"
  [[ -z "$(git -C "$destination" status --porcelain --untracked-files=all)" ]] || fail "$name source checkout is dirty"
  printf '%s\n' "$destination"
}

printf 'Preparing pinned sources...\n'
FLOW_SOURCE="$(clone_pinned flow "$FLOW_SOURCE_BRANCH" "$FLOW_SOURCE_SHA")"
WATCHDOG_SOURCE="$(clone_pinned watchdog "$WATCHDOG_BRANCH" "$WATCHDOG_HEAD_SHA")"
PRODUCT_SOURCE="$(clone_pinned product "$PRODUCT_BRANCH" "$PRODUCT_SHA")"

python3 - "$FLOW_SOURCE/planejamento/engineering_blocks.json" "$FLOW_PROPOSAL_BRANCH" <<'PY'
import json, pathlib, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
proposal = sys.argv[2]
assert manifest.get("enabled") is True
assert manifest.get("concurrency") == 1
assert manifest.get("allow_push") is True
assert manifest.get("allow_deploy") is False
assert manifest.get("allow_migration") is False
assert manifest.get("allow_external_messages") is False
assert manifest.get("repository") == "98erickgarcia-maker/ebt-platform"
assert manifest.get("branch") == proposal
print("flow-manifest-ok")
PY

grep -Fq "SOURCE_SHA='$WATCHDOG_SOURCE_SHA'" "$WATCHDOG_SOURCE/scripts/ops/install_ebt_watchdog_vps.sh"   || fail "Watchdog installer source pin differs from reviewed source."
grep -Fq 'Environment=EBT_NOTIFY=false' "$PRODUCT_SOURCE/templates/systemd/ebt-production-watch-vps.service"   || fail "Product monitor notifications are not disabled."
grep -Fq 'OnUnitActiveSec=15min' "$PRODUCT_SOURCE/templates/systemd/ebt-production-watch-vps.timer"   || fail "Product monitor timer interval is unexpected."
grep -Fq 'OnUnitInactiveSec=15min' "$FLOW_SOURCE/templates/systemd/ebt-engineering-runner.timer"   || fail "Flow runner timer interval is unexpected."

git ls-remote --exit-code "$PUBLIC_REPO" "refs/heads/$FLOW_PROPOSAL_BRANCH" >/dev/null   || fail "Remote Flow proposal branch is missing."
proposal_remote="$(git ls-remote "$PUBLIC_REPO" "refs/heads/$FLOW_PROPOSAL_BRANCH" | awk 'NR==1 {print $1}')"
[[ "$proposal_remote" == "$FLOW_PROPOSAL_SHA" ]]   || fail "Remote Flow proposal branch moved: expected $FLOW_PROPOSAL_SHA, got $proposal_remote"

printf 'PRECHECK_OK flow_source=%s flow_proposal=%s watchdog=%s product=%s\n'   "$FLOW_SOURCE_SHA" "$proposal_remote" "$WATCHDOG_HEAD_SHA" "$PRODUCT_SHA"

if (( CHECK_ONLY == 1 )); then
  printf 'CHECK_ONLY: no systemd unit was installed or enabled.\n'
  exit 0
fi

INSTALL_STARTED=1

printf '\n1/3 Installing read-only GitHub schedule watchdog...\n'
bash "$WATCHDOG_SOURCE/scripts/ops/install_ebt_watchdog_vps.sh"

printf 'Forcing one read-only watchdog observation for deterministic evidence...\n'
set +e
systemctl start ebt-schedule-watchdog.service
watchdog_probe_rc=$?
set -e
if [[ "$watchdog_probe_rc" -ne 0 && "$watchdog_probe_rc" -ne 2 ]]; then
  fail "Watchdog probe returned unexpected exit code: $watchdog_probe_rc"
fi
[[ -s /var/lib/ebt-watch/state.json ]] || fail "Watchdog did not persist its first observation."
printf 'Watchdog observation persisted (exit=%s; 2 means detected incident).\n' "$watchdog_probe_rc"

printf '\n2/3 Installing direct read-only EBT product monitor...\n'
SOURCE_ROOT="$PRODUCT_SOURCE" EXPECTED_SOURCE_SHA="$PRODUCT_SHA"   bash "$PRODUCT_SOURCE/scripts/ops/install_ebt_production_watch_vps.sh"

printf '\n3/3 Installing Flow engineering controller last...\n'
SOURCE_ROOT="$FLOW_SOURCE" EXPECTED_SOURCE_SHA="$FLOW_SOURCE_SHA"   EXPECTED_PROPOSAL_SHA="$FLOW_PROPOSAL_SHA"   GIT_KEY_PATH="$GIT_KEY_PATH" KNOWN_HOSTS_PATH="$KNOWN_HOSTS_PATH"   bash "$FLOW_SOURCE/scripts/ops/install_ebt_engineering_auto.sh"

for unit in "${TARGET_TIMERS[@]}"; do
  systemctl is-enabled --quiet "$unit" || fail "$unit is not enabled"
  systemctl is-active --quiet "$unit" || fail "$unit is not active"
done

printf '\nInstalling stable local status/rollback helpers...\n'
install -d -o root -g root -m 0755 "$HELPER_DIR"
install -o root -g root -m 0644 "$BUNDLE_ROOT/scripts/ops/vps_automation_status.py" "$HELPER_DIR/vps_automation_status.py"
cat > "$STATUS_COMMAND" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
exec python3 /opt/ebt-vps-automation/vps_automation_status.py
SH
chmod 0755 "$STATUS_COMMAND"
install -o root -g root -m 0755 "$BUNDLE_ROOT/scripts/ops/disable_ebt_vps_automation.sh" "$DISABLE_COMMAND"

printf '\nFinal sanitized activation integrity check...\n'
"$STATUS_COMMAND"

INSTALL_STARTED=0

printf '\nAUTOMATION_BUNDLE_INSTALLED\n'
printf 'All four timers are enabled and active.\n'
printf 'No merge, product deploy, SQL migration or force-push was performed by this bootstrap.\n'
printf 'Status: sudo ebt-vps-automation-status\n'
printf 'Rollback timers only: sudo ebt-vps-automation-disable\n'
