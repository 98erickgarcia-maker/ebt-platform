# Engenharia EBT por blocos: contrato detalhado

Referência: 09/10/2026. Manifesto operacional: `planejamento/engineering_blocks.json`. O bloco atual propõe paginação do histórico Flow; o produto completo continua dividido em recortes. Este documento não promove gates ou comprova instalação remota.

## Papéis e execução

Os dez papéis são escopo, contratos, backend, frontend, negativos, acessibilidade, segurança, regressão, revisão e passagem. O runner executa uma invocação por vez, na ordem FLOW-01 até FLOW-10. Cada invocação é nova e recebe os IDs concluídos e a tarefa; não existe transferência automática de conversa nem dez processos persistentes.

| Tarefa | Depende de | Saída principal | Estimativa interna |
|---|---|---|---|
| FLOW-01 | baseline disponível | Fonte, recorte e ledger de cenários | 1h |
| FLOW-02 | 01 | Contrato cursor/limite/ordenação/compatibilidade | 1h |
| FLOW-03 | 02 | Backend limitado e testes sintéticos | 3h |
| FLOW-04 | 03 | Consumidor UI e tratamento de estado | 2h |
| FLOW-05 | 03, 04 | Negativas com resultados e lacunas SQL | 2h |
| FLOW-06 | 04 | Teclado, feedback e acessibilidade | 1h |
| FLOW-07 | 03, 05 | Segurança das páginas e cursor | 1h |
| FLOW-08 | 05, 06, 07 | Regressão integrada focal e E2E fonte | 2h |
| FLOW-09 | 08 | Revisão de diff/provas e correções | 1h |
| FLOW-10 | 09 | Manifesto de passagem, limites e rollback | 1h |

Os 15h são estimativa do recorte, incluindo revisão e validação; não são horas reais nem acréscimo ao orçamento. Preservam-se 180h de entregas e 20h de reserva. O plano histórico adiava Flow; a distribuição deste novo recorte dentro das 180h precisa ser reconciliada explicitamente com o backlog ativo. Não consumir reserva como funcionalidade ou presumir que tarefas antigas foram entregues.

Cada tarefa possui entradas, entregáveis, critérios de aceite, negativas, caminhos atribuídos, limite de arquivos e regra de recuperação no manifesto. O runner valida `depends_on` contra IDs concluídos antes de chamar o modelo. Valida também `write_paths` como subconjunto da allowlist global e `max_changed_files` como inteiro dentro dos caminhos atribuídos. Campos ausentes usam compatibilidade: dependências vazias, caminhos globais e limite do conjunto atribuído.

Hashes dos arquivos permitidos são capturados antes e depois da invocação, incluindo criação e remoção. Somente o delta de conteúdo desta invocação conta no escopo/limite da tarefa; arquivo sujo anterior que permaneça intacto não é atribuído à rodada atual. O delta é conferido mesmo quando o modelo retorna erro e novamente depois dos checks. Violação bloqueia a tarefa sem promover completed, commit ou sincronização. Arquivos fora da allowlist global continuam recusados pela verificação Git e pelos controles existentes. Os registros da tarefa incluem caminhos alterados, hashes antes/depois e dependências. O patch contra HEAD pode incluir conteúdo anterior do mesmo arquivo; os hashes antes/depois identificam o delta observado, sem prometer patch isolado byte a byte.

Entregáveis, critérios de aceite, estimativas, recuperação e negativas continuam contratos de agente/revisão, repetidos em `instruction`; não são certificações automáticas de negócio. Os mecanismos reais incluem ordem da fila, dependências, lock do processo, allowlists global/por tarefa, limite de arquivos, checks e evidências. Os testes sintéticos cobrem dependência ausente antes da IA, alteração globalmente permitida fora da tarefa, excesso de arquivos, arquivo sujo anterior preservado, remoção e violação durante erro do modelo/checks.

## Critérios que bloqueiam o recorte

A paginação requer tamanho padrão e máximo, ordenação determinística com desempate estável já existente, cursor com semântica explícita, autorização a cada página e comportamento de compatibilidade. Não carregar todo o histórico e apenas cortar em memória. Sem chave estável compatível com o schema atual, bloquear; nova migration não pertence ao manifesto.

Negativas incluem cursor malformado/excessivo/adulterado, limites inválidos, ID direto entre tenants, carteira incompatível, revogação entre páginas, igualdade de timestamps, inserção concorrente, erro de próxima página, cliques duplicados, troca de protocolo com resposta atrasada e separação segura entre vazio acessível e registro inacessível. Mudança de contrato/segurança recebe trilha N, sem dispensa R1 por origem histórica.

