# PAC-08 | Cadastro único, busca e paginação

Estado: planejado. 9h estimadas (6.75h implementação, 1.5h verificação/revisão e 0.75h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 64-73h.

## Resultado integrado

Pessoa/organização cadastradas uma vez e recuperadas na consulta.

## Dependências

[PAC-07](PAC-07.md)

Tickets/gates externos: P04-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P05-01](../entregas/P05-01.md) | Fixar contrato mínimo de pessoa e organização | 3h | R2 |
| [P05-02](../entregas/P05-02.md) | Reaproveitar cadastro e prevenção de duplicidade | 3h | R2 |
| [P05-03](../entregas/P05-03.md) | Reaproveitar lista, busca e paginação | 3h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir duplicidade, ID estável, vínculos, recarregamento e paginação com dados sintéticos.

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
