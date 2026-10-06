# PAC-15 | Tramitação e encerramento do Flow

Estado: planejado. 12h estimadas (7h implementação, 4h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 152-164h.

## Resultado integrado

Uma transição autorizada e encerramento deixam resultado auditável.

## Dependências

[PAC-14](PAC-14.md)

Tickets/gates externos: P08-04. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P08-05](../entregas/P08-05.md) | Implementar uma transição manual autorizada | 3h | N |
| [P08-06](../entregas/P08-06.md) | Implementar encerramento com resultado | 3h | N |
| [P08-07](../entregas/P08-07.md) | Conferir falhas e persistência do fluxo | 3h | N |
| [P08-08](../entregas/P08-08.md) | Demonstrar G-FLOW e limites do piloto | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Negar transição inválida, conferir atomicidade estado/histórico e recuperação de G-FLOW.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-FLOW; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
