# Automação Linux do EBT Flow

Data de referência: 10/10/2026.

## Objetivo

Executar a fila `FLOW-01..FLOW-10` em uma VPS Linux por ciclos de 15 minutos usando o runner existente, sem autorizar merge, deploy, migration, mensagens externas ou force-push.

## Componentes

- `scripts/ops/ebt_engineering_auto.sh`: ciclo seguro, lock, sincronização fast-forward, execução do runner, commit verificado e push somente da branch de proposta.
- `scripts/ops/install_ebt_engineering_auto.sh`: instalador systemd.
- `deployment/systemd/ebt-engineering-auto.service`: serviço oneshot.
- `deployment/systemd/ebt-engineering-auto.timer`: agenda em 00/15/30/45 minutos.
- `scripts/ops/EBT_AUTO_LINUX.bat`: atalho opcional para iniciar/consultar o serviço via WSL.

## Branch e fronteira de segurança

A automação trabalha somente em `codex/flow-history-proposal-vps-20261009`. A branch base configurada é `codex/enterprise-blocks-15min-20261009`.

O wrapper mantém `allow_push=false` no runner. Depois de `task_verified`, ele valida os caminhos modificados contra `allowed_paths`, executa `git diff --check`, cria commit e salva `pending-push.json` antes da tentativa de rede. O push é não-forçado e aponta exclusivamente para a branch de proposta.

Se o push falhar, a próxima rodada tenta primeiro sincronizar o mesmo SHA. Se o remoto mudou, o ciclo bloqueia; não há reset, rebase automático, force-push ou sobrescrita.

## Instalação

O usuário de serviço esperado é `ebt-scout`. Ele precisa ter o login do Codex exigido pelo runner, escrita no worktree e uma credencial SSH GitHub com escrita adequada ao repositório. Chaves privadas não pertencem ao repositório.

```bash
chmod +x scripts/ops/ebt_engineering_auto.sh scripts/ops/install_ebt_engineering_auto.sh
sudo scripts/ops/install_ebt_engineering_auto.sh
```

Para desativar push automático da proposta:

```bash
AUTO_PUSH_PROPOSAL=0 sudo scripts/ops/install_ebt_engineering_auto.sh
```

## Operação

```bash
systemctl list-timers ebt-engineering-auto.timer --no-pager
journalctl -u ebt-engineering-auto.service -n 100 --no-pager
sudo systemctl start ebt-engineering-auto.service
sudo systemctl disable --now ebt-engineering-auto.timer
```

## Estados

`task_verified` permite empacotar e sincronizar somente a tarefa verificada. `proposal_review_ready` indica fim da fila de proposta; não significa release-ready. Release continua dependendo de CI do SHA exato e das evidências SQL/browser exigidas pelo risco.

## Evidência de teste do wrapper

Antes de adicionar estes arquivos ao repositório, o wrapper foi exercitado com repositório Git remoto sintético: criação da branch de proposta, commit de tarefa verificada, push/readback do SHA e recuperação de push interrompido por checkpoint. Isso não comprova instalação na VPS real nem credenciais do host.
