@echo off
setlocal
REM Windows/WSL convenience launcher. Real automation is Linux systemd + Bash.
wsl.exe -e bash -lc "sudo systemctl start ebt-engineering-auto.service; sudo systemctl status ebt-engineering-auto.service --no-pager; echo --- TIMER ---; sudo systemctl status ebt-engineering-auto.timer --no-pager; echo --- LAST LOGS ---; sudo journalctl -u ebt-engineering-auto.service -n 40 --no-pager"
endlocal
