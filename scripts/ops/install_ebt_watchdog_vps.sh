#!/usr/bin/env bash
# Install only EBT's read-only GitHub Actions watchdog on a dedicated Linux VPS.
# It does not deploy any application, send messages, change SQL, or restart services.
set -Eeuo pipefail
umask 077

REPO='98erickgarcia-maker/ebt-platform'
SOURCE_SHA='56a659ac1fc7597f7e453bd7e39042742e8f408e'
RAW="https://raw.githubusercontent.com/$REPO/$SOURCE_SHA"
APP_DIR='/opt/ebt-watchdog'
SERVICE='/etc/systemd/system/ebt-schedule-watchdog.service'
TIMER='/etc/systemd/system/ebt-schedule-watchdog.timer'

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ "$EUID" -eq 0 ]] || fail 'Execute como root (sudo bash ebt_install_watchdog_vps.sh).'
[[ -d /run/systemd/system ]] || fail 'systemd nao esta em execucao nesta VPS.'
for binary in curl python3 systemctl install mktemp sed useradd id; do
    command -v "$binary" >/dev/null 2>&1 || fail "Programa ausente: $binary"
done
[[ -x /usr/bin/python3 ]] || fail 'Python3 ausente em /usr/bin/python3; nao alterar a instalacao existente.'
[[ ! -L "$APP_DIR" ]] || fail "$APP_DIR e um link simbolico; revise manualmente."
[[ ! -e "$APP_DIR" || -d "$APP_DIR" ]] || fail "$APP_DIR nao e um diretorio."
[[ ! -e "$SERVICE" || -f "$SERVICE" ]] || fail 'Unit de servico nao e arquivo regular.'
[[ ! -e "$TIMER" || -f "$TIMER" ]] || fail 'Unit de timer nao e arquivo regular.'
if [[ -e "$SERVICE" ]] && ! grep -Fq "$APP_DIR/schedule_watchdog.py" "$SERVICE"; then
    fail "Ja existe servico com mesmo nome em outro diretorio: $SERVICE"
fi

STAGING="$(mktemp -d)"
trap 'rm -rf -- "$STAGING"' EXIT
fetch() {
    local path="$1" destination="$2"
    curl --fail --silent --show-error --location --retry 2 --max-time 30 \
         --proto '=https' --proto-redir '=https' "$RAW/$path" -o "$destination"
}
fetch 'scripts/ops/schedule_watchdog.py' "$STAGING/schedule_watchdog.py"
fetch 'templates/systemd/ebt-schedule-watchdog.service' "$STAGING/service.orig"
fetch 'templates/systemd/ebt-schedule-watchdog.timer' "$STAGING/timer"
/usr/bin/python3 -m py_compile "$STAGING/schedule_watchdog.py"
grep -Fq 'StateDirectory=ebt-watch' "$STAGING/service.orig" || fail 'Unit inesperada (StateDirectory).'
grep -Fq 'OnUnitActiveSec=5min' "$STAGING/timer" || fail 'Timer inesperado (intervalo).'
grep -Fq 'NoNewPrivileges=true' "$STAGING/service.orig" || fail 'Unit inesperada (seguranca).'
sed -e 's@/opt/ebt-platform/scripts/ops/schedule_watchdog.py@/opt/ebt-watchdog/schedule_watchdog.py@g' \
    -e 's@WorkingDirectory=/opt/ebt-platform@WorkingDirectory=/opt/ebt-watchdog@g' \
    -e '/^EnvironmentFile=-\/etc\/ebt-watch.env$/d' \
    "$STAGING/service.orig" > "$STAGING/service"
grep -Fq "ExecStart=/usr/bin/python3 $APP_DIR/schedule_watchdog.py" "$STAGING/service" || fail 'Unit nao aponta para o watchdog isolado.'

if ! id -u ebt-watch >/dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin ebt-watch
fi
install -d -o root -g root -m 0755 "$APP_DIR"
install -o root -g root -m 0644 "$STAGING/schedule_watchdog.py" "$APP_DIR/schedule_watchdog.py"
install -o root -g root -m 0644 "$STAGING/service" "$SERVICE"
install -o root -g root -m 0644 "$STAGING/timer" "$TIMER"
systemctl daemon-reload
systemctl enable --now ebt-schedule-watchdog.timer
systemctl is-active --quiet ebt-schedule-watchdog.timer || fail 'Timer nao ficou ativo.'
systemctl is-enabled --quiet ebt-schedule-watchdog.timer || fail 'Timer nao ficou habilitado no boot.'
printf '\nINSTALLED: EBT watchdog timer is ACTIVE and ENABLED.\n'
printf 'Pinned GitHub source: %s\n' "$SOURCE_SHA"
printf 'Runs every five minutes; only GitHub GET and local journal/state.\n'
printf 'Recent state: sudo systemctl list-timers --all ebt-schedule-watchdog.timer\n'
printf 'Log: sudo journalctl -u ebt-schedule-watchdog.service -n 30 --no-pager\n'
printf 'Stop only watchdog: sudo systemctl disable --now ebt-schedule-watchdog.timer\n'
printf 'A FAIL result for an overdue GitHub schedule is an expected alert, not an installation failure.\n'
