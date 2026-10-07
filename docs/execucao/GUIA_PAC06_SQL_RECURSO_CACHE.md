# PAC-06 — SQL, recurso e sessão

Data: 07/10/2026. Recorte demonstrado em QA, sem publicação em produção. G-SEG permanece aberto até PAC-07.

## GitHub confirmado

- [Repositório EBT Platform](https://github.com/98erickgarcia-maker/ebt-platform).
- [PR #7 — PAC-06](https://github.com/98erickgarcia-maker/ebt-platform/pull/7).
- [Branch do PAC-06](https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/pac06-sql-rls-resource-cache).
- Base: [PR #6 — identidade e tenant](https://github.com/98erickgarcia-maker/ebt-platform/pull/6), sobre o caminho SQL/Blob do [PR #3](https://github.com/98erickgarcia-maker/ebt-platform/pull/3).

O PR é empilhado sobre a branch do PR #6. Revisar e integrar a cadeia na ordem; nenhum merge foi realizado nesta entrega.

## O que mudou

1. Três migrations versionadas: baseline compatível com o schema QA anterior, chave/índices por tenant e política RLS. Divergência de schema/índice interrompe a adoção; registros e metadados anteriores são preservados. Downgrade destrutivo não é executado automaticamente.
2. O SQL recebe contexto de tenant por conexão confiável, em chave somente leitura. Contexto ausente não lê registros. A política filtra linhas e bloqueia escrita cruzada; o pool não herda o tenant anterior.
3. A criação usa tenant e responsável da identidade do servidor. Operador acessa sua carteira; Administrador/Consulta leem sua empresa conforme permissões; Suporte não acessa registros comerciais. ID/download fora do escopo retornam 404 antes de consultar bytes do Blob.
4. Exportação JSON usa a mesma consulta da listagem, limitada a 100 registros autorizados.
5. HTTP privado usa no-store; o cliente invalida dados e descarta respostas/corpos/401/downloads antigos ao trocar empresa, usuário ou perfil. Logout limpa o estado imediatamente e as operações de cookie são serializadas.

Registros anteriores sem responsável não são atribuídos arbitrariamente a um operador. Não existe delegação de carteira ou edição/exclusão na UI deste recorte.

## Como conferir

Os workflows do PR executam a versão identificada no [registro](../../evidencias/execucao/PAC-06/registro.md). Para reexecutar em infraestrutura efêmera, abra o [run SQL/Blob](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191593) do PR e use **Re-run jobs**. Uma alteração de código backend/testes no PR também aciona a validação pertinente. O workflow usa dados e credenciais sintéticos de execução, sem dados de cliente.

Backend local sem fixture SQL:

```powershell
dotnet restore EBT.Platform.sln --nologo
dotnet test EBT.Platform.sln --no-restore --nologo --filter 'Category!=QaPersistence'
```

Frontend:

```powershell
Set-Location src/frontend
npm.cmd ci --ignore-scripts
npm.cmd test -- --run
npm.cmd run lint
npm.cmd run build
```

Os testes reais usam `EBT_QA_E2E=1`, SQL Server e Azurite configurados pelo workflow. Sem essa fixture, `QaFact` informa skip; não apresentar skip ou retorno antecipado como prova de SQL.

Para navegação manual, prepare uma fixture exclusiva de QA usando a configuração pública e segredos de execução descritos no workflow, inicie a API em `http://127.0.0.1:5000` (destino já definido no proxy Vite) e rode `npm.cmd run dev`. Acesse `/seguranca-qa` no endereço informado pelo Vite. Não reutilize banco/contas de cliente ou segredos de produção.

Na página **Sessão QA**, o código deve ser o da fixture de execução. Ele fica somente no estado do formulário, é limpo após login e não é persistido em localStorage. O backend bloqueia o login sintético em Production.

Sequência de conferência:

1. Entrar como `admin.orbe@demo.invalid`, criar um registro sintético e conferir sua releitura.
2. Trocar para `operador.orbe@demo.invalid`: o registro do administrador não entra na carteira; criar um registro próprio.
3. Trocar para Consulta: a UI não oferece escrita; o servidor também a recusa.
4. Sair: a lista privada desaparece imediatamente; acesso posterior à API exige nova sessão.
5. Entrar em Nexo: registros de Orbe não aparecem. ID/download cruzados, pool SQL e exportação são verificados nos testes automatizados.

As outras telas permanecem com massa ilustrativa da fundação. O novo fluxo de QA não transforma essas telas em módulos CRM autenticados. O endereço GitHub não representa uma implantação online da API.

## Provas e continuidade

- [Estado de execução PAC-06](../../planejamento/execucao_pac06.json), separado da baseline histórica.
- [Resumo CI sanitizado](../../evidencias/execucao/PAC-06/ci-resumo.json).
- [P04-05 — migrations/índices](../../evidencias/execucao/P04-05/registro.md).
- [P04-06 — RLS real](../../evidencias/execucao/P04-06/registro.md).
- [P04-07 — autorização por recurso](../../evidencias/execucao/P04-07/registro.md).
- [P04-08 — sessão/cache](../../evidencias/execucao/P04-08/registro.md).

Próximo pacote: [PAC-07](pacotes/PAC-07.md), com auditoria mínima, proteção adicional de cookies/tokens, onboarding negativo e demonstração integrada G-SEG com dois consumidores. A prova parcial do PAC-06 não fecha esse gate.
