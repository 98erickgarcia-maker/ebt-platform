# PAC-06 — plano de implementação e verificação

Data: 07/10/2026. Estado: preparação iniciada; funcionalidades ainda não implementadas neste pacote.

## Fonte e limites

- Repositório: https://github.com/98erickgarcia-maker/ebt-platform.
- Base: PR #6, branch `feat/pac-05-identity-tenant-scope-v2-20261007`, commit `e84ad5e8def9b8b3001475cda6fcf73610a17804`.
- Código funcional anterior: `f9492219407707e23ff7611c58e69ec4726e8dac`. CI documental `37697473803`, fundação `37697473804` e SQL/Blob `37697473874`: sucesso confirmado via API do GitHub. Provas anteriores não certificam as novas fronteiras do PAC-06.
- Implementação isolada em `codex/pac06-sql-rls-resource-cache`, com PR a empilhar sobre a branch do PR #6. Não mesclar os PRs anteriores nem alterar os projetos-fonte.
- Manter 12h estimadas do pacote, 180h de entregas e 20h de reserva. Horas estimadas não representam horas já executadas.
- Não alterar CASST, ativar integrações externas nem implantar em produção. Massa e credenciais exclusivamente sintéticas de QA.
- G-SEG permanece aberto até PAC-07 e suas provas.

## Decisões propostas para o recorte

### P04-05 — migrations e índices (N)

Versionar o schema atual e a evolução do recorte com EF Core migrations. A inicialização de QA passa de `EnsureCreated` para migrations controladas. Cobrir banco vazio e o schema sintético anterior criado por `EnsureCreated`, sem apagar registros/anexos ou reescrever histórico de migrations. A adoção do schema anterior exige preflight de compatibilidade; divergência deve interromper a migração com diagnóstico seguro.

Identidade de registro composta por tenant e ID; índices de listagem incluem tenant, escopo do responsável e ordenação. Não transformar título em unicidade de negócio. Provar duplicidade do identificador negada dentro do tenant e independência de IDs entre tenants.

### P04-06 — SQL/RLS real (N)

Adicionar política SQL de filtro e bloqueio de escrita baseada em contexto de conexão confiável. Contexto ausente deve negar o acesso aos registros. O contexto é definido pelo servidor, nunca por headers recebidos. Contextos/repositórios não podem compartilhar tenant mutável entre requisições. Tratar abertura/reabertura da conexão, retries e reutilização do pool para não herdar contexto do consumidor anterior.

Verificar consultas SQL diretas sem filtro LINQ, leitura cruzada, insert/update indevidos e alternância A/B em conexão reutilizada. Falha de preparação do SQL não conta como proteção funcionando. A prova precisa usar SQL Server e Blob/Azurite reais de QA.

### P04-07 — autorização por recurso (N)

Persistir responsável derivado da identidade confiável do servidor, sem aceitar proprietário indicado pelo cliente. Administrador acessa os registros da sua empresa; operador acessa sua carteira; Consulta mantém leitura autorizada pela política documentada e não escreve; Suporte não acessa registros comerciais. Registros anteriores sem responsável não devem ser atribuídos arbitrariamente a um operador.

Aplicar a mesma política a leitura por ID, listagem, download e exportação do recorte. Retornar 404 para recurso fora do escopo, evitando revelar sua existência. Garantir autorização antes de obter bytes do Blob. Exportação não pode ampliar o conjunto autorizado da listagem.

### P04-08 — sessão/cache/troca de perfil (R2, promover para N se necessário)

Respostas privadas de autenticação e registros não devem ser armazenadas em caches HTTP compartilhados. Caso haja cache de aplicação, sua chave inclui tenant, usuário e perfil. No cliente HTTP, invalidar estado e cancelar/descartar respostas de uma geração anterior ao logout ou mudança de identidade/perfil. Expiração/401 deve limpar o estado privado.

O frontend atual ainda contém telas sintéticas independentes da API autenticada. Integrar o fluxo de sessão do recorte sem apresentar dados de demonstração como registros privados persistidos; documentar limites e cobrir troca de usuário em testes.

## Ordem de execução

1. Reproduzir a base isolada: restore e testes backend pertinentes, instalação pelo lockfile e testes frontend. Excluir a categoria SQL real do teste local sem fixture, evitando apresentar retorno antecipado como prova de SQL.
2. Escrever cenários negativos e observar falha pertinente antes de implementar cada fronteira.
3. Implementar migrations/índices, provar subida e evolução do snapshot sintético.
4. Implementar contexto SQL e RLS com testes reais de filtro, bloqueio e pool.
5. Implementar política por recurso e verificar carteira/ID/download/exportação.
6. Implementar invalidação de sessão/cache e testes de respostas atrasadas, logout e troca de perfil.
7. Revisar o diff; corrigir achados; executar backend/frontend, lint, builds e auditorias pertinentes. Executar CI de SQL/Blob real para a versão final.
8. Registrar evidências dos cenários P04-05 a P04-08 com versão, ambiente, comandos, observado e limites. Atualizar estados apenas com a prova correspondente; abrir PR empilhado e conferir SHA remoto.

## Matriz mínima de provas novas

| Fronteira | Prova obrigatória |
|---|---|
| Migration | Banco vazio; snapshot sintético anterior com registro e metadados de anexo preservados; reexecução sem duplicar história |
| Índices | Identificador duplicado no mesmo tenant recusado; mesmo identificador A/B independente |
| RLS | SQL sem filtro não revela B; contexto ausente nega; insert/update cruzados recusados; pool A/B não herda contexto |
| Recurso | ID de outra empresa 404; operador sem carteira 404; download não consulta bytes sem autorização; exportação limitada |
| Cache/sessão | no-store privado; logout limpa estado; A/B e perfis não reutilizam dados; resposta antiga descartada; 401 invalida |
| Regressão | Casos PAC-05 continuam passando; SQL/Blob real identificado; G-SEG continua aberto |

Este documento registra plano e preparação, não aceite dos tickets nem conclusão do PAC-06.
