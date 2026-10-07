# PAC-06 — registro integrado

Data: 07/10/2026. Estado: **demonstrado em QA no recorte**. G-SEG aberto até PAC-07; sem homologação do usuário, merge ou implantação em produção.

## Versão e checkout

Repositório confirmado: https://github.com/98erickgarcia-maker/ebt-platform.

[PR #7](https://github.com/98erickgarcia-maker/ebt-platform/pull/7), branch `codex/pac06-sql-rls-resource-cache`, empilhado sobre `feat/pac-05-identity-tenant-scope-v2-20261007` do PR #6. Base `e84ad5e8def9b8b3001475cda6fcf73610a17804`; código funcional validado **`904a087edab46cb50d5eb787f17859af1ad83a79`**, confirmado também por `git ls-remote`. Commit posterior de documentos não amplia a prova funcional.

Worktree dedicado `pac06-isolamento/EBT PLATAFORM`; checkout original preservado. Nenhuma edição dos projetos CASST ou outros projetos-fonte. Foram mantidos os limites das 180h de entregas e 20h de reserva, sem contratar serviço.

## Rastreabilidade documental

Os JSONs originais de planejamento e o PDF preservam a baseline de 06/10; seus estados planejados não são o painel atual de execução. O estado comprovado deste pacote está no [overlay PAC-06](../../../planejamento/execucao_pac06.json) e nos registros por ticket. Os hashes do manifesto foram reconciliados somente para as fichas/índice/fase/pacote editados; orçamento, dependências e PDF foram preservados. O verificador documental passou a excluir dependências/builds gerados (`node_modules`, `bin`, `obj`, `dist`) da conferência de links.

## Resultado integrado e tickets

| Ticket | Resultado e estado | Prova |
|---|---|---|
| P04-05 | Migrations e índices por tenant; demonstrado em QA | [Registro](../P04-05/registro.md), vazio/legado, unicidade e drift |
| P04-06 | SQL/RLS real; demonstrado em QA | [Registro](../P04-06/registro.md), filtro, bloqueio e mesmo SPID no pool |
| P04-07 | Autorização por responsável; demonstrado em QA | [Registro](../P04-07/registro.md), ID, Blob, listagem e exportação |
| P04-08 | Sessão/estado privado; demonstrado em QA, trilha N | [Registro](../P04-08/registro.md), geração, logout e corrida de respostas |

P04-08 foi promovido de R2 para N por alterar uma fronteira de segurança/concorrência. Mantidas 3h estimadas do ticket e 12h do pacote; não adicionar a validação novamente às horas estimadas. Horas-pessoa reais não apontadas nesta sessão; nenhum consumo de reserva foi afirmado por inferência. Trabalho restante do pacote: homologação operacional/integrar a cadeia de PRs, não realizada nesta entrega.

## Comandos e evidência

Versão `904a087` em GitHub Actions, Ubuntu, SQL Server 2022 Developer e Azurite em containers efêmeros com imagens fixadas. Dados sintéticos Orbe/Nexo; fixture por teste com nome exclusivo.

- [Fundação 37701191579](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191579): `dotnet restore/build/test`, 23 casos backend aprovados; 5 SQL explicitamente skipped neste job sem fixture. `npm ci/test/lint/build/audit`: 28/28 frontend, lint/build aprovados e zero vulnerabilidades npm. Auditoria .NET sem pacotes vulneráveis nas fontes consultadas.
- [SQL/Blob 37701191593](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191593): `dotnet test --filter Category=QaPersistence`, **5/5 aprovados, 0 falhas, 0 skips**; API autenticada/health, salvar/reler/download e negativa Nexo também aprovados.
- [Planejamento 37701191611](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191611): sucesso.
- [Resumo sanitizado](ci-resumo.json). Logs brutos não foram copiados para o repositório.

Também executados localmente: 23/23 backend pertinentes, 28/28 frontend, lint, build e `git diff --check`. Ciclo negativo/positivo observado para chave tenant no modelo e política cache no cliente. Testes reais de SQL foram comprovados no CI, sem alegar fixture SQL local.

## Revisão e correções

Revisor independente `review_pac06`, somente análise estática, sem executar processos. Achados corrigidos antes da versão final funcional:

1. Baseline poderia adotar índice ausente/divergente: preflight ampliado e teste negativo observa SQL 51000, preservando registro e sem histórico de migration aplicado.
2. Fixtures tinham nomes fixos: GUID exclusivo por fixture, mantendo guardas de destino QA; execução não herda dados da tentativa anterior.
3. Refresh automático poderia descartar logout enfileirado: fila executa todas as operações de cookie; geração controla apenas publicação. Teste comprova `/me` lento -> POST logout -> novo `/me` anônimo.

Revisão final não identificou impedimento concreto no recorte examinado. Isso não é garantia universal de ausência de falhas.

Durante a validação local, timeout de worker threads no Windows impediu executar inicialmente todos os testes; forks completou a suíte, sem declarar a tentativa parcial aprovada. Uma alteração de codificação foi corrigida e a regressão de textos/rotas passou na versão final. Codex Process Jobs não suporta win32 nesta instalação; a tentativa falhou antes de lançar o job e os testes foram executados pelo terminal.

## Limites e próximo passo

- Recorte FoundationRecords sintético: carteira por responsável, sem delegação, edição ou exclusão via UI. Exportação limitada aos mesmos 100 registros da listagem.
- Migration anterior preserva registro/metadados SQL; não comprova restore operacional. QA usa principal administrativo sintético, sem afirmar segregação de privilégios de produção.
- `/seguranca-qa` usa identidade do servidor. Demais telas da fundação continuam ilustrativas. Login QA bloqueado em Production. Teste de componente não equivale a revisão visual online.
- [Guia e links GitHub](../../../docs/execucao/GUIA_PAC06_SQL_RECURSO_CACHE.md).
- Próximo: PAC-07 / P04-09, auditoria mínima do recorte. Depois cookies/tokens, onboarding negativo e demonstração integrada G-SEG A/B. O G-SEG permanece aberto até essas provas.
