#!/usr/bin/env bash
set -Eeuo pipefail

REPOSITORY="98erickgarcia-maker/ebt-platform"
PUBLIC_CLONE_URL="https://github.com/${REPOSITORY}.git"
SSH_REMOTE="git@github.com:${REPOSITORY}.git"
PROPOSAL_BRANCH="${PROPOSAL_BRANCH:-codex/flow-history-proposal-vps-20261009}"
SOURCE_ROOT="${SOURCE_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)}"
EXPECTED_SOURCE_SHA="${EXPECTED_SOURCE_SHA:-}"
EXPECTED_PROPOSAL_SHA="${EXPECTED_PROPOSAL_SHA:-}"
WORKSPACE="/var/lib/ebt-engineering/workspace"
STATE="/var/lib/ebt-engineering/state"
INSTALL_ROOT="/opt/ebt-engineering"
SERVICE_USER="ebt-scout"
GIT_KEY_PATH="${GIT_KEY_PATH:-/etc/ebt-engineering/controller_ed25519}"
KNOWN_HOSTS_PATH="${KNOWN_HOSTS_PATH:-/etc/ebt-engineering/known_hosts}"
SERVICE_PATH="/etc/systemd/system/ebt-engineering-runner.service"
RUNNER_TIMER_PATH="/etc/systemd/system/ebt-engineering-runner.timer"
WATCH_SERVICE_PATH="/etc/systemd/system/ebt-engineering-watch.service"
WATCH_TIMER_PATH="/etc/systemd/system/ebt-engineering-watch.timer"
CONTROLLER_ENV="/etc/ebt-engineering-controller.env"

