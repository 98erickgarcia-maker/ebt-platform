# PAC-19 | Conversa, resposta e callbacks

Estado: planejado. 12h estimadas (7h implementação, 4h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 116-128h.

## Resultado integrado

Conversa, resposta e callbacks.

## Dependências

[PAC-18](PAC-18.md)

Tickets/gates externos: P11-04. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P11-05](../entregas/P11-05.md) | Processar evento e vincular contato e conversa | 3h | N |
| [P11-06](../entregas/P11-06.md) | Registrar resposta e outbox na mesma transação | 3h | N |
| [P11-07](../entregas/P11-07.md) | Enviar texto pelo adapter oficial delimitado | 3h | N |
| [P11-08](../entregas/P11-08.md) | Conciliar callbacks e eventos fora de ordem | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir API, assinatura, persistência, A/B, duplicatas e status observados na versão do canal; mock não homologa provedor.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-MSG continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
