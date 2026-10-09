# EBT | GitHub no Teams

A integracao publica notificacoes do GitHub por um webhook do Microsoft Teams Workflows.

## Arquivos

- `.github/workflows/ebt-teams-notifications.yml`: workflow de eventos.
- `scripts/ops/github_teams_notify.py`: envia alertas resumidos.
- `tests/ops/test_github_teams_notify.py`: testes unitarios sem envio real.
- `.github/workflows/ebt-production-watch.yml`: envia alertas apenas em mudancas de incidentes.

## Ativacao

1. No Teams, escolha o canal e crie um Workflow para receber alertas de webhook.
2. No GitHub, crie o repository secret `TEAMS_WORKFLOWS_WEBHOOK_URL` com a URL gerada. Nao publique o segredo no codigo.
3. Apos revisar e integrar o pull request, execute manualmente o workflow `EBT Teams Notifications` na aba Actions.
4. Confira uma mensagem de teste no canal escolhido.

Sem webhook configurado, nao ha notificacao real. O codigo nao realiza merge, deploy nem correcoes automaticas. Para corrigir codigo com IA em modo autonomo sera necessario configurar executor separado com testes e revisao.

## Testes

`python -m unittest discover -s tests/ops -p 'test_github_teams_notify.py' -v`
