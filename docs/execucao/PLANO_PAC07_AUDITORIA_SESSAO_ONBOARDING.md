# PAC-07 — plano de auditoria, sessão e onboarding

Data: 07/10/2026. **Planejamento detalhado; nenhuma funcionalidade deste pacote foi implementada ou demonstrada nesta entrega. G-SEG permanece aberto.**

**Objetivo:** preparar auditoria mínima persistida, revogação de sessão, proteção CSRF e ativação de convite no recorte sintético EBT, com provas integradas Orbe/Nexo.

**Arquitetura:** manter .NET/React/SQL Server e Blob/Azurite existentes. Evoluir o schema por nova migration; usar identidade e tenant resolvidos pelo servidor. O onboarding fica em rotas próprias e não transforma o login ilustrativo em autenticação operacional.

**Stack:** .NET 10, EF Core/SQL Server, ASP.NET Core Cookie Authentication/Antiforgery, React/TypeScript/Vite, Vitest e Chromium E2E a incorporar pelo lockfile na execução.

**Especificação:** [PAC-07](pacotes/PAC-07.md), [P04-09](entregas/P04-09.md), [P04-10](entregas/P04-10.md), [P04-11](entregas/P04-11.md), [P04-12](entregas/P04-12.md). Aplicar [revisão das bases](../REVISAO_BASES.md) e [gates](../VALIDACAO_E_GATES.md).

## Base e capacidade preservadas

