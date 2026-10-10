@echo off
title EBT - acesso privado ao painel manual
echo Mantenha esta janela aberta enquanto utilizar o painel.
echo Se as portas ja estiverem ocupadas, confira se o painel existente esta acessivel.
start "" "http://127.0.0.1:5810/"
ssh -NT -L 127.0.0.1:5810:127.0.0.1:5810 -L 127.0.0.1:5801:127.0.0.1:5800 -o ExitOnForwardFailure=yes -o ServerAliveInterval=10 -o ServerAliveCountMax=6 root@177.153.38.72
echo.
echo Tunel encerrado. A sessao do Chrome fica preservada na VPS.
pause
