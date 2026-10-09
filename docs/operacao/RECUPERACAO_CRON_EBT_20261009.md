# EBT Production Watch — recuperação de agendamento (09/10/2026)

## Objetivo e evidência observada

Acompanhar a **continuidade do disparo agendado** do workflow e tornar a origem de cada execução evidente. Antes da correção, a `main` possuía o cron `7,22,37,52 * * * *` desde o merge do PR #17, e a consulta à API do GitHub em 09/10/2026, por volta de 12h31 em Brasília, retornou `total_count=0` para `event=schedule`. A última execução conhecida do monitor ocorreu às 08h05 (Brasília) por `push`: https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37921637201 . Nesse momento, mais de 4h haviam passado sem um novo disparo do monitor.

A ausência de `schedule` é um defeito **de continuidade de supervisão**, não prova de falha do site. Últimas sondas tiveram 8/8 PASS; isso não comprova funcionamento atual.

## Diagnóstico atualizado — primeiro disparo real confirmado

Branch `fix/ebt-watch-schedule-recovery-20261009`:
- **Mantém o cron original** `7,22,37,52 * * * *`, pois houve disparo real bem-sucedido na `main` sem alterar o agendamento. Não há evidência que justifique mudar seus minutos.
- Acrescenta ao job a etapa `Record invocation origin and revision`, que registra `github.event_name`, `github.ref`, `github.sha` no log e no sumário de execução, sem imprimir segredos.
- Não modifica as sondas, dados da aplicação, banco, Azure, envio de e-mail, permissões do job ou tratamento de incidentes.
- Em 09/10/2026 às 16:57:56 UTC (13:57 Brasília), a API registrou **primeira execução real** com `event=schedule`, `conclusion=success`, SHA `f1a370d51d00bc8e0c87f065f9020658c3822cad`: https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37962877132. O job `agents` e todas as etapas tiveram sucesso. A consulta subsequente retornou `total_count=1`; **recorrência ainda não demonstrada**. Não atribuir a recuperação a este PR ainda não integrado.

## Diagnóstico e ativação (somente mediante revisão)

1. Abra https://github.com/98erickgarcia-maker/ebt-platform/actions/workflows/ebt-production-watch.yml . Confira se o workflow está **enabled** ou se aparece **Enable workflow**. Se estiver desativado, reabilite pela interface com as permissões apropriadas. Registrar evidência/horário.
2. Confirme em `Settings → Actions` que GitHub Actions não está bloqueado por política ou configuração do repositório. Este diagnóstico requer acesso com permissões suficientes; sem tal acesso, registrar bloqueio.
3. Revisar o diff e a CI do PR desta branch. **Não mesclar automaticamente**; apenas a etapa adicional de registro da origem é proposta para a `main`, sem alterar o cron.
4. Uma execução manual opcional somente de leitura pode testar o job, mas **não** comprova cron. Já existe um evento `schedule` real; agora é necessário observar a recorrência.
5. Consulte `GET /repos/98erickgarcia-maker/ebt-platform/actions/runs?event=schedule&per_page=30` e procure **novas execuções com evento `schedule`** posteriores à execução 37962877132, na `main`. Verifique conclusão, commit, início e artefato `ebt-ops-...`.
6. Refaça a consulta em janelas sucessivas. Falhas/cancelamentos exigem inspeção dos logs; silêncio por mais de 90 minutos exige alerta e investigação. O GitHub pode atrasar ou descartar execuções agendadas; não prometer precisão de 15 minutos.
7. Encerrar a issue https://github.com/98erickgarcia-maker/ebt-platform/issues/19 **somente depois** de observar disparos agendados e continuidade recuperada; checks `push` passando não bastam.

## Testes e verificações

- Rodar `python -m unittest discover -s tests/ops -v` na branch candidata e conferir logs reais do PR.
- A CI de PR testa sintaxe/rotinas, mas **não** verifica agendamento da `main`.
- Conferir que `.github/workflows/ebt-production-watch.yml` conserva `pull_request`, `push`, `schedule` e `workflow_dispatch`.
- Confirmar que, após revisão e integração, o sumário de workflow declara o evento de execução, branch e SHA sem dados privados.
- A Sentinela externa horária de ChatGPT é salvaguarda de alerta, não substituto para monitoramento a cada 15 minutos.

## Limitações e segurança

Nenhum merge, deploy, restart, alteração SQL/Azure ou mensagem real é autorizado neste PR. Se o GitHub não executar schedules mesmo com o workflow habilitado, o próximo passo é conferir políticas de Actions e suporte GitHub, não criar falsas execuções por pushes repetitivos. Fonte: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule .
