# PAC-09 | Histórico, próxima ação e funil

Estado: planejado. 9h estimadas (6.75h implementação, 1.5h verificação/revisão e 0.75h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 85-94h.

## Resultado integrado

Interação, responsável, próxima ação e mudança de etapa persistem juntos.

## Dependências

[PAC-08](PAC-08.md)

Tickets/gates externos: P05-03. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P05-04](../entregas/P05-04.md) | Reaproveitar histórico de interações | 3h | R2 |
| [P05-05](../entregas/P05-05.md) | Reaproveitar responsável e próxima ação | 3h | R2 |
| [P05-06](../entregas/P05-06.md) | Configurar funil simples e mudança de etapa | 3h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Percorrer jornada comercial e conferir autoria, ordenação, negativa de perfil e tenant.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-CRM continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
