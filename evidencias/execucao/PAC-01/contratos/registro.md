# P01-03 e P01-04 — recorte e contratos CASST

Data: 09/10/2026. Autoria técnica: agente contratos do Codex. Ambiente: inspeção estática Windows, checkout CASST consultado somente para leitura. Não houve execução da jornada, teste autenticado, build, migração, envio, cópia de banco ou publicação. Horas previstas: 2h + 2h, dentro das 180h; tempo técnico real não medido por cronômetro, não lançar estimativa como horas consumidas. Reserva não acionada.

Fonte: `C:\Users\Ivair Silva\Documents\Codex\2026-08-18\CRM_CASST_WEB\.worktrees\crm-casst-foundation`. Caminhos abaixo são relativos a essa raiz. A versão efetiva é o conteúdo local de cada arquivo registrado em `fontes-hashes.json`, não somente HEAD. Árvore completa, direitos e cenários históricos pertencem aos demais tickets do PAC-01. Este registro não aprova G0 isoladamente.

## P01-03 — ficha fechada para implementação posterior

Recorte escolhido: cadastro de organização prospect, pessoa de contato vinculada, histórico comercial e próxima ação com responsável. Preservar `Prospect.Id`, `Person.Id`, `ProspectPersonLink.Id` e `CommercialInteraction.Id`; uma pessoa pode participar de vários vínculos sem criar uma nova identidade por tela. O ID da organização prospect será o ID canônico deste recorte. Não prometer conversão em cliente ativo nesta jornada.

Jornada a demonstrar em QA: vendedor cadastra organização sintética e contato; relê o mesmo ID; registra contato concluído; agenda acompanhamento; relê histórico e agenda; conclui a ação com resultado e follow-up atômico; recarrega e confirma datas, responsável e histórico persistidos. Gestor consulta a carteira autorizada; vendedor de outra carteira e tenant B recebem negativa para IDs de A. Nenhuma etapa envia mensagem real.

Perfis observados: `Seller`, `CommercialManager`, `Administrator`; matriz efetiva das demais funções depende de `TenantPolicies` e revisão de segurança. Vendedor exige propriedade do prospect e das interações; gestor não deve ganhar acesso a outro tenant. Eventos incluem cadastro/atualização, vínculo de pessoa, agendamento, conclusão, cancelamento, avanço automático para Contacted e auditoria. Aceite operacional do usuário permanece pendente.

Campos mínimos funcionais: nome da organização, tipo Company, responsável ativo, estado comercial; contato nome e ao menos um canal sintético; vínculo/cargo/decisor quando pertinente; interação tipo, assunto, responsável, ProspectId e PersonId; para plano, PlannedAt; para conclusão, CompletedAt e Result; NextStep e FollowUp quando existir acompanhamento. Datas são DateTimeOffset; GUIDs são strings no frontend; RowVersion é token base64 opaco. Campos opcionais do contrato não serão apagados nem renomeados por alteração de rótulo.

Até cinco etapas ativas propostas: New=1, PendingContact=2, Contacted=3, Qualified=4, Nurturing=5. A fonte tem SETE estados persistidos, incluindo Disqualified=6 e Converted=7. Essa escolha documental NÃO demonstra um funil de cinco etapas na UI/API. Restringir ou configurar etapas é adaptação R2; se mudar validação de contrato/schema/segurança, promover a N. Preservar os valores 6/7 nos registros existentes e tratar resultados terminais sem renumerar enum. Sem implementação, C02 permanece pendente.

Fora do pacote: proposta, conversão para cliente ativo, oportunidade, valor estimado, financeiro, OS, SST, importação de dados reais, comunicação automática, Outlook e WhatsApp oficiais, documentos e workflow. A fonte `CustomerEndpoints.cs:109-113` condiciona cadastro de cliente a proposta aceita fora de Testing, salvo cadastro legado por Administrator/CommercialManager. `ProspectContracts.cs:315-321` inclui EstimatedValue no contrato de abertura de oportunidade. Usar clientes ou oportunidade como cadastro simples introduziria dependência comercial escondida; por isso ambos ficam fora. O novo consumidor exigirá extração/adaptação própria, nunca remoção dessa regra na CASST.

| Critério | Resultado desta rodada | Prova e limite |
|---|---|---|
| P01-03-C01 jornada completa demonstrável | Pendente | Roteiro definido; execução integrada, reload e persistência não realizados |
| P01-03-C02 até cinco etapas | Pendente | Cinco etapas propostas; fonte possui sete estados e precisa adaptação |
| P01-03-C03 sem financeiro escondido | Satisfeito documentalmente | Prospect + interação; oportunidade/proposta/cliente ativo excluídos explicitamente |

## P01-04 — mapa real tela → API → regra → dados

