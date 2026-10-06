# PAC-17 | Migration, restore, operação e candidato

Estado: planejado. 8h estimadas (4h implementação, 3h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 172-180h.

## Resultado integrado

Candidato tem ensaio de atualização/retorno, recuperação e roteiro de piloto.

## Dependências

[PAC-16](PAC-16.md)

Tickets/gates externos: P09-04. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P09-05](../entregas/P09-05.md) | Ensaiar atualização de banco e retorno | 2h | N |
| [P09-06](../entregas/P09-06.md) | Ensaiar restore integrado e diagnóstico | 2h | N |
| [P09-07](../entregas/P09-07.md) | Preparar operação e aceite do piloto | 2h | R2 |
| [P09-08](../entregas/P09-08.md) | Fechar candidato e backlog após 200h | 2h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir retorno ensaiado, banco/arquivos restaurados, limites e autoria real do aceite.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-RC; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
