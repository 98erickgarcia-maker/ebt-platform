# PAC-20 | Falhas, interface e gate de comunicação

Estado: planejado. 12h estimadas (7h implementação, 4h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 128-140h.

## Resultado integrado

Falhas, interface e gate de comunicação.

## Dependências

[PAC-19](PAC-19.md)

Tickets/gates externos: P11-08. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P11-09](../entregas/P11-09.md) | Tratar timeout, retry e envio desconhecido | 3h | N |
| [P11-10](../entregas/P11-10.md) | Mostrar conversa e resposta na interface Connect | 3h | N |
| [P11-11](../entregas/P11-11.md) | Validar jornada e negativas do canal | 3h | N |
| [P11-12](../entregas/P11-12.md) | Demonstrar G-MSG e manual de operação | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir API, assinatura, persistência, A/B, duplicatas e status observados na versão do canal; mock não homologa provedor.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-MSG; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
