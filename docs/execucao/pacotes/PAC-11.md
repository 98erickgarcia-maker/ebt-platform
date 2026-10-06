# PAC-11 | Documento privado e acesso autorizado

Estado: planejado. 12h estimadas (8.5h implementação, 2.5h verificação/revisão e 1h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 104-116h.

## Resultado integrado

Documento vinculado pode ser enviado e baixado apenas por ator autorizado.

## Dependências

[PAC-07](PAC-07.md), [PAC-10](PAC-10.md)

Tickets/gates externos: P04-GATE, P05-GATE. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P06-01](../entregas/P06-01.md) | Delimitar documento comercial do piloto | 3h | R2 |
| [P06-02](../entregas/P06-02.md) | Reaproveitar metadados e vínculo | 3h | R2 |
| [P06-03](../entregas/P06-03.md) | Adaptar upload privado e validações | 3h | R2 |
| [P06-04](../entregas/P06-04.md) | Garantir download com autorização por ID | 3h | N |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Exercitar upload inválido, acesso por ID, negativa de B e falha entre metadado e arquivo.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote é parcial. G-GED continua pendente até o pacote final da fase e suas provas. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
