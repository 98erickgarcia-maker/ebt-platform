@echo off
setlocal
REM Convenience launcher for a Linux/WSL host provisioned with the native EBT engineering controller.
wsl.exe -e bash -lc "sudo systemctl start ebt-engineering-runner.service; sudo systemctl status ebt-engineering-runner.service --no-pager; echo --- RUNNER TIMER ---; sudo systemctl status ebt-engineering-runner.timer --no-pager; echo --- WATCH TIMER ---; sudo systemctl status ebt-engineering-watch.timer --no-pager; echo --- LAST LOGS ---; sudo journalctl -u ebt-engineering-runner.service -n 60 --no-pager"
endlocal
