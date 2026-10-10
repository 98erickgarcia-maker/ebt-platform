#!/usr/bin/env bash
set -Eeuo pipefail

[[ "$EUID" -eq 0 ]] || { echo "Run with sudo/root." >&2; exit 1; }

for unit in   ebt-engineering-runner.timer   ebt-engineering-watch.timer   ebt-schedule-watchdog.timer   ebt-production-watch-vps.timer; do
  systemctl disable --now "$unit" || true
done

echo "EBT automation timers disabled."
echo "No application service, database, Git branch or installed evidence file was deleted."
