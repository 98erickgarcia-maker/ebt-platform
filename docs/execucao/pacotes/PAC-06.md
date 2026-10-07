# PAC-06 | SQL, autorização por recurso e cache

Estado: demonstrado em QA no recorte em 07/10/2026; [registro](../../../evidencias/execucao/PAC-06/registro.md). G-SEG permanece aberto. 12h estimadas (7.5h implementação, 3.5h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 52-64h.

## Resultado integrado

Banco e autorização mantêm o isolamento inclusive em acesso por ID.

## Dependências

[PAC-05](PAC-05.md)

Tickets/gates externos: P04-04. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P04-05](../entregas/P04-05.md) | Criar índices e migration do recorte | 3h | N |
| [P04-06](../entregas/P04-06.md) | Conferir SQL/RLS do recorte com banco real | 3h | N |
| [P04-07](../entregas/P04-07.md) | Implementar autorização por recurso | 3h | N |
| [P04-08](../entregas/P04-08.md) | Isolar cache, sessão e troca de perfil | 3h | N (promovido de R2) |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir migration/índices no SQL real, ID direto, cache e troca de perfil.

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
