# PAC-03 | Banco, storage, diagnóstico e CI

Estado: planejado. 8h estimadas (3.5h implementação, 3.5h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 20-28h.

## Resultado integrado

Persistência de QA e fundação demonstradas no ambiente identificado.

## Dependências

[PAC-02](PAC-02.md)

Tickets/gates externos: P02-04. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P02-05](../entregas/P02-05.md) | Montar banco e storage exclusivos de QA | 2h | N |
| [P02-06](../entregas/P02-06.md) | Reaproveitar cliente HTTP e padrões de erro | 2h | R2 |
| [P02-07](../entregas/P02-07.md) | Configurar CI mínimo e diagnóstico seguro | 2h | N |
| [P02-08](../entregas/P02-08.md) | Demonstrar fundação e registrar G1 | 2h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Exercitar erro HTTP, salvar/recarregar, diagnóstico sanitizado e os critérios de G1.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G1; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
