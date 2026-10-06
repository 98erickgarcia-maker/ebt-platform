# PAC-13 | Tarefas vinculadas e prazos

Estado: planejado. 12h estimadas (7.75h implementação, 2.75h verificação/revisão e 1.5h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 128-140h.

## Resultado integrado

Tarefa passa por criação, conclusão/cancelamento e atualização das pendências.

## Dependências

[PAC-10](PAC-10.md), [PAC-12](PAC-12.md)

Tickets/gates externos: P05-GATE, P06-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P07-01](../entregas/P07-01.md) | Fixar contrato da tarefa vinculada | 2h | R2 |
| [P07-02](../entregas/P07-02.md) | Reaproveitar criação, lista e filtros | 2h | R1 |
| [P07-03](../entregas/P07-03.md) | Reaproveitar conclusão e cancelamento | 2h | R2 |
| [P07-04](../entregas/P07-04.md) | Conferir datas e indicação de atraso | 2h | R2 |
| [P07-05](../entregas/P07-05.md) | Exibir pendência interna sem canal externo | 2h | R2 |
| [P07-06](../entregas/P07-06.md) | Demonstrar G-TASK e métricas básicas | 2h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Reconciliar contador, prazo/atraso, histórico e alterações permitidas/proibidas de G-TASK.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-TASK; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
