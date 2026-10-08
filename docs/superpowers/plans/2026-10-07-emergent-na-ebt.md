# Prospecção Emergent na EBT — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans para execução nativa ou superpowers:subagent-driven-development se o usuário escolher delegação. Executar uma tarefa verificável por vez.

**Goal:** integrar as capacidades já programadas de prospecção ao CRM EBT, preservando IDs, dados, canais e a identidade institucional em todas as telas.

**Architecture:** adaptar regras do pacote FastAPI/MongoDB ao backend .NET/SQL existente. React/TypeScript usa o shell, a sessão e o cliente HTTP EBT; contatos, histórico e próxima ação são os mesmos do CRM. Filas e receitas têm estado persistido, controle concorrente e conexão autorizada por tenant/carteira.

**Tech Stack:** .NET 10, EF Core SQL Server, React/TypeScript/Vite e Playwright já usados no projeto. HTTP dos provedores pelos clientes existentes ou clientes nomeados, sem biblioteca visual ou LLM adicional.

**Spec:** [especificação aprovada](../specs/2026-10-07-emergent-na-plataforma-ebt-design.md). Aprovação recebida do usuário em 07/10/2026. Este plano aguarda revisão e escolha do método de execução.

## Global Constraints

- Manter 180h de entregas e 20h de reserva; esta adaptação é escopo adicional, sem consumo fictício.
- Preservar fontes, alterações preexistentes, login, IDs, histórico, tarefas, documentos e WazVox.
- Identidade confirmada: preto `#101112`, branco suave `#f5f4f0`, laranja `#ff8b46` e logo EBT oficial.
- Segredos exclusivamente no servidor; nenhuma credencial, dado real ou anexo de cliente no pacote.
- Novos endpoints: `/api/connect/v1/prospecting`. Tenant e carteira são resolvidos pelo servidor.
- Imports/worker/segurança/schema recebem trilha N; provas anteriores não aprovam a adaptação.
- Envio real permanece desativado por padrão. Nenhuma campanha, alteração DNS, serviço pago ou publicação implícita.
- Pedidos 2/3/4 do pacote permanecem posteriores; templates/regras sem IA são o recorte funcional.
- Antes de cada edição, backup/hash dos arquivos afetados. Não usar reset/clean ou inclusão ampla no Git. Cada checkpoint contém apenas arquivos desta tarefa; commit não pode capturar mudanças acumuladas.

## Review Focus

1. CNPJ e e-mail iguais em carteiras diferentes: não expor registro privado nem movimentá-lo por deduplicação.
2. Edição de contato/template depois da aprovação: invalidar o digest antes de preparar ou enviar.
3. Queda após o provedor aceitar operação: preservar estado incerto e reconciliar; nunca reenviar automaticamente.
4. Dois workers e mudança de mês: consumo e cursor atômicos, sem ultrapassar limite ou repetir contato.
5. Navegar na página atual enquanto uma carga está pendente: descartar resposta antiga e terminar a carga substituta, sem travar a interface.

## Arquivos e contratos compartilhados

| Arquivo | Responsabilidade |
|---|---|
| `src/backend/Ebt.Platform.Api/ProspectingModels.cs` | Entidades de catálogo, metadados, receitas, templates/versões, aprovações/operações, supressão e consumo |
| `src/backend/Ebt.Platform.Api/ProspectingRules.cs` | CNPJ, normalização, classificação, variáveis e digest; sem I/O |
| `src/backend/Ebt.Platform.Api/ProspectingCrm.cs` | Vínculos ao Contact/Organization/Interaction/ContactTask existentes e DTOs de consulta |
| `src/backend/Ebt.Platform.Api/ProspectingEndpoints.cs` | Contratos HTTP, limites, idempotência, versão e autorização |
| `src/backend/Ebt.Platform.Api/ProspectingWorker.cs` | Receitas, cursor/limite/lease e fila durável |
| `src/backend/Ebt.Platform.Api/ProspectingOutlook.cs` | Configuração coerente, token application, rascunho, envio e reconciliação Graph |
| `src/backend/Ebt.Platform.Api/ProspectingMeta.cs` | Template oficial Meta, opt-in, consumo, eventos e integração de status |
| `src/backend/Ebt.Platform.Api/Data.cs`, `Program.cs`, `Migrations/*` | Registro das entidades, clientes, worker, endpoints e migration/RLS |
| `src/frontend/src/prospecting/api.ts` | DTOs e adaptadores usando `../api.ts` |
| `src/frontend/src/prospecting/ProspectingPage.tsx` | Painel, Contatos, Receitas, Templates, Conexões e Custos no padrão EBT |
| `src/frontend/src/App.tsx`, `style.css`, `Brand.tsx` | Navegação, integração com o mesmo contato e identidade global |
| `tests/integration/prospecting_qa.py` | Contratos HTTP/SQL sintéticos, isolamento, concorrência e recuperação |
| `src/frontend/e2e/prospecting.spec.ts`, `navigation.spec.ts` | Jornadas integradas e regressão da carga de navegação |

