# Bootstrap único das automações Linux da EBT

O bootstrap `scripts/ops/install_ebt_vps_automation_bundle.sh` reduz a ativação operacional a um único fluxo reproduzível sem incorporar segredos ao repositório.

## Fontes imutáveis

O script exige e confere:
- Flow/controller source: `532a3301c6de60f99d431e1f9d4f8294bf0ab8b5`;
- Flow proposal initial SHA: `0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0`;
- watchdog do cron: head `e6a112f4db0d0bec02f623c968c579116b7dfe9c`, fonte de runtime `56a659ac1fc7597f7e453bd7e39042742e8f408e`;
- monitor direto do produto: `3820d0edd5126ae416ea569b3dc30b5b0ce1a215`;
- branch Flow operacional: `codex/flow-history-proposal-vps-20261009`, que deve continuar no proposal SHA `0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0` durante a ativação inicial. O instalador relê o remoto autenticado antes de habilitar os timers.

Se qualquer branch tiver mudado, o bootstrap falha antes de instalar unidades.

## Pré-flight sem mutação

```bash
sudo EXPECTED_BUNDLE_SHA=<sha-final-do-bootstrap> \
     GIT_KEY_PATH=/etc/ebt-engineering/controller_ed25519 \
     KNOWN_HOSTS_PATH=/etc/ebt-engineering/known_hosts \
     scripts/ops/install_ebt_vps_automation_bundle.sh --check-only
```

Esse modo primeiro exige que o próprio checkout do bootstrap esteja limpo e exatamente em `EXPECTED_BUNDLE_SHA`. Depois clona fontes públicas em staging temporário, verifica os SHAs, manifesto, branch remota, permissões dos arquivos root-only e exige que os quatro timers EBT estejam inativos/desabilitados. Não habilita systemd.

## Instalação

Depois do preflight verde:

```bash
sudo EXPECTED_BUNDLE_SHA=<sha-final-do-bootstrap> \
     GIT_KEY_PATH=/etc/ebt-engineering/controller_ed25519 \
     KNOWN_HOSTS_PATH=/etc/ebt-engineering/known_hosts \
     scripts/ops/install_ebt_vps_automation_bundle.sh
```

A ordem é proposital:
1. watchdog read-only do scheduler GitHub;
2. monitor read-only do produto;
3. executor Flow por último.

O bootstrap é destinado a uma ativação limpa. Se algum timer EBT já estiver ativo/habilitado, ele falha antes de instalar. Depois que a instalação começa, qualquer erro dispara rollback automático dos quatro timers para evitar estado parcial ativo.

## Evidência sanitizada

```bash
sudo ebt-vps-automation-status
```

O coletor não lê nem imprime chaves/tokens. Ele retorna um JSON sanitizado com dois níveis separados:

- `installation_integrity`: PASS/FAIL da instalação e isolamento;
- `observed_health`: saúde observada do produto, scheduler GitHub e engenharia.

Isso evita confundir incidente externo com instalação quebrada. Por exemplo, o watchdog pode reportar `github_schedule=FAIL` por `schedule_gap` e, ao mesmo tempo, `installation_integrity=PASS` se os timers, branch, remote, isolamento da chave e monitores estiverem corretamente instalados.

O bootstrap executa esse coletor no fim da instalação. Se `installation_integrity` falhar, o comando retorna erro e o rollback automático desabilita os quatro timers. A primeira execução do agente pode ainda aparecer como `PENDING_FIRST_CYCLE` sem invalidar a instalação.

## Rollback

```bash
sudo ebt-vps-automation-disable
```

O rollback somente desabilita os quatro timers. Não apaga banco, aplicação, branches, commits ou evidências locais.


## Helpers persistentes

Ao final da instalação íntegra, o bootstrap instala:

- `/usr/local/sbin/ebt-vps-automation-status`;
- `/usr/local/sbin/ebt-vps-automation-disable`;
- `/opt/ebt-vps-automation/vps_automation_status.py`.

Assim status e rollback não dependem da permanência do checkout usado para instalar.


## Liberação do primeiro FLOW

O bundle instala o controlador Flow com `EBT_DEFER_TIMER_START=1`. Nesse momento:
- units e workspace estão instalados;
- `ebt-engineering-runner.timer` e `ebt-engineering-watch.timer` permanecem inativos/desabilitados;
- o serviço `ebt-engineering-runner.service` não pode estar ativo.

Depois o bundle instala os helpers persistentes e só então habilita os timers Flow.

O runner usa `OnActiveSec=2min`, não `OnBootSec`. Assim, mesmo numa VPS com horas de uptime, o primeiro agente não dispara imediatamente ao habilitar o timer. Há uma janela determinística para o veredito final de integridade antes do primeiro ciclo.
