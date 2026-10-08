# PAC-16 | Reconciliação e jornadas integradas

Estado: planejado. 8h estimadas (4h implementação, 3h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 164-172h.

## Resultado integrado

Versão candidata reúne site, CRM e Flow/documentos do recorte.

## Dependências

[PAC-10](PAC-10.md), [PAC-12](PAC-12.md), [PAC-13](PAC-13.md), [PAC-20](PAC-20.md)

Tickets/gates externos: P05-GATE, P06-GATE, P07-GATE, P11-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P09-01](../entregas/P09-01.md) | Reconciliar resultados e versão entregue | 2h | R2 |
| [P09-02](../entregas/P09-02.md) | Conferir jornada de contato e tarefas | 2h | R2 |
| [P09-03](../entregas/P09-03.md) | Conferir jornada CRM em dois consumidores | 2h | N |
| [P09-04](../entregas/P09-04.md) | Conferir jornada de comunicação e documento privado | 2h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Confrontar manifesto com evidências e percorrer jornadas em A/B sem esconder pendências.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-RC continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