As entidades persistidas herdam `TenantRow`; versão, FKs, filtro e barreira SQL fazem parte da definição. DTOs públicos não expõem Secrets, token, cache ou erro bruto do provedor. Identificadores de contato nas novas rotas são os GUIDs atuais do CRM.

### Tarefa 0 — fechar os achados da base antes de ampliar

**Fonte:** `docs/qualidade/REVISAO_PROMPTSPELLSMITH_CONNECT_20261007.md`, confrontada com o runtime atual durante a revisão solicitada pelo usuário. Modificar `App.tsx`, `api.ts`, `CrmEndpoints.cs`, `MessagingEndpoints.cs` e `Security.cs` somente nos fluxos afetados.

- [ ] Reproduzir R01: abrir B enquanto os recursos de A ainda estão carregados e simular erro. Fazer `e2e/contact-context.spec.ts` exigir que tarefas/documentos/notas e ações de A nunca apareçam sob B. Limpar recursos, vincular dados ao ID carregado e bloquear ações até confirmar o contexto.
- [ ] Reproduzir R02 com mais de 25 contatos e filtro ativo. Acrescentar `contactName` e `recipient` à projeção autorizada de conversa; a UI identifica destinatário sem depender da página de contatos e bloqueia resposta sem essa identificação. Provar em `tests/integration/connect_hardening_qa.py` e browser.
- [ ] Reproduzir R03; impedir com 409 a alteração de carteira que deixe conversas/canais incompatíveis enquanto não houver transferência consistente. Manter a negativa do worker e provar que o contato e o canal continuam operacionais depois da tentativa recusada.
- [ ] Completar R04: `GET /api/admin/api-keys` retorna somente metadados autorizados e Configurações oferece revogação pelo ID. Provar perda de acesso, expiração e negativa B; nunca retornar token/hash pela listagem.
- [ ] Completar R05: titular autenticado aceita convite válido correspondente ao próprio e-mail, sem redefinir senha; outro titular, expirado e replay são recusados ou retornam resultado idempotente já confirmado. Provar a nova associação A/B com SQL sintético.
- [ ] Executar `python tests/integration/connect_hardening_qa.py` e os E2E novos/afetados; registrar resultados da versão, sem promover o relatório histórico para corrigido por inferência.
- [ ] Revisar diff/hash e registrar checkpoint. Essa correção antecede o uso desses contratos pela prospecção e não representa contratação de novos módulos.

### Tarefa 1 — regras, schema e isolamento

**Interfaces:** `ProspectingRules.Cnpj(string value): string`, `Score(CatalogBusiness row): ProspectScore`, `Render(string text, IReadOnlyDictionary<string,string> variables): string`, `Digest(ProspectPreview preview): string`. `PlatformDb` recebe DbSets das novas entidades; `ProspectingEndpoints.Map(WebApplication app): void` mantém as rotas atuais intactas.

- [ ] Criar testes de CNPJ numérico/alfanumérico, variável ausente, URL inválida e mesma empresa em tenants A/B; confirmar falha da capacidade nova antes da implementação.
- [ ] Implementar regras a partir de `entregas/emergent-prospeccao-v1/backend/ebt_prospecting/domain.py`, com limites de catálogo de 1000 linhas por requisição, lote 1–100 e intervalo 1–720h.
- [ ] Acrescentar modelo, índices tenant/CNPJ e tenant/chave de operação, FKs e versionamento; gerar migration e acrescentar predicados RLS antes de ativar tabelas.
- [ ] Criar banco local exclusivo `EbtPlatformQa_Prospecting_*`, aplicar migration e executar `python tests/integration/prospecting_qa.py --scenario schema`; exigir negativas A/B por SQL e HTTP, sem alterar o banco compartilhado.
- [ ] Revisar diff/hash e registrar checkpoint isolado dos arquivos desta tarefa.

### Tarefa 2 — catálogo, CRM e consulta

**Interfaces:** `ProspectingCrm.Visible(PlatformDb db, AccessScope access): IQueryable<Contact>` usa a política existente. `FromCatalog(PlatformDb db, AccessScope access, CatalogBusiness row, Guid ownerId): Task<Contact>` resolve Organization e Contact estáveis. `View(Contact contact, PlatformDb db): Task<ProspectContactDto>` retorna dados e metadados permitidos.

