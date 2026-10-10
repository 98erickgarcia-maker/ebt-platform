#!/usr/bin/env bash
set -Eeuo pipefail

FETCH_REPOSITORY_URL="${FETCH_REPOSITORY_URL:-https://github.com/98erickgarcia-maker/ebt-platform.git}"
PUSH_REPOSITORY_URL="${PUSH_REPOSITORY_URL:-git@github.com:98erickgarcia-maker/ebt-platform.git}"
REPO_DIR="${REPO_DIR:-/opt/ebt/ebt-platform}"
BASE_BRANCH="${BASE_BRANCH:-codex/enterprise-blocks-15min-20261009}"
PROPOSAL_BRANCH="${PROPOSAL_BRANCH:-codex/flow-history-proposal-vps-20261009}"
STATE_DIR="${STATE_DIR:-/var/lib/ebt-engineering}"
SERVICE_USER="${SERVICE_USER:-ebt-scout}"
AUTO_PUSH_PROPOSAL="${AUTO_PUSH_PROPOSAL:-1}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

[[ "${EUID}" -eq 0 ]] || { echo "Run this installer as root (sudo)." >&2; exit 1; }
command -v systemctl >/dev/null || { echo "systemd/systemctl is required." >&2; exit 1; }
command -v git >/dev/null || { echo "git is required." >&2; exit 1; }
id "$SERVICE_USER" >/dev/null 2>&1 || { echo "Required service user '$SERVICE_USER' does not exist." >&2; exit 1; }
[[ "$AUTO_PUSH_PROPOSAL" == "0" || "$AUTO_PUSH_PROPOSAL" == "1" ]] || { echo "AUTO_PUSH_PROPOSAL must be 0 or 1." >&2; exit 1; }

install -d -m 0755 /etc/ebt /opt/ebt
install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0750 "$STATE_DIR"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0755 "$(dirname "$REPO_DIR")"
  runuser -u "$SERVICE_USER" -- git clone "$FETCH_REPOSITORY_URL" "$REPO_DIR"
fi

runuser -u "$SERVICE_USER" -- test -r "$REPO_DIR/.git" || { echo "$SERVICE_USER cannot read $REPO_DIR/.git" >&2; exit 1; }
runuser -u "$SERVICE_USER" -- test -w "$REPO_DIR" || { echo "$SERVICE_USER cannot write $REPO_DIR. Fix ownership/ACL explicitly." >&2; exit 1; }

runuser -u "$SERVICE_USER" -- git -C "$REPO_DIR" remote set-url --push origin "$PUSH_REPOSITORY_URL"

install -m 0755 "$SCRIPT_DIR/ebt_engineering_auto.sh" /usr/local/sbin/ebt-engineering-auto
install -m 0644 "$SCRIPT_DIR/../../deployment/systemd/ebt-engineering-auto.service" /etc/systemd/system/ebt-engineering-auto.service
install -m 0644 "$SCRIPT_DIR/../../deployment/systemd/ebt-engineering-auto.timer" /etc/systemd/system/ebt-engineering-auto.timer

cat > /etc/ebt/engineering-auto.env <<ENV
REPO_DIR=$REPO_DIR
REMOTE=origin
BASE_BRANCH=$BASE_BRANCH
PROPOSAL_BRANCH=$PROPOSAL_BRANCH
STATE_DIR=$STATE_DIR
MANIFEST_REL=planejamento/engineering_blocks.json
RUNNER_REL=scripts/ops/engineering_runner.py
WATCH_REL=scripts/ops/engineering_watch.py
AUTO_PUSH_PROPOSAL=$AUTO_PUSH_PROPOSAL
ENV
chmod 0640 /etc/ebt/engineering-auto.env
chown root:"$SERVICE_USER" /etc/ebt/engineering-auto.env

runuser -u "$SERVICE_USER" -- env \
  REPO_DIR="$REPO_DIR" REMOTE=origin BASE_BRANCH="$BASE_BRANCH" PROPOSAL_BRANCH="$PROPOSAL_BRANCH" \
  STATE_DIR="$STATE_DIR" MANIFEST_REL=planejamento/engineering_blocks.json \
  RUNNER_REL=scripts/ops/engineering_runner.py WATCH_REL=scripts/ops/engineering_watch.py \
  AUTO_PUSH_PROPOSAL="$AUTO_PUSH_PROPOSAL" \
  /usr/local/sbin/ebt-engineering-auto --dry-run

systemctl daemon-reload
systemctl enable --now ebt-engineering-auto.timer

echo
echo "Installed. Timer status:"
systemctl status ebt-engineering-auto.timer --no-pager || true
echo
echo "Automatic proposal push: $AUTO_PUSH_PROPOSAL"
echo "Push URL: $(runuser -u "$SERVICE_USER" -- git -C "$REPO_DIR" remote get-url --push origin)"
echo
echo "Useful commands:"
echo "  systemctl list-timers ebt-engineering-auto.timer --no-pager"
echo "  journalctl -u ebt-engineering-auto.service -n 100 --no-pager"
echo "  systemctl start ebt-engineering-auto.service"
echo "  systemctl stop ebt-engineering-auto.timer"
