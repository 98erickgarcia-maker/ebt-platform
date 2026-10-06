# PAC-02 | Estrutura, configuração e dados sintéticos

Estado: planejado. 8h estimadas (3h implementação, 4h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 12-20h.

## Resultado integrado

Estrutura executável e configuração própria para dois consumidores.

## Dependências

[PAC-01](PAC-01.md)

Tickets/gates externos: P01-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P02-01](../entregas/P02-01.md) | Registrar arquitetura e limite do Core inicial | 2h | N |
| [P02-02](../entregas/P02-02.md) | Criar estrutura e comandos reproduzíveis | 2h | N |
| [P02-03](../entregas/P02-03.md) | Separar configuração e segredos por ambiente | 2h | N |
| [P02-04](../entregas/P02-04.md) | Criar massa sintética para dois consumidores | 2h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir reprodução dos comandos, separação de configuração e ausência de dados reais.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G1 continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
