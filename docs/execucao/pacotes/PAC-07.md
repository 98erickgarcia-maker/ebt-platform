# PAC-07 | Auditoria, proteção da sessão e onboarding

Estado: planejado. 12h estimadas (8h implementação, 3h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 52-64h.

## Resultado integrado

Onboarding e trilha de auditoria fecham o gate de segurança.

## Dependências

[PAC-06](PAC-06.md)

Tickets/gates externos: P04-08. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P04-09](../entregas/P04-09.md) | Reusar evento de auditoria com minimização | 3h | R2 |
| [P04-10](../entregas/P04-10.md) | Conferir proteção de cookies ou tokens | 3h | R2 |
| [P04-11](../entregas/P04-11.md) | Fechar onboarding e cenários negativos | 3h | N |
| [P04-12](../entregas/P04-12.md) | Demonstrar G-SEG com dois consumidores | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Reproduzir onboarding, verificar negativas, proteção de sessão e ausência de segredo nos eventos.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-SEG; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
