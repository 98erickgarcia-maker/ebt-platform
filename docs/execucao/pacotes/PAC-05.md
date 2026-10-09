# PAC-05 | Identidade e escopo de tenant

Estado: planejado. 12h estimadas (7.5h implementação, 3.5h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 28-40h.

## Resultado integrado

Identidade alimenta o contexto e restringe consultas/gravações.

## Dependências

[PAC-03](PAC-03.md)

Tickets/gates externos: P02-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P04-01](../entregas/P04-01.md) | Definir matriz usuário, empresa e ação | 3h | N |
| [P04-02](../entregas/P04-02.md) | Reusar sessão/login com limites claros | 3h | R2 |
| [P04-03](../entregas/P04-03.md) | Definir TenantContext a partir da identidade | 3h | N |
| [P04-04](../entregas/P04-04.md) | Aplicar escopo a consultas e gravações | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Tentar manipular tenant recebido do cliente e cruzar leitura/gravação entre A e B.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-SEG continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
