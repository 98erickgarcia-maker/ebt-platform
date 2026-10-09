# PAC-12 | Versões, concorrência e recuperação documental

Estado: planejado. 12h estimadas (7.5h implementação, 3.5h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 152-164h.

## Resultado integrado

Revisão/versionamento e restore preservam documento e histórico.

## Dependências

[PAC-11](PAC-11.md)

Tickets/gates externos: P06-04. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P06-05](../entregas/P06-05.md) | Reaproveitar revisão e nova versão | 3h | R2 |
| [P06-06](../entregas/P06-06.md) | Conferir falha, repetição e concorrência | 3h | N |
| [P06-07](../entregas/P06-07.md) | Conferir recuperação de banco e arquivo | 3h | N |
| [P06-08](../entregas/P06-08.md) | Demonstrar G-GED com segundo consumidor | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir repetição, concorrência, hash dos bytes restaurados e segundo consumidor de G-GED.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-GED; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