| Operação / consumidor | Endpoint observado / produtor | Regra e dados |
|---|---|---|
| Listar e detalhar; `src/frontend/src/pages/ProspectsPage.tsx:246-263`; drawer `components/ProspectWorkspaceDrawer.tsx:43-62` | GET `/api/prospects/`, GET `/api/prospects/{prospectId}`; `src/backend/CrmCasst.Api/Endpoints/ProspectEndpoints.cs:28-33` | AccessibleProspects `:1105`; detalhe `:533-603`; `prospects`, `persons`, `prospect_person_links` com joins por TenantId |
| Cadastrar organização e contato; ProspectsPage e contrato `src/frontend/src/api/contracts.ts:781-803` | POST `/api/prospects/`; CreateProspectRequest/Response em `src/backend/CrmCasst.Application/Prospecting/ProspectContracts.cs:280-313` | Resolve responsável e pessoa no tenant; CreateAsync `ProspectEndpoints.cs:608` em diante; resposta contém Id e PersonId, seguida de GET detalhado |
| Alterar organização | PUT `/api/prospects/{prospectId}`; UpdateProspectRequest `ProspectContracts.cs:301` | `ProspectEndpoints.cs:867-895`: RowVersion decodificado, recurso acessível, concorrência; contrato não contém troca de responsável |
| Vincular pessoa / trocar contato principal; `ProspectsPage.tsx:2425`, `:289` | POST `/api/prospects/{prospectId}/people`, PUT `/api/prospects/{prospectId}/primary-person`; `ProspectEndpoints.cs:34-35` | AddProspectPersonRequest `ProspectContracts.cs:269`; PersonId e LinkId separados; troca requer RowVersion do prospect |
| Histórico da organização; `ProspectsPage.tsx:1435-1444`, drawer `:53-62` | GET `/api/interactions/?prospectId={id}`; `CommercialInteractionEndpoints.cs:21-22` | `CommercialInteractionAccessPolicy.cs:15-46`: tenant e carteira; listagem paginada não equivale a todo histórico |
| Agendar/registrar contato; `src/frontend/src/pages/AgendaPage.tsx:197-199` | POST `/api/interactions/`; `CommercialInteractionEndpoints.cs:29`; CommercialInteractionCreateRequest `src/backend/CrmCasst.Application/Interactions/CommercialInteractionContracts.cs:111` | `src/backend/CrmCasst.Infrastructure/Interactions/CommercialInteractionService.cs:45-115`: vínculos validados, follow-up e SaveChanges; datas/status persistidos em commercial_interactions |
| Concluir com follow-up; `AgendaPage.tsx:202-204` | POST `/api/interactions/{interactionId}/complete`; `CommercialInteractionEndpoints.cs:32` | CompleteRequest contém RowVersion e FollowUp; resposta Interaction + FollowUp, `CommercialInteractionContracts.cs:289`; serviço `:165-254` concorrência/auditoria e sincronização das datas da organização |
| Cancelar; `AgendaPage.tsx:207` | POST `/api/interactions/{interactionId}/cancel`; `CommercialInteractionEndpoints.cs:33` | RowVersion; serviço `:290-323`; histórico preservado, próxima data recalculada |
| Próximas ações / ausência de ação; `AgendaPage.tsx:150-175` | GET `/api/interactions/agenda`, GET `/api/interactions/agenda/prospects-without-next-action`; `CommercialInteractionEndpoints.cs:23-26` | Datas do prospect reconciliadas com ações planejadas/concluídas; `CommercialInteractionService.cs:528-599` |

O catálogo registra endpoints presentes no código; disponibilidade HTTP nesta rodada não foi verificada. Rotas excluídas existem na fonte e não estão sendo propostas como entregas EBT.

### Cardinalidades, origem e compatibilidade

Uma organização tem 0..N pessoas via ProspectPersonLink, com um PersonId principal opcional; cada vínculo liga exatamente um prospect a uma pessoa dentro do mesmo tenant. `ProspectPersonLinkConfiguration.cs:28-45` usa índice único ativo (TenantId, ProspectId, PersonId), FKs compostas e DeleteBehavior.Restrict. Uma organização tem 0..N interações; cada interação possui responsável e links opcionais ProspectId/CustomerId/PersonId/OpportunityId. Para este recorte exigir ProspectId, conservar PersonId quando houver contato e manter CustomerId/OpportunityId nulos. Nenhuma identidade global entre tenants foi prometida.

