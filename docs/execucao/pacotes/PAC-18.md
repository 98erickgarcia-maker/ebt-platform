# PAC-18 | Contrato do canal e recebimento durável

Estado: planejado. 12h estimadas (7h implementação, 4h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 104-116h.

## Resultado integrado

Contrato do canal e recebimento durável.

## Dependências

[PAC-07](PAC-07.md), [PAC-10](PAC-10.md), [PAC-13](PAC-13.md)

Tickets/gates externos: P04-GATE, P05-GATE, P07-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P11-01](../entregas/P11-01.md) | Fixar canal, conta de QA e versão do provedor | 3h | N |
| [P11-02](../entregas/P11-02.md) | Definir mensagens, conversas e contrato de resposta | 3h | N |
| [P11-03](../entregas/P11-03.md) | Validar assinatura e handshake do webhook | 3h | N |
| [P11-04](../entregas/P11-04.md) | Persistir entrada e deduplicar eventos | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Conferir API, assinatura, persistência, A/B, duplicatas e status observados na versão do canal; mock não homologa provedor.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-MSG continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