- [ ] Criar cenários `catalog_preview_confirm_repeat`, `canonical_contact_history_task`, `portfolio_duplicate_private` e `csv_formula`; observar falha nos endpoints novos.
- [ ] Implementar `/catalog/preview`, `/catalog/{id}/confirm`, `/contacts`, `/contacts/{id}`, `/contacts/{id}/metadata`, `/contacts/export.csv` e `/contacts/{id}/suppress`, com fonte/data, paginação e autorização.
- [ ] Persistir os vínculos no mesmo CRM; nenhuma atualização silenciosa de nome/e-mail/carteira em registro existente. Escrever eventos de revisão e supressão em Interaction.
- [ ] Executar `python tests/integration/prospecting_qa.py --scenario crm`; exigir importação idempotente, mesmo ID após reload e negativas de perfil/carteira/tenant/exportação.
- [ ] Revisar diff/hash e registrar checkpoint.

### Tarefa 3 — templates, prévia e aprovação

**Interfaces:** `Preview(PlatformDb db, AccessScope access, Guid contactId, Guid templateId, string sender): Task<ProspectPreview>` produz assunto/corpo/destinatário, versões e digest. `Schedule(..., ProspectScheduleCommand command): Task<ProspectOperation>` valida digest e grava snapshot aprovado, ator, dueAt, modo e chave da operação.

- [ ] Criar cenários `template_version_render`, `preview_missing_variable`, `changed_contact_rejects_digest`, `changed_template_rejects_digest` e `schedule_idempotency`.
- [ ] Implementar `/templates`, edição/versionamento com If-Match, `/contacts/{id}/preview`, `/contacts/{id}/schedule`, `/operations` e cancelamento; corpo máx. 8000, assunto máx. 200, agendamento UTC persistido e apresentação em São Paulo.
- [ ] Implementar `/contacts/{id}/whatsapp-manual`: validar digest/telefone, retornar link e registrar preparação; nunca registrar envio ou entrega pelo clique.
- [ ] Executar `python tests/integration/prospecting_qa.py --scenario approval`; exigir todos os casos e rejeição de leitor/CSRF/ID de outro tenant.
- [ ] Revisar diff/hash e registrar checkpoint.

### Tarefa 4 — receitas e worker persistente

**Interfaces:** `ProspectingWorker.ProcessRecipe(CancellationToken ct): Task<bool>` e `ProcessOperation(CancellationToken ct): Task<bool>` usam scope por unidade de trabalho. `/recipes` produz receita com version/state/cursor/nextRunAt; operações de run/pause exigem versão e permissão da carteira.

- [ ] Criar cenários `two_workers_one_batch`, `monthly_budget_concurrent`, `pause_restart_cursor` e `month_rollover`; reservar consumo real antes de promover contatos.
- [ ] Implementar receitas, execução imediata, pausa, leases/fencing, agenda, cursor determinístico e contadores; conferir usuário/tenant/carteira ativos antes do lote.
- [ ] Registrar worker uma vez em Program.cs; manter o worker atual de conversas e suas filas independentes por tipo de operação, sem duplicar envio.
- [ ] Executar `python tests/integration/prospecting_qa.py --scenario worker`; exigir concorrência e reinício no SQL local real, sem aplicar uma migration ao ambiente online.
- [ ] Revisar diff/hash e registrar checkpoint.

### Tarefa 5 — Outlook automático e fila durável

**Interfaces:** `ProspectingOutlook.Status(ChannelConnection connection): OutlookStatusDto`, `CreateDraft(ProspectOperation operation, CancellationToken ct): Task<GraphDraftResult>`, `SendDraft(string immutableId, CancellationToken ct): Task<GraphSendResult>`, `Reconcile(string immutableId, CancellationToken ct): Task<GraphEvidence>`.

- [ ] Criar cenários `complete_credential_set_only`, `draft_id_persisted_before_send`, `graph_202_is_accepted`, `crash_after_accept_no_resend`, `sent_items_reconciliation` e `suppression_before_dispatch`; usar servidor HTTP sintético, sem e-mail real.
- [ ] Implementar cliente Graph application e referência de configuração por conexão; adaptar conjunto completo GRAPH_* ou MS_*/AZURE_* sem misturar aplicativos. Atualizar `.env.example` somente com placeholders e comentário dos conjuntos.
- [ ] Integrar estados da fila ao worker: snapshot, aprovação, conexão, supressão e versão conferidos antes da operação; persistir ID/estado de tentativa antes do efeito externo. Lease vencido não autoriza reenvio ambíguo.
- [ ] Implementar status/conexão/desconexão administrativa e exportação de evidência sanitizada. Preservar delegated opcional com cache protegido e estado de uso único, sem mudar login EBT.
- [ ] Executar `python tests/integration/prospecting_qa.py --scenario outlook`; prova real permanece pendente de teste controlado autorizado.
- [ ] Revisar diff/hash e registrar checkpoint.