`ProspectDetailResponse` e `Prospect` concordam estaticamente nos IDs, People, RowVersion, datas, informações de origem e conversão (`ProspectContracts.cs:215-267`, `contracts.ts:682-779`). `SourceSystem`, `ExternalRecordId`, `SourceCode`, `ExternalIntegrationId` e `ExternalLegacyId` são origem externa e NÃO substituem GUID canônico. `ProspectConfiguration.cs:54-70` apresenta unicidade por tenant/origem/ID externo e FKs compostas. Importação é fora desta jornada; não inventar novo ExternalRecordId ou reutilizar dados reais.

Interação detalhada retorna RowVersion; listagem não contém esse token. O frontend deve carregar detalhe antes de concluir/cancelar. Produtor e consumidor de Completion concordam em interaction/followUp (`contracts.ts:1130`, contratos backend). `OriginType`/`OriginId` também existem e são opcionais; não preencher com sales-order/service-order neste recorte. Índice de automação idempotente em `CommercialInteractionConfiguration.cs:65-68` NÃO garante idempotência do POST manual genérico. Repetição de cadastro/interação manual exige caso dedicado e possível contrato novo; não alegar garantia por associação.

### Cache, efeito posterior e riscos de extração

Queries do prospect incluem prefixo tenant e invalidam list/detail após salvar (`ProspectsPage.tsx:246`, `:295`, `:342`, `:437-445`). Histórico de interações é invalidado em `:1207-1224`. Agenda usa raiz de interações; `AgendaPage.tsx:186-188` invalida detalhe/raiz ao criar/concluir/cancelar. Servidor sincroniza LastContactAt, NextContactAt e status do prospect (`CommercialInteractionService.cs:528-599`). Entretanto refresh da Agenda não invalida explicitamente a raiz prospects; conferir retorno à lista sem recarregar e corrigir no novo consumidor se datas ficarem stale. É uma lacuna de contrato UI/cache observada, não prova de falha executada.

`AuthProvider.tsx:9-29` cancela/remove queries cujo primeiro segmento é tenant quando tenant/usuário/perfil muda. `ProspectsPage.tsx:2879` usa `["interaction-edit", interactionId]`, sem prefixo tenant. Essa query escapa da limpeza observada; testar troca de usuário/perfil/tenant e corrigir escopo no consumidor EBT antes de G-SEG. Servidor continua responsável por autorizar IDs; nenhum teste de exploração ocorreu.

Mudança de tenant, autenticação, schema, índices ou storage pertence à trilha N. Extração/configuração do fluxo pertence a R2. Evidência histórica SQL/domínio/E2E não prova o consumidor EBT nem corrige onboarding. Falha histórica de ativação/onboarding registrada em docs/REVISAO_BASES.md continua pendência para G-SEG, com repetição E2E em ambiente próprio e dados sintéticos.

### Testes pertinentes identificados, não executados

`tests/CrmCasst.Api.Tests/Interactions/CommercialInteractionEndpointTests.cs`: Creates_filters_and_lists_planned_interaction_in_agenda (:368), Completing_with_follow_up_is_atomic_and_keeps_audit_free_of_PII (:427), Seller_and_tenant_boundaries_are_fail_closed_for_links_and_reads (:500), Atomic_follow_up_reconciles_both_source_dates (:285), Planned_interaction_can_be_cancelled_but_not_completed_afterwards (:753), Completed_interaction_can_be_corrected_with_concurrency_and_audit (:189). São candidatos a regressão do recorte, não resultados aprovados desta rodada. Testes de Person e Prospect, critérios de busca, guards de escrita tenant e AuthProvider também devem acompanhar extração.

Próxima verificação: contratos no novo consumidor com massa própria; salvar/reload; negativa A/B, vendedor e gestor; conflito RowVersion; POST repetido; cache após conclusão/cancelamento/troca de sessão; SQL real e onboarding E2E. Suíte SQLite não substitui SQL real e RLS. Não copiar fixtures com dados de cliente.

| Critério | Resultado desta rodada | Prova e limite |
|---|---|---|
| P01-04-C01 produtor/consumidor concordam | Parcial, estático | Formatos principais inspecionados; lacunas cache/escopo identificadas; sem teste HTTP/runtime |
| P01-04-C02 campo/cardinalidade registrados | Satisfeito documentalmente | IDs, origem, tokens, FKs e campos mínimos registrados com fontes |
| P01-04-C03 nenhum endpoint inventado | Satisfeito documentalmente | Todas as rotas citadas constam nos arquivos de endpoints hashados |

Saída: ficha e mapa entregues para revisão do PAC-01. Estado do produto continua não demonstrado em QA; G0 depende de todos os tickets e direitos/evidências exigidos. Este documento não autoriza PAC-02 automaticamente.


Verificação final: 20 hashes recalculados e comparados ao manifesto, todos coincidentes. Duração medida apenas desta verificação estática: 0.113 segundos; duração total da atividade não instrumentada. Resultado em verificacao.json. Não equivale a teste de produto.
