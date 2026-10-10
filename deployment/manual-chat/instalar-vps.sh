#!/bin/sh
# Run from the extracted package root on the existing EBT VPS. No credentials copied.
set -eu
if [ "$(id -u)" -ne 0 ]; then
    echo 'Execute como root na VPS EBT existente.' >&2
    exit 1
fi
for required in /opt/ebt-engineering/engineering_blocks.json /var/lib/ebt-engineering/state/checkpoint.json /opt/ebt-engineering/node/bin/node /var/lib/ebt-linux-chat-chrome; do
    if [ ! -e "$required" ]; then
        echo 'Pre-requisito da VPS EBT ausente; nenhuma credencial sera criada ou copiada.' >&2
        exit 1
    fi
done
test -f scripts/ops/manual_chat.py
test -f deployment/linux-chat/compose.yaml
stamp=$(date +%Y%m%d%H%M%S)
install -d -m 755 /opt/ebt-engineering/manual-chat/web /opt/ebt-engineering/linux-chat/supervisor
copy_reviewed() {
    source_file=$1
    target_file=$2
    file_mode=$3
    if [ -f "$target_file" ]; then
        cp -p "$target_file" "$target_file.before-manual-$stamp"
    fi
    install -m "$file_mode" "$source_file" "$target_file"
}
docker compose -f /opt/ebt-engineering/linux-chat/compose.yaml stop browser
python3 deployment/manual-chat/recover_profile.py
copy_reviewed scripts/ops/manual_chat.py /opt/ebt-engineering/manual-chat/manual_chat.py 644
copy_reviewed scripts/ops/insert_chat.mjs /opt/ebt-engineering/manual-chat/insert_chat.mjs 644
copy_reviewed scripts/ops/continue_chat.py /opt/ebt-engineering/manual-chat/continue_chat.py 644
copy_reviewed deployment/manual-chat/ebt-chat-continue.service /etc/systemd/system/ebt-chat-continue.service 644
copy_reviewed deployment/manual-chat/ebt-chat-continue.timer /etc/systemd/system/ebt-chat-continue.timer 644
copy_reviewed deployment/manual-chat/web/index.html /opt/ebt-engineering/manual-chat/web/index.html 644
copy_reviewed deployment/manual-chat/web/app.js /opt/ebt-engineering/manual-chat/web/app.js 644
copy_reviewed deployment/manual-chat/ebt-manual-chat.service /etc/systemd/system/ebt-manual-chat.service 644
copy_reviewed deployment/linux-chat/compose.yaml /opt/ebt-engineering/linux-chat/compose.yaml 644
copy_reviewed deployment/linux-chat/launch-chrome.sh /opt/ebt-engineering/linux-chat/launch-chrome.sh 755
copy_reviewed deployment/linux-chat/supervisor/desktop.conf /opt/ebt-engineering/linux-chat/supervisor/desktop.conf 644
docker compose -f /opt/ebt-engineering/linux-chat/compose.yaml config --quiet
docker compose -f /opt/ebt-engineering/linux-chat/compose.yaml up -d --wait --wait-timeout 60
systemctl daemon-reload
systemctl enable --now ebt-manual-chat.service
curl -fsS http://127.0.0.1:5810/healthz
echo '\nPainel instalado. Abra o tunel privado e revise o teste antes de aprovar.'
echo 'O timer CONTINUE nao e ativado por este instalador: exige destino privado e autorizacao explicita.'