### Tarefa 6 — Meta, canais existentes e custos

**Interfaces:** `ProspectingMeta.Enqueue(..., MetaTemplateCommand command): Task<ProspectOperation>` congela template/idioma/parâmetros/opt-in. `ProcessEvent(...): Task` vincula evento à operação por conexão/ID e não altera outro tenant. `/costs` retorna parâmetros de cálculo e consumo separado de fatura real.

- [ ] Criar cenários `manual_link_is_prepared`, `meta_optin_required`, `meta_budget_two_operations`, `signed_event_duplicate_out_of_order` e `wazvox_reply_regression`.
- [ ] Implementar template oficial no conector desativado por padrão, reaproveitando canais/WebhookReceipt protegidos e verificando HMAC sobre corpo bruto. Deduplicar ID do provedor e manter estados monótonos onde o contrato permitir.
- [ ] Implementar parâmetros de custo, orçamento atômico e consulta de limites; apresentar tarifa informada como simulação e não como preço universal.
- [ ] Executar `python tests/integration/prospecting_qa.py --scenario channels` e os testes atuais de protocolo WazVox afetados; exigir preservação das conversas atuais.
- [ ] Revisar diff/hash e registrar checkpoint.

### Tarefa 7 — integração completa do frontend

**Interfaces:** `ProspectingPage({ me: Me, onOpenContact: (id: string) => void }): ReactNode` usa exclusivamente o cliente HTTP atual e o prefixo novo. A aba Contatos chama o callback com ID canônico. Troca de empresa/carteira remonta/limpa o módulo e descarta resposta antiga.

- [ ] Acrescentar DTOs/adaptadores tipados e as seis abas. Aproveitar textos e fluxos do componente recuperado, preservando a marca e os componentes atuais da EBT. Não montar App.js nem substituir o login da prévia.
- [ ] Implementar loading/vazio/erro, filtros/paginação, catálogo preview/confirm, revisão/links, template versionado e prévia, receitas, agendamento, conexões, evidências e custos, com controles por perfil.
- [ ] Acrescentar Prospecção à navegação de App.tsx e abertura do mesmo contato em Relacionamentos; manter seleção, formulário e estado incerto de ação no erro.
- [ ] Reproduzir e corrigir o cenário de navegação da página atual durante carga, com teste determinístico `navigation_current_view_pending_request` em `e2e/navigation.spec.ts`.
- [ ] Executar `npm run build`, `npx playwright test e2e/prospecting.spec.ts e2e/navigation.spec.ts` e regressões existentes diretamente afetadas; exigir criação/receita → mesmo contato CRM → histórico/tarefa → prévia/fila → reload.
- [ ] Inspecionar login e todas as telas em 320/390/768/1366px; salvar capturas versionadas e verificar foco, legibilidade, ausência de overflow de página e erros de console.
- [ ] Revisar diff/hash e registrar checkpoint.

### Tarefa 8 — candidato local e passagem

- [ ] Executar uma regressão integrada de segurança, cadastro/tarefas, conversas, documentos e prospecção no SQL sintético. Repetir apenas recortes afetados por nova falha/correção.
- [ ] Ensaiar backup/restore das novas entidades, validar hashes e migration idempotente, preservar dados e fontes anteriores.
- [ ] Gerar `evidencias/prospecting_connect_local.json`, manifesto de fontes/build, resultados/ambiente, limitações e instrução local de configuração/rollback em TXT.
- [ ] Atualizar somente status comprovados; separar frontend restaurado, integração local, QA sintético, autenticação real, envio aceito/confirmado/entregue e publicação.
- [ ] Fazer revisão final independente do diff desta integração conforme o método escolhido. Não publicar ou migrar ambiente online sem candidato validado e autorização específica existente.

## Handoff de execução

Recomendação: execução nativa neste chat, porque as tarefas dependem fortemente dos mesmos contratos de identidade e fila. O usuário pode escolher execução com subagentes se preferir. A revisão deste plano e a escolha são o último gate de planejamento exigido pela skill aplicada antes da adaptação funcional.
