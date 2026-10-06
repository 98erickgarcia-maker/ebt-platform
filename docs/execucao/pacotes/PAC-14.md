# PAC-14 | Protocolo, numeração e consulta

Estado: planejado. 12h estimadas (7h implementação, 4h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 140-152h.

## Resultado integrado

Protocolo vincula interessado/documento e apresenta histórico coerente.

## Dependências

[PAC-07](PAC-07.md), [PAC-12](PAC-12.md), [PAC-13](PAC-13.md)

Tickets/gates externos: P04-GATE, P06-GATE, P07-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P08-01](../entregas/P08-01.md) | Especificar fluxo e numeração do piloto | 3h | N |
| [P08-02](../entregas/P08-02.md) | Criar protocolo e sequência transacional | 3h | N |
| [P08-03](../entregas/P08-03.md) | Vincular interessado, documento e responsável | 3h | N |
| [P08-04](../entregas/P08-04.md) | Criar consulta e histórico de movimentação | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Criar concorrente e repetir solicitação no SQL real; conferir unicidade e vínculos.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-FLOW continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
