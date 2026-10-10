# Retomar sem comprar creditos

A VPS usa a cota incluida na conta existente. Nenhuma compra ou recarga automatica foi ativada. O limite continua aplicavel: o monitor nao cria capacidade de IA.

Os timers ebt-engineering-runner.timer e ebt-engineering-watch.timer estao habilitados. O supervisor observa a cada15min, sem chamada IA. O runner preserva tarefa/checkpoint e tenta novamente apos cooldown de6h; nova falta de cota gera nova espera. Dez papeis sao sequenciais, nao dez processos permanentes.

Para ver o estado:
```powershell
ssh root@177.153.38.72 "cat /var/lib/ebt-engineering/state/heartbeat.json; systemctl list-timers --all ebt-engineering* --no-pager"
```

Para verificar manualmente, sem apagar estado nem contornar cooldown:
```powershell
ssh root@177.153.38.72 "systemctl start ebt-engineering-watch.service; systemctl start ebt-engineering-runner.service"
```

O watcher retorna codigo2 quando observa bloqueio; isso nao significa erro interno. Quando a cota voltar, o runner retoma FLOW-01, exige dependencias/caminhos/testes e confirma SHA remoto na branch de proposta. Nao faz merge/deploy automatico. Falha de testes ou seguranca exige correcao revisada; nao reiniciar infinitamente nem apagar checkpoint.

Os dez Chats normais estao no indice local tmp/release/CHATS_NORMAIS_EBT.md. Revisoes desses chats precisam ser integradas e verificadas pelo coordenador; abrir conversa nao comprova execucao na VPS.

Custos: sem novos creditos/API pagos; VPS e hospedagem existentes continuam sujeitos aos seus contratos. Desenvolvimento continuo sem limites nao e garantido pela cota incluida.
