# Automação Linux do EBT Flow

Data de referência: 10/10/2026.

## Objetivo

Executar a fila `FLOW-01..FLOW-10` em uma VPS Linux a cada 15 minutos com um único controlador verificável. O agente não recebe credencial Git e não pode fazer commit/push diretamente. Merge, deploy, migration e mensagens externas continuam proibidos.

## Arquitetura escolhida

A automação usa o mecanismo nativo de `scripts/ops/engineering_runner.py`.

- O serviço `ebt-engineering-runner.service` roda como `root` somente para proteger metadados Git, checkpoint e transporte.
- Toda invocação Codex e os checks `dotnet/npm` são rebaixados pelo runner para o usuário sem privilégio `ebt-scout`.
- A chave SSH e o `known_hosts` ficam em arquivos root-only e seus caminhos chegam ao controlador por `/etc/ebt-engineering-controller.env`.
- O ambiente passado ao agente não contém `EBT_ENGINEERING_GIT_KEY` nem credenciais de banco/cloud.
- Depois dos checks, o próprio controlador cria o commit e sincroniza somente `codex/flow-history-proposal-vps-20261009`.
- O push é normal, nunca `--force`. Falha de rede deixa o checkpoint em `awaiting_sync`; o mesmo commit é tentado novamente antes de qualquer novo agente.
- `proposal_review_ready` encerra a fila de proposta. Não autoriza merge, release ou deploy.

Isso substitui a ideia anterior de um segundo wrapper com credencial Git no usuário do agente.

## Pré-requisitos

1. Usuário Linux `ebt-scout` existente e perfil Codex em `/var/lib/ebt-scout/.codex`.
2. `codex`, `dotnet` e `npm` disponíveis no PATH definido pelo service.
3. Chave SSH com escrita somente neste repositório e `known_hosts` já verificado. O instalador não gera, copia nem imprime segredo.
4. Branch remota `codex/flow-history-proposal-vps-20261009` criada a partir de um SHA de CI aprovado.
5. Checkout fonte limpo no SHA revisado, informado em `EXPECTED_SOURCE_SHA`.

## Instalação

Exemplo, substituindo o SHA pelo candidato realmente aprovado:

```bash
sudo install -d -m 0700 /etc/ebt-engineering
sudo install -o root -g root -m 0600 /caminho/seguro/chave_ed25519 /etc/ebt-engineering/controller_ed25519
sudo install -o root -g root -m 0600 /caminho/seguro/known_hosts /etc/ebt-engineering/known_hosts

sudo EXPECTED_SOURCE_SHA=<sha-aprovado> \
  GIT_KEY_PATH=/etc/ebt-engineering/controller_ed25519 \
  KNOWN_HOSTS_PATH=/etc/ebt-engineering/known_hosts \
  scripts/ops/install_ebt_engineering_auto.sh
```

O script valida o SHA da fonte do instalador e, separadamente, o SHA exato da branch/workspace de proposta. Após o fetch autenticado ele lê novamente `origin/<proposal>` e aborta se o remoto tiver mudado antes do `systemctl enable`. Também valida checkout limpo, permissões dos arquivos de transporte, manifesto, binários e unidades systemd.

## Operação

```bash
systemctl list-timers ebt-engineering-runner.timer ebt-engineering-watch.timer --no-pager
sudo systemctl start ebt-engineering-runner.service
sudo journalctl -u ebt-engineering-runner.service -n 100 --no-pager
sudo systemctl disable --now ebt-engineering-runner.timer ebt-engineering-watch.timer
```

O atalho `scripts/ops/EBT_AUTO_LINUX.bat` apenas aciona/consulta essas unidades via WSL; a automação real é Linux/systemd.

## Limites de segurança

O controlador só aceita o repositório `98erickgarcia-maker/ebt-platform` e a branch de proposta fixada no código/manifesto. Alteração de remote, branch, `.git`, SHA durante a tarefa, arquivo fora da allowlist, segredo aparente, check falho ou divergência de evidência interrompe a fila.

Nenhuma dessas provas representa release. CI no SHA composto, SQL/browser quando exigidos, rollback e aceite operacional continuam gates separados.


## Ativação diferida

Para um bootstrap coordenado, o instalador aceita `EBT_DEFER_TIMER_START=1`. Nesse modo ele instala e valida o controlador, workspace, chave, units e manifesto, mas deixa `ebt-engineering-runner.timer` e `ebt-engineering-watch.timer` desabilitados/inativos.

O timer do runner usa `OnActiveSec=2min` em vez de `OnBootSec`. Assim a primeira execução é contada a partir da ativação do timer, evitando disparo imediato em uma VPS que já está ligada há mais de dois minutos.

O bundle da VPS deve:
1. instalar o Flow com timers diferidos;
2. instalar helpers/status;
3. validar integridade pré-ativação;
4. habilitar os timers Flow;
5. executar o veredito final.
