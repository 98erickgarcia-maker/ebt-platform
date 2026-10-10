# Bootstrap único das automações Linux da EBT

O bootstrap `scripts/ops/install_ebt_vps_automation_bundle.sh` reduz a ativação operacional a um único fluxo reproduzível sem incorporar segredos ao repositório.

## Fontes imutáveis

O script exige e confere:
- Flow/controller source: `9dc3b5ff647aa2453e18cc3148f13d1364145741`;\n- Flow proposal initial SHA: `0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0`;
- watchdog do cron: head `e6a112f4db0d0bec02f623c968c579116b7dfe9c`, fonte de runtime `56a659ac1fc7597f7e453bd7e39042742e8f408e`;
- monitor direto do produto: `3820d0edd5126ae416ea569b3dc30b5b0ce1a215`;
- branch Flow operacional: `codex/flow-history-proposal-vps-20261009`, que deve continuar no proposal SHA `0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0` durante a ativação inicial. O instalador relê o remoto autenticado antes de habilitar os timers.

Se qualquer branch tiver mudado, o bootstrap falha antes de instalar unidades.

## Pré-flight sem mutação

```bash
sudo GIT_KEY_PATH=/etc/ebt-engineering/controller_ed25519 \
     KNOWN_HOSTS_PATH=/etc/ebt-engineering/known_hosts \
     scripts/ops/install_ebt_vps_automation_bundle.sh --check-only
```

Esse modo clona fontes públicas em staging temporário, verifica os SHAs, manifesto, branch remota e permissões dos arquivos root-only. Não habilita systemd.

## Instalação

Depois do preflight verde:

```bash
sudo GIT_KEY_PATH=/etc/ebt-engineering/controller_ed25519 \
     KNOWN_HOSTS_PATH=/etc/ebt-engineering/known_hosts \
     scripts/ops/install_ebt_vps_automation_bundle.sh
```

A ordem é proposital:
1. watchdog read-only do scheduler GitHub;
2. monitor read-only do produto;
3. executor Flow por último.

## Evidência sanitizada

```bash
sudo scripts/ops/collect_ebt_vps_automation_status.sh
```

O coletor não lê nem imprime chaves/tokens. Ele mostra estado dos timers, branch/SHA do workspace e subconjuntos sanitizados dos arquivos de estado.

## Rollback

```bash
sudo scripts/ops/disable_ebt_vps_automation.sh
```

O rollback somente desabilita os quatro timers. Não apaga banco, aplicação, branches, commits ou evidências locais.
