# PASSO A PASSO — EBT Platform PAC-02

## Objetivo e resultado alcançado

Criar a primeira aplicação executável da EBT Platform sobre o G0 do EBT Connect.

Resultado validado no commit `03e0928d2670fe14fa7d96c20037efee0ddbcab7`:

- backend .NET modular compila;
- frontend React/TypeScript compila;
- 3 testes backend passam;
- 11 testes frontend passam, cobrindo as nove rotas-base;
- lint passa sem warnings/erros;
- auditorias backend/frontend não reportam vulnerabilidades;
- varredura de padrões de segredo passa;
- configuração Development/Production está separada;
- massa A/B é sintética e determinística.

## Pré-requisitos

- .NET SDK 10.0.400;
- Node 24.19.0;
- npm compatível com o lockfile;
- nenhuma credencial real;
- Development para executar fixtures sintéticos.

## Estrutura

```text
EBT.Platform.sln
src/
  backend/
    Ebt.Domain/
    Ebt.Application/
    Ebt.Infrastructure/
    Ebt.Api/
  frontend/
tests/
  Ebt.Foundation.Tests/
```

## Como executar

Backend:

```bash
dotnet restore EBT.Platform.sln --nologo
dotnet build EBT.Platform.sln --no-restore --nologo
dotnet test EBT.Platform.sln --no-build --no-restore --nologo
dotnet run --project src/backend/Ebt.Api/Ebt.Api.csproj
```

Frontend:

```bash
cd src/frontend
npm ci --ignore-scripts
npm test -- --run
npm run lint
npm run build
npm run dev
```

## Arquivos e integrações

A fundação cria somente código no repositório EBT Platform. Nenhum banco, e-mail, WhatsApp, storage ou serviço externo foi conectado.

## Validações executadas

Run principal: `37671307509`.

- backend restore/build/test: validado;
- backend auditoria: validado;
- secret patterns: validado;
- frontend install/test/lint/build: validado;
- frontend audit: validado;
- documentação/organização: validado no run `37671307545`.

## Problemas encontrados e resolvidos

1. A primeira tentativa de branch do PAC-02 divergiu devido a atualização concorrente no PAC-01. Nenhum trabalho foi sobrescrito; foi criada uma branch limpa baseada no novo HEAD.
2. O projeto de testes inicialmente precisava do using global do xUnit. Corrigido antes do primeiro CI.
3. A declaração parcial do `Program` foi ajustada para sintaxe válida antes do primeiro CI.
4. O posicionamento da agenda foi corrigido antes do primeiro CI.
5. Actions v4 geraram aviso de runtime Node antigo. As actions do workflow de fundação foram atualizadas e fixadas por SHA nas versões oficiais atuais.
6. A cobertura frontend foi ampliada para todas as nove rotas-base.
7. Foi adicionada varredura automática de padrões comuns de segredo.

## Limitações e próximo passo

PAC-02 não fecha G1. O próximo pacote é PAC-03: SQL, persistência, diagnóstico e CI dessa fronteira.

Não habilitar login real, tenant real, drag-and-drop persistente, busca global, notificações ou dados de cliente antes dos pacotes que definem esses contratos.