- [GitHub confirmado da EBT Platform](https://github.com/98erickgarcia-maker/ebt-platform).
- [PR #7 — PAC-06](https://github.com/98erickgarcia-maker/ebt-platform/pull/7): aberto, rascunho, sem merge; head `900cac70c3e9323e50d61ef0aa3c7d75b0ca9112`, branch `codex/pac06-sql-rls-resource-cache`, consultados nesta entrega.
- CIs da mesma versão, confirmados como sucesso: [fundação 37702169147](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37702169147), [SQL/Blob 37702169126](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37702169126), [planejamento 37702169131](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37702169131). São provas da base, não do PAC-07.
- [Registro anterior](../../evidencias/execucao/PAC-06/registro.md): permite localizar os cenários já demonstrados. Qualquer alteração de segurança/schema exige nova prova pertinente.
- PAC-07: **12h estimadas**, 8h implementação + 3h verificação/revisão + 1h registro, janela 64–76h. Preservar **180h de entregas + 20h de reserva**; não registrar estimativa como hora real.
- P04-09/P04-10 passam de R2 inicial para **N planejada**, porque introduzem novas fronteiras de persistência e segurança. P04-11/P04-12 mantêm N.
- Não alterar projetos CASST/Vikings, copiar bancos/credenciais reais, mesclar PRs anteriores ou publicar em produção. Este plano não executa as instruções do PDF de referência.
- Não criar registros de resultado P04-09 a P04-12 nem marcar casos como aprovados antes das execuções correspondentes.

## Achados estáticos que orientam as tarefas

1. `AuthEndpoints.cs` encerra a sessão com `SignOutAsync` e remoção do cookie. Não há registro de revogação no servidor nesta base. A execução deverá reproduzir a reutilização de uma cópia do cookie antes de implementar a correção; o presente exame não é essa prova dinâmica.
2. `Program.cs`/`AuthEndpoints.cs` não apresentam validação Antiforgery para os POSTs autenticados. A estratégia atual usa cookies; especificar proteção também para login e ativação.
3. `EbtSessionClaims.IsSessionCurrent` converte um `long` em `DateTimeOffset` sem validar os limites da representação. Testar claim fora do intervalo e rejeitar com segurança, sem erro 500.
4. O modelo SQL atual contém `FoundationRecords`; os campos de auditoria, convite, aceite e revogação abaixo são capacidades futuras. Os logs de diagnóstico atuais não substituem um evento de negócio persistido.
5. O proxy Vite aponta para a porta 5000, enquanto o smoke de API do CI QA usa 5080. Unificar o alvo na execução antes de atribuir falha de jornada ao onboarding.

## Contratos propostos, ainda não disponíveis

| Operação HTTP | Acesso e resultado planejados |
|---|---|
| `GET /api/auth/csrf` | Emite token de requisição associado ao cookie Antiforgery; sem cache. Não estabelece sessão de usuário. |
| `POST /api/auth/qa-login` | Preservar restrição QA/Development e código sintético; adicionar CSRF e sessão revogável. |
| `POST /api/auth/logout` | Identidade autenticada + CSRF; revogar no SQL antes de expirar o cookie. |
| `GET /api/auth/me` | Retornar apenas identidade validada no servidor; sessão revogada/expirada responde 401. |
| `POST /api/onboarding/invitations` | Administrador do tenant atual + CSRF; aceitar e-mail sintético, nome e perfil Operator/ReadOnly; tenant exclusivamente do servidor. Responder 201 com URL de ativação de QA. |
| `POST /api/onboarding/activate` | Anônimo + CSRF; convite válido e não consumido, termo aceito e senha válida. Confirmar persistência antes de emitir sessão e `nextPath=/seguranca-qa`. |
| `POST /api/auth/login` | Apenas QA/Development; seleção de tenant, e-mail e senha para contas ativadas. O cadastro do servidor determina tenant/perfil; erro genérico 401. |
| `GET /api/foundation/audit` | Administrador do tenant atual; lista mínima ordenada, limitada a 100 eventos, sem payload sensível. Outros perfis: 403. |

Usar cabeçalho `X-EBT-CSRF` para mutações. Token ausente, inválido ou associado a outra identidade: 400, sem escrita e sem sessão nova. Renovar token após autenticação, ativação ou troca de identidade. Manter 401/403/404 das políticas de recurso existentes. Falha do provedor não pode ser tratada como autorização concedida.

URLs de convite: `/ativar#token=<valor>`, para evitar enviar o segredo na URL HTTP ao servidor. Remover o fragmento após conclusão; não registrar token, senha, cookie, request body ou URL de convite em logs, traces ou evidências. O retorno do token é restrito ao administrador de QA; não haverá envio de e-mail nesta etapa.

## Foco da revisão e provas correspondentes

| Condição | Comportamento exigido | Tarefa |
|---|---|---|
| Duas ativações concorrentes do mesmo convite | Exatamente uma consome o token e cria a conta; outra recusada | 3 |
| Cookie copiado antes do logout; sessão muda durante uma resposta lenta | Cópia negada no servidor; resposta anterior descartada no cliente | 2/4 |
| Expiração malformada ou fora do intervalo | Negativa segura sem exceção exposta | 2 |
| Falha após upload ou durante transação SQL | Não gravar evento de sucesso isolado; preservar compensação de Blob | 1 |
| Navegação após termo/senha depende de estado desatualizado | Destino só depois de ativação confirmada e identidade reconsultada | 3/4 |

## Tarefa 1 — P04-09: evento mínimo na transação SQL (3h)

**Arquivos existentes a alterar:** `src/backend/Ebt.Application/Foundation/FoundationPersistenceContracts.cs`, `src/backend/Ebt.Infrastructure/Persistence/SqlFoundationRecordRepository.cs`, `src/backend/Ebt.Infrastructure/Persistence/EbtDataContext.cs`, `src/backend/Ebt.Api/FoundationRecordEndpoints.cs` e snapshot de migrations.

**Arquivos a criar:** `src/backend/Ebt.Application/Security/EbtAuditContracts.cs`, `src/backend/Ebt.Infrastructure/Persistence/SqlAuditReader.cs`, migration adicional de auditoria e `tests/Ebt.Foundation.Tests/Pac07AuditIntegrationTests.cs`. Nomes/IDs cronológicos de migration devem ser gerados na execução; não reescrever as três migrations anteriores.

**Interfaces futuras:** `EbtAuditContext(Guid ActorUserId, string TenantKey, string CorrelationId)`; `SaveForIdentityAsync(FoundationRecordDraft draft, EbtIdentityProfile identity, string correlationId, CancellationToken cancellationToken = default)`; `IFoundationRecordRepository.AddAsync(FoundationStoredRecord record, EbtAuditContext audit, CancellationToken cancellationToken = default)`; `IEbtAuditReader.ListAsync(string tenantKey, int limit, CancellationToken cancellationToken)` retornando `IReadOnlyList<EbtAuditEntry>`.

`EbtAuditEntry`: ID, ActorUserId, TenantKey, UTC, operação fixa (`foundation.record.created`, `onboarding.invitation.created`, `onboarding.activated`), ResourceId e correlação gerada pelo servidor. Nenhum título, e-mail, nome de arquivo, conteúdo anterior/posterior, senha ou token. Chave composta tenant/ID e índice tenant/UTC/ID; filtro e bloqueio RLS para a nova tabela.

- [ ] Criar testes SQL que falhem antes da implementação: gravação confirmada produz exatamente um evento com ator/tenant/correlação corretos; falha de gravação não produz evento; busca do tenant B não lê evento A; payload sensível não é coluna nem conteúdo do evento.
- [ ] Executar `dotnet test EBT.Platform.sln --filter FullyQualifiedName~Pac07AuditIntegrationTests` com `EBT_QA_E2E=1` e SQL/Azurite sintéticos prontos; registrar falha da regra, distinguindo erro de infraestrutura.
- [ ] Persistir registro e evento no mesmo `SaveChanges`/transação. Passar correlação de `SafeDiagnostics` e identidade confiável da API. Chamadas internas sem ator humano deverão declarar ator de sistema sintético, sem inventar autoria.
- [ ] Preservar a compensação do Blob quando SQL falha; testar essa falha. Para convite/ativação, usar os mesmos campos mínimos dentro das respectivas transações da tarefa 3.
- [ ] Reexecutar os casos, conferir migrations/snapshot sem diferenças pendentes e fazer commit somente dos arquivos da tarefa.

## Tarefa 2 — P04-10: revogação, CSRF e negativas (3h)

**Alterar:** `src/backend/Ebt.Api/Security/EbtAuthentication.cs`, `AuthEndpoints.cs`, `src/backend/Ebt.Api/Program.cs`, `src/backend/Ebt.Application/Security/EbtSecurity.cs`, `src/frontend/src/api/http.ts`, `session.ts` e testes existentes de autenticação/sessão.

**Criar:** `src/backend/Ebt.Application/Security/EbtSessionContracts.cs`, `src/backend/Ebt.Infrastructure/Security/SqlSessionRegistry.cs`, migration de sessões e `tests/Ebt.Foundation.Tests/Pac07SessionTests.cs`/`Pac07SessionIntegrationTests.cs`.

**Interfaces futuras:** `EbtSessionRecord(Guid SessionId, Guid UserId, DateTimeOffset ExpiresUtc, DateTimeOffset? RevokedUtc)`; `IEbtSessionRegistry.CreateAsync(EbtSessionRecord session, CancellationToken ct)`, `FindCurrentAsync(Guid sessionId, Guid userId, DateTimeOffset now, CancellationToken ct)` retornando `EbtSessionRecord?`, `RevokeAsync(Guid sessionId, Guid userId, DateTimeOffset now, CancellationToken ct)`. Sessões persistidas no SQL de QA; um fake de teste não fecha o critério de revogação real.

- [ ] Reproduzir POST sem/contra token e cópia de cookie após logout com testes negativos; observar falha na base. Adicionar expirado, claim numérica extrema e usuário desativado.
- [ ] Implementar `OnValidatePrincipal` consultando registro de sessão e identidade atual do servidor. Sessão inexistente, expirada, revogada ou usuário inativo: rejeitar principal. Resolver o TenantContext apenas dessa identidade validada; nunca de tenant/role enviado pelo cliente.
- [ ] Criar sessão persistida antes de emitir cookie; revogar antes de logout. Manter duração absoluta 30 minutos, sem sliding, HttpOnly e SameSite Strict; Secure sempre em Production, política compatível com HTTP local apenas em QA/Development. Não liberar o login sintético em Production.
- [ ] Implementar Antiforgery do ASP.NET Core e validação explícita em todas as mutações dos grupos `/api/auth`, `/api/foundation` e `/api/onboarding`. Provar token sem cookie e token de identidade anterior negados. Garantir no-store inclusive em erros.
- [ ] Atualizar cliente HTTP, fila serial de autenticação, mocks, fábricas de testes existentes e smoke de CI para obter/enviar CSRF. Não adicionar bypass de CSRF aos testes positivos. Não abortar mutações de cookie nem permitir que refresh suprima logout já enfileirado.
- [ ] Conferir `X-Content-Type-Options: nosniff`, proteção contra frame e Referrer-Policy sem referência; inspecionar cookies e negativas de Production em teste isolado, sem implantar.
- [ ] Executar `dotnet test EBT.Platform.sln --filter FullyQualifiedName~Pac07Session` e `npm.cmd test -- --run src/api/session.test.ts src/api/http.test.ts`; exigir casos SQL reais além dos testes de política. Fazer commit da tarefa.

Bootstrap de autenticação: a busca por SessionId/UserId deve funcionar antes de conhecer o tenant. Tabelas globais de sessão/identidade não terão um endpoint de consulta livre; o serviço interno vincula os dois IDs e carrega o tenant do cadastro confiável. Convites e auditoria permanecem escopados por tenant/RLS. Provar que o cliente não consegue escolher outro usuário ou tenant por payload/header.

## Tarefa 3 — P04-11: ativação confirmada e próxima tela (3h)

**Alterar:** contexto SQL/snapshot/registro de serviços, endpoints de autenticação, `src/frontend/src/App.tsx`, `src/frontend/src/pages/SecurityQaPage.tsx` e API de sessão.

**Criar:** `src/backend/Ebt.Application/Security/EbtOnboardingContracts.cs`, `src/backend/Ebt.Infrastructure/Security/SqlOnboardingService.cs`, `src/backend/Ebt.Api/Security/OnboardingEndpoints.cs`, migration de contas/convites, `src/frontend/src/pages/ActivationPage.tsx`, `PasswordLoginPage.tsx`, seus testes e `tests/Ebt.Foundation.Tests/Pac07OnboardingIntegrationTests.cs`.

**Interfaces futuras:** `CreateInvitationRequest(string Email, string DisplayName, EbtRole Role)`; `ActivationRequest(string Token, string Password, bool AcceptTerms)`; `InvitationIssued(Guid InvitationId, string Token, DateTimeOffset ExpiresUtc)`; `ActivationConfirmed(EbtIdentityProfile Identity, string NextPath)`; `IEbtOnboardingService.CreateAsync(CreateInvitationRequest request, EbtIdentityProfile actor, string correlationId, CancellationToken ct)` e `ActivateAsync(ActivationRequest request, string correlationId, CancellationToken ct)` retornando os respectivos tipos. Erro público de convite uniforme, sem revelar cadastro/tenant.

- [ ] Testar previamente convite inválido, expirado, consumido, sem aceite, senha fora do intervalo e corrida de consumo. Token inválido/reutilizado: 400, nenhuma conta/sessão adicional; cadastro duplicado do mesmo tenant não cria outra conta.
- [ ] Restringir emissão ao Administrador e perfis convidados Operator/ReadOnly. E-mail exclusivamente `@demo.invalid`, nome 1–120 caracteres, validade 24h, token criptograficamente aleatório de 32 bytes; guardar apenas hash SHA-256 do token. Tenant e perfil vêm do convite persistido, sem campos de autoridade no payload de ativação.
- [ ] Registrar aceite UTC e versão de termo sintético `qa-2026-10`; senha 12–128 caracteres, armazenada pelo `PasswordHasher<TUser>` do framework, sem hash caseiro. Aplicar limitação de 5 tentativas/60 segundos por IP às operações públicas de login/ativação, sem confiar em forwarded headers externos; excesso responde 429. Testar a sexta tentativa, sem registrar IP em auditoria de negócio. Não apresentar o termo de QA como instrumento jurídico de produção.
- [ ] Consumir convite, criar conta e registrar auditoria em transação SQL atômica, com concorrência protegida. Se houver retry EF, executar a transação completa pela execution strategy, sem duplicar emissão de cookie/token.
- [ ] Emitir sessão somente depois do commit. Frontend aguarda ativação, reconsulta `/api/auth/me` e só então navega com replace para `/seguranca-qa`; limpa fragmento e estado de senha. Ao falhar, permanece na ativação com erro seguro.
- [ ] Criar `/acesso` para reentrada com senha; manter `/login` ilustrativo identificado. Convite é exibido apenas no painel de QA, sem envio externo e sem copiar segredo para relatório.
- [ ] Executar testes SQL e frontend de ativação/navegação; incluir perfil persistido após reload/logout/login. Fazer commit. O aceite E2E completo depende da tarefa 4.

A pendência histórica CASST precisa ser relacionada ao mecanismo de navegação/estado que for reproduzido no recorte EBT. Documentar cenário esperado, falha observada e produtor corrigido. Uma nova tela verde da EBT, isoladamente, não comprova correção do defeito CASST; se não houver reprodução equivalente ou evidência suficiente, manter esse aceite específico pendente, sem fechar G-SEG integral.

Persistir contas com ID gerado no servidor, tenant, e-mail normalizado, nome, perfil, hash de senha, estado ativo e aceite UTC/versão. Unicidade de tenant/e-mail normalizado. Convites: ID, tenant, e-mail/perfil/nome de destino, hash do token, expiração e consumo UTC; negar reutilização mesmo sob concorrência. Atualizar implementações/fakes de contratos alterados e testes de migrations existentes sem remover suas negativas.

## Tarefa 4 — P04-12: matriz SQL/navegador e decisão de gate (3h)

**Alterar:** `.github/workflows/validar-qa-persistencia.yml`, `src/frontend/package.json`/lockfile, `vitest.config.ts` e configuração do alvo HTTP de QA.

**Criar:** `src/frontend/playwright.config.ts`, `src/frontend/e2e/pac07-security.spec.ts`, `scripts/qa_security_smoke.py` e registros sanitizados somente após execução. Playwright deve ser escolhido na execução em versão compatível, travado no lockfile; não instalar dependência neste planejamento.

- [ ] Preservar SQL Server/Azurite reais e negativos PAC-05/PAC-06. Separar testes Vitest (`src/**/*.test.{ts,tsx}`) dos E2E; manter pool forks no Windows conforme correção anterior.
- [ ] Unificar API/proxy/smoke: backend 5080 e proxy frontend com alvo explícito `http://127.0.0.1:5080` apenas no QA do CI; padrão local 5000 preservado. Aguardar health de infraestrutura, sem aumentar timeout da ativação para esconder defeito.
- [ ] Adicionar gatilho do CI QA para alterações frontend e scripts de smoke; iniciar frontend e executar Chromium com timeout de jornada 30s, workers=1 e retries=0. Evitar traces/snapshots que capturem token, senha ou headers; relatórios devem conter nomes/resultados/correlação sanitizada.
- [ ] Executar navegador real: administrador Orbe cria convite; convidado aceita termo/senha, chega à tela prevista, grava/recarrega conforme perfil; logout e login Nexo não mostram registro Orbe. Reutilização/invalidez do convite falham sem criar segunda sessão.
- [ ] Reconciliar navegador e SQL: acesso direto por ID/download/exportação, escrita proibida de Consulta, carteira do Operador, ausência de acesso comercial de Suporte, headers falsos ignorados, cookie revogado 401, evento mínimo RLS, conexões A/B e ausência de contexto negadas. Verificar tanto resposta quanto ausência de escrita/evento proibidos.
- [ ] Incluir decisão de gate que recebe resultados dos casos exigidos e nega avanço se qualquer caso obrigatório falhar, não executar ou tiver provedor substituído. Provar a negativa com um resultado de vazamento marcado como falha, sem executar vazamento em produção.
- [ ] Rodar uma regressão integrada de backend/frontend, lint/build/auditorias e CI SQL/navegador na mesma versão. Rever diff antes de abrir PR empilhado sobre a branch do PR #7; anexar URL e verificar SHA remoto. Não mesclar automaticamente.
- [ ] Registrar versão, ambiente sintético, identificador do banco `EbtQa_*`, comandos, casos, esperado/observado e limites. Atualizar estado individual apenas com a prova indicada; homologação e produção continuam separadas.

**Comandos futuros**, na raiz ou frontend conforme indicado:

```powershell
dotnet restore EBT.Platform.sln
dotnet build EBT.Platform.sln --no-restore
dotnet test EBT.Platform.sln --no-build --filter "Category!=QaPersistence"
# Somente com fixtures SQL/Azurite reais e EBT_QA_E2E=1:
dotnet test EBT.Platform.sln --no-build --filter "Category=QaPersistence"
# Em src/frontend, com API/QA prontas para o E2E:
npm.cmd ci --ignore-scripts
npm.cmd test -- --run
npm.cmd run lint
npm.cmd run build
npx.cmd playwright test --project=chromium
```

Teste SQL ignorado/skip não prova provedor real. CI verde da base ou do planejamento não demonstra os novos casos. Os comandos E2E só estarão disponíveis após a tarefa 4.

## Critério de encerramento e corte

Os 12 casos originais permanecem **não executados** no [controle estruturado deste plano](../../planejamento/plano_pac07.json). Na futura execução, P04-09 exige evento confirmado/erro/minimização; P04-10 exige CSRF/revogação/headers; P04-11 exige jornada equivalente reproduzida e corrigida, inválido/reuso e correção sem timeout ampliado; P04-12 exige permitido/proibido, bloqueio por vazamento e banco real identificado.

Fechar G-SEG somente quando todas as provas aplicáveis forem demonstradas na versão identificada, inclusive o aceite de onboarding. Mesmo fechado no QA sintético, o gate não é homologação operacional, integração de fornecedor nem publicação. Se faltar prova, registrar precisamente o critério pendente e impedir consumidores dependentes; continuar apenas trabalho independente.

Cada 3h é um timebox, não garantia de terminar. Ao exceder, dividir subtarefas e registrar trabalho real; não consumir as 20h de reserva por inferência nem reduzir os negativos para caber. Persistência de conta, CSRF e E2E podem exigir reestimativa dentro do corte previsto nos gates. E-mail, Outlook, WhatsApp, campanhas e prospecção automática não são adicionados a estas 12h; têm o pacote separado já preparado para Emergent e dependem de escopo/homologação próprios.

## Texto de passagem para implementação futura

> Trabalhe exclusivamente no repositório EBT Platform indicado neste documento. Leia AGENTS.md, REVISAO_BASES.md, VALIDACAO_E_GATES.md e este plano. O estado atual é planejamento: só execute os módulos quando houver uma solicitação que altere expressamente esse escopo. Ao executar, parta da versão PAC-06 indicada, preserve a árvore local e use branch isolada. Implemente P04-09 a P04-12 em tarefas pequenas, com testes negativos antes da mudança, SQL Server/Azurite reais e Chromium no fechamento. Mantenha .NET/React/SQL e os contratos de isolamento; não reescreva a plataforma em outra stack. Não altere CASST nem ative conectores/envios/produção. Registre provas por SHA/cenário e mantenha G-SEG aberto enquanto faltar qualquer critério, especialmente a reprodução e correção do onboarding equivalente. Não apresente dependência instalada, tela demonstrativa, mock ou CI documental como módulo funcionando.

## Referências técnicas consultadas

O ASP.NET Core oferece validação do principal para reagir a mudanças no servidor; este plano a usa como ponto de validação da sessão persistida. [Documentação de Cookie Authentication](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie?view=aspnetcore-10.0).

A estratégia de CSRF segue emissão de tokens pelo Antiforgery e validação de requisições que usam cookies. [Documentação de Antiforgery](https://learn.microsoft.com/en-us/aspnet/core/security/anti-request-forgery?view=aspnetcore-10.0). Essas referências orientam o desenho e não substituem a prova no recorte.