Frontend deve limpar contexto anterior quando protocolo/perfil muda e recusar resposta atrasada que carregue histórico de outro contexto. Feedback de carregamento/erro, retry, foco visível, teclado, nomes acessíveis e controles desabilitados devem fazer parte da revisão. Build não demonstra tela, teclado, leitor de tela ou reflow inspecionados.

## Evidência versionada

O registro de cada tarefa identifica tarefa/papel, branch, HEAD, horário UTC, cenário, caminho e hash, alteração de comportamento, comando executado, resultado, ambiente, limites e próximo passo. Quando a árvore ainda não foi commitada, HEAD sozinho não identifica o candidato: registrar também hashes de snapshot/patch. Evidência histórica só vale para sua versão e cenário; composição ou correção de segurança invalida as negativas afetadas.

O controlador persiste `checkpoint.json`, `heartbeat.json`, `<task_id>.json`, `<task_id>.patch` e snapshots em `artifacts/<task_id>/`. Os caminhos concretos dependem do estado configurado pelo supervisor. Não publicar arquivos privados ou detalhes brutos de fornecedor. O documento `FLOW_HISTORY_PAGINATION_PROPOSAL.md` é um entregável futuro do bloco, não uma implementação já certificada por este detalhamento.

Checks configurados: diff Git, `flow_backend` dedicado e build frontend conforme tarefa. O `flow_backend` chama `tests/WazVox.ProtocolTests -- --flow-history`; enquanto FLOW-03 não substituir o sentinel fail-closed por testes executáveis do contrato de paginação, esse check falha de propósito e não pode cair na suíte WazVox genérica. E2E escrito é cenário-fonte; E2E aprovado exige execução. Fake de HTTP ou teste de parser não aprova SQL real, isolamento autenticado, restore, aceite ou publicação. Classificar cenário indisponível como NOT_RUN, preservando o impedimento concreto.

`task_verified` significa tarefa com artefatos e checks configurados; `proposal_review_ready` significa somente que as dez tarefas da fila de proposta foram verificadas pelos gates locais configurados. Esse estado não equivale a release-ready: CI do SHA candidato e as provas SQL/browser exigidas pelo risco continuam separadas. O papel revisão usa uma nova invocação, mas não comprova revisores humanos independentes ou equipe separada. Nenhum desses estados significa Enterprise completo.

## Continuidade e supervisor

Heartbeat v1 usa IDs, status, timestamps UTC, PID e SHA sanitizados. `updated_at` mostra observação; `progress_at` muda somente com tarefa efetivamente verificada. Processo vivo, PID e lease não comprovam progresso útil nem identidade criptográfica do processo. O monitor observa a cada 15 minutos; thresholds padrão de lease/progresso são 30 minutos. Ele distingue alive, progressing, stalled, blocked, succeeded e monitor_error. A conclusão terminal pertence à tarefa/proposta declarada, sem promover gate do produto.

Um único runner mantém lock do kernel e checkpoint. Rodada é limitada a 900s; política permite no máximo 12 chamadas por dia, backoff de 6h em cota e 30min em falha. Cota/autenticação não autorizam compra, chave nova, credencial copiada ou provedor pago alternativo. Monitor não reinicia processo, corrige código, envia alerta ou aciona IA. PAUSE impede nova rodada.

Em queda/timeout, conservar último checkpoint e diff parcial; conferir paths/hashes antes de repetir a mesma tarefa. A retomada reconstrói contexto em nova invocação ephemeral, sem session-ID automático. Falha de checks/escopo bloqueia a fila afetada; não ampliar paths, apagar evidência ou editar completed para avançar. SHA remoto divergente exige reconciliação; nunca reset/clean/force-push.

O runner exige que o workspace esteja exatamente na `branch` declarada no manifesto; qualquer outra branch `codex/*` é recusada antes da invocação. A política `allow_push` permanece conforme configuração existente, sem alteração por este detalhamento. Quando um controlador autorizado fizer sincronização, commit local e SHA remoto são provas separadas. Nenhuma sincronização de proposta autoriza merge, deploy ou migration. Depois da conclusão, novo módulo exige recorte, dependências e critérios próprios; não reexecutar a mesma revisão sem mudança verificável.

## Passagem para publicação

Exigir candidato composto identificado, CI pertinente no SHA exato, negativas SQL/browser do recorte conforme risco, manifesto de artefato/configuração, retorno à versão anterior e observação online do host/versionamento. SQL local, health público, acesso autenticado, navegação online e aceite permanecem distintos. Nunca preencher uma prova ausente usando outra.

Sem mudança de schema neste recorte, rollback é retorno do artefato/configuração preservados; não inventar rollback de migration. Fonte/artefato anterior, pré-requisitos, limites e ação de retorno devem estar identificados antes da publicação. Alteração de orçamento/escopo deve preservar histórico e ser reconciliada pelo responsável, sem fabricar horas ou apagar pendências.
