# PAC-10 | Segundo consumidor, importação e fechamento do CRM

Estado: planejado. 10h estimadas (6.5h implementação, 2.5h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 94-104h.

## Resultado integrado

CRM demonstrável em dois consumidores, com importação delimitada e manual.

## Dependências

[PAC-09](PAC-09.md)

Tickets/gates externos: P05-06. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P05-07](../entregas/P05-07.md) | Aplicar marca e vocabulário a uma tela completa | 3h | R2 |
| [P05-08](../entregas/P05-08.md) | Rodar segundo consumidor sem forks de regra | 3h | N |
| [P05-09](../entregas/P05-09.md) | Preparar importação de planilha limpa do recorte | 2h | R2 |
| [P05-10](../entregas/P05-10.md) | Demonstrar G-CRM e manual de implantação | 2h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir marca sem fork de regra, repetição da importação e resultado persistido de G-CRM.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G-CRM; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