fail(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need(){ command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"; }
root_private_file(){
  local path="$1"
  [[ "$path" = /* && -f "$path" && ! -L "$path" ]] || fail "Required root-only file missing or unsafe: $path"
  [[ "$(stat -c %u "$path")" == "0" ]] || fail "File must be owned by root: $path"
  local mode
  mode="$(stat -c %a "$path")"
  [[ "$mode" == "600" || "$mode" == "400" ]] || fail "File must be mode 0600 or 0400: $path"
}

[[ "$EUID" -eq 0 ]] || fail "Run with sudo/root."
for cmd in git python3 systemctl install stat find chown chmod; do need "$cmd"; done
id "$SERVICE_USER" >/dev/null 2>&1 || fail "User $SERVICE_USER does not exist."
[[ -d "$SOURCE_ROOT/.git" ]] || fail "SOURCE_ROOT must be a Git checkout."
[[ "$EXPECTED_SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]] || fail "Set EXPECTED_SOURCE_SHA to the reviewed PR SHA."
[[ "$EXPECTED_PROPOSAL_SHA" =~ ^[0-9a-f]{40}$ ]] || fail "Set EXPECTED_PROPOSAL_SHA to the approved proposal branch SHA."
actual_source="$(git -C "$SOURCE_ROOT" rev-parse HEAD)"
[[ "$actual_source" == "$EXPECTED_SOURCE_SHA" ]] || fail "SOURCE_ROOT SHA differs from EXPECTED_SOURCE_SHA."
[[ -z "$(git -C "$SOURCE_ROOT" status --porcelain --untracked-files=all)" ]] || fail "SOURCE_ROOT must be clean."
root_private_file "$GIT_KEY_PATH"
root_private_file "$KNOWN_HOSTS_PATH"
[[ -d /var/lib/ebt-scout/.codex ]] || fail "Codex profile /var/lib/ebt-scout/.codex is missing."

ENGINEERING_PATH="/opt/ebt-engineering/node/bin:/opt/ebt-engineering/dotnet:/usr/local/bin:/usr/bin:/bin"
env PATH="$ENGINEERING_PATH" bash -lc 'command -v codex >/dev/null && command -v dotnet >/dev/null && command -v npm >/dev/null' \
  || fail "codex, dotnet and npm must be available in the engineering service PATH."

install -d -o root -g root -m 0755 "$INSTALL_ROOT"
install -d -o root -g "$SERVICE_USER" -m 0750 /var/lib/ebt-engineering "$STATE"
install -d -o root -g "$SERVICE_USER" -m 0770 "$STATE/model-io"
install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0700 /var/lib/ebt-engineering/codex-profile

install -o root -g root -m 0644 "$SOURCE_ROOT/scripts/ops/engineering_runner.py" "$INSTALL_ROOT/engineering_runner.py"
install -o root -g root -m 0644 "$SOURCE_ROOT/scripts/ops/engineering_watch.py" "$INSTALL_ROOT/engineering_watch.py"
install -o root -g root -m 0644 "$SOURCE_ROOT/planejamento/engineering_blocks.json" "$INSTALL_ROOT/engineering_blocks.json"
install -o root -g root -m 0644 "$SOURCE_ROOT/templates/systemd/ebt-engineering-runner.service" "$SERVICE_PATH"
install -o root -g root -m 0644 "$SOURCE_ROOT/templates/systemd/ebt-engineering-runner.timer" "$RUNNER_TIMER_PATH"
install -o root -g root -m 0644 "$SOURCE_ROOT/templates/systemd/ebt-engineering-watch.service" "$WATCH_SERVICE_PATH"
install -o root -g root -m 0644 "$SOURCE_ROOT/templates/systemd/ebt-engineering-watch.timer" "$WATCH_TIMER_PATH"

cat > "$CONTROLLER_ENV" <<ENV
EBT_ENGINEERING_GIT_KEY=$GIT_KEY_PATH
EBT_ENGINEERING_KNOWN_HOSTS=$KNOWN_HOSTS_PATH
ENV
chown root:root "$CONTROLLER_ENV"
chmod 0600 "$CONTROLLER_ENV"

if [[ ! -d "$WORKSPACE/.git" ]]; then
  if [[ -e "$WORKSPACE" ]]; then
    [[ -z "$(find "$WORKSPACE" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] \
      || fail "Workspace exists and is not empty."
    rmdir "$WORKSPACE"
  fi
  git clone --branch "$PROPOSAL_BRANCH" --single-branch "$PUBLIC_CLONE_URL" "$WORKSPACE"
else
  [[ "$(git -C "$WORKSPACE" branch --show-current)" == "$PROPOSAL_BRANCH" ]] || fail "Workspace is on the wrong branch."
  [[ -z "$(git -C "$WORKSPACE" status --porcelain --untracked-files=all)" ]] || fail "Workspace is dirty."
fi

workspace_head="$(git -C "$WORKSPACE" rev-parse HEAD)"
[[ "$workspace_head" == "$EXPECTED_PROPOSAL_SHA" ]] || fail "Workspace proposal SHA differs from approved SHA."

git -C "$WORKSPACE" remote set-url origin "$SSH_REMOTE"
git -C "$WORKSPACE" remote set-url --push origin "$SSH_REMOTE"
git -C "$WORKSPACE" config user.name "EBT Engineering Controller"
git -C "$WORKSPACE" config user.email "ebt-engineering@users.noreply.github.com"

export GIT_SSH_COMMAND="/usr/bin/ssh -F /dev/null -i $GIT_KEY_PATH -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$KNOWN_HOSTS_PATH"
git -C "$WORKSPACE" fetch --prune origin "$PROPOSAL_BRANCH"
remote_proposal="$(git -C "$WORKSPACE" rev-parse "origin/$PROPOSAL_BRANCH")"
[[ "$remote_proposal" == "$EXPECTED_PROPOSAL_SHA" ]] || fail "Remote proposal branch moved during installation."
[[ "$(git -C "$WORKSPACE" rev-parse HEAD)" == "$EXPECTED_PROPOSAL_SHA" ]] || fail "Workspace changed before controller activation."
unset GIT_SSH_COMMAND

chown -R "$SERVICE_USER:$SERVICE_USER" "$WORKSPACE"
chown -R root:root "$WORKSPACE/.git"
chmod 0700 "$WORKSPACE/.git"
find "$WORKSPACE/.git" -mindepth 1 -type d -exec chmod go-w {} +
find "$WORKSPACE/.git" -type f -exec chmod go-w {} +

python3 - "$INSTALL_ROOT/engineering_blocks.json" "$PROPOSAL_BRANCH" <<'PY'
import json, pathlib, sys
path=pathlib.Path(sys.argv[1])
branch=sys.argv[2]
m=json.loads(path.read_text(encoding="utf-8"))
assert m.get("enabled") is True
assert m.get("concurrency") == 1
assert m.get("allow_push") is True
assert m.get("allow_deploy") is False
assert m.get("allow_migration") is False
assert m.get("allow_external_messages") is False
assert m.get("repository") == "98erickgarcia-maker/ebt-platform"
assert m.get("branch") == branch
print("manifest-ok")
PY

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$SERVICE_PATH" "$RUNNER_TIMER_PATH" "$WATCH_SERVICE_PATH" "$WATCH_TIMER_PATH"
fi

systemctl daemon-reload
systemctl enable --now ebt-engineering-runner.timer ebt-engineering-watch.timer

printf '\nInstalled native EBT controller at approved proposal SHA %s. No merge/deploy/migration is enabled.\n' "$EXPECTED_PROPOSAL_SHA"
systemctl list-timers ebt-engineering-runner.timer ebt-engineering-watch.timer --no-pager || true
printf '\nManual verified cycle: sudo systemctl start ebt-engineering-runner.service\n'
printf 'Logs: sudo journalctl -u ebt-engineering-runner.service -n 100 --no-pager\n'
