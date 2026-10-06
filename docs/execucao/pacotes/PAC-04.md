# PAC-04 | Site essencial completo

Estado: planejado. 12h estimadas (8.25h implementação, 2.25h verificação/revisão e 1.5h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 28-40h.

## Resultado integrado

Pacote de site com navegação, identidade, contato, manual e retorno.

## Dependências

[PAC-01](PAC-01.md), [PAC-03](PAC-03.md)

Tickets/gates externos: P01-GATE, P02-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P03-01](../entregas/P03-01.md) | Escolher uma única base de site existente | 2h | R1 |
| [P03-02](../entregas/P03-02.md) | Centralizar marca, contato e serviços do pacote | 2h | R2 |
| [P03-03](../entregas/P03-03.md) | Reaproveitar páginas e navegação | 2h | R1 |
| [P03-04](../entregas/P03-04.md) | Conferir formulário e canal efetivo | 2h | R2 |
| [P03-05](../entregas/P03-05.md) | Executar regressão visual e de acesso focal | 2h | R1 |
| [P03-06](../entregas/P03-06.md) | Preparar entrega, manual e retorno do site | 2h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Percorrer páginas em celular/computador; conferir canal efetivo e diferenças da fonte aprovada.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-SITE; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
