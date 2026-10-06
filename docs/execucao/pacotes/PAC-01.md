# PAC-01 | Baseline e contrato do primeiro recorte

Estado: planejado. 12h estimadas (7.75h implementação, 2.75h verificação/revisão e 1.5h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: 0-12h.

## Resultado integrado

Fonte congelada, fluxo escolhido e mapa dos contratos reutilizáveis.

## Dependências

Sem pacote anterior obrigatório.

Tickets/gates externos: nenhum. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.

## Tarefas internas e aceite original

| Ticket | Resultado/atividade | Horas | Trilha |
|---|---|---:|---|
| [P01-01](../entregas/P01-01.md) | Congelar fontes e hashes do fluxo escolhido | 2h | R2 |
| [P01-02](../entregas/P01-02.md) | Separar evidência aprovada, incompleta e histórica | 2h | R1 |
| [P01-03](../entregas/P01-03.md) | Escolher o fluxo mínimo do primeiro CRM | 2h | R2 |
| [P01-04](../entregas/P01-04.md) | Mapear contratos e vínculos desse fluxo | 2h | R2 |
| [P01-05](../entregas/P01-05.md) | Conferir direitos de uso e dependências | 2h | R2 |
| [P01-06](../entregas/P01-06.md) | Fechar baseline e ordem dos pequenos PRs | 2h | R2 |

Ler e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.

## Revisão específica do conjunto

Confrontar versão/hash e cenário; localizar a falha de onboarding e os limites do reuso.

1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.
2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.
3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.
4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.

## Gate e ambiente

Este pacote contém o fechamento de G0; exige todas as provas aplicáveis da fase. Não equivale a produção.

Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.

## Fechamento e continuidade

[Registro do pacote](../../../templates/PACOTE_CODEX.md) | [Ciclo de execução/revisão](../EXECUCAO_PELO_CODEX.md) | [Todos os pacotes](../PACOTES_CODEX.md)

Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.
