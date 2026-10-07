# PASSO A PASSO — EBT Platform PAC-02

## Objetivo

Criar a primeira aplicação executável da EBT Platform sobre o baseline aprovado do PAC-01.

## Pré-requisitos

- branch do PAC-01 preservada;
- .NET SDK 10.0.400 no ambiente de build;
- Node 24.19.0 no CI;
- nenhum segredo ou cadastro real;
- revisão do PR e CI antes de considerar o pacote demonstrado.

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
```

Frontend:

```bash
cd src/frontend
npm ci --ignore-scripts
npm test -- --run
npm run lint
npm run build
```

API em Development:

```bash
dotnet run --project src/backend/Ebt.Api/Ebt.Api.csproj
```

Frontend:

```bash
cd src/frontend
npm run dev
```

## O que validar

1. `/health` retorna produto/plataforma/ambiente sem segredo.
2. dados sintéticos só são expostos quando `SyntheticDataEnabled=true`.
3. falta de configuração privada obrigatória interrompe startup com mensagem segura.
4. Orbe e Nexo têm IDs e usuários próprios.
5. dashboard e todas as rotas-base renderizam a identidade EBT.
6. nenhuma marca de produto-fonte aparece no frontend.
7. busca global/notificações/criação permanecem desabilitadas enquanto não possuem contrato real.
8. desktop/mobile mantêm navegação e foco visível.

## Arquivos e integrações alterados

Este pacote cria somente runtime próprio da EBT Platform e workflow de CI. Não altera bancos, serviços externos nem os repositórios-fonte.

## Problemas/limitações conhecidos

- SQL real entra no PAC-03.
- autenticação e isolamento por tenant entram nos pacotes de segurança.
- métricas/tabelas atuais usam massa sintética.
- drag-and-drop do pipeline ainda não é habilitado; o comportamento só será ativado junto da regra de histórico/conflito.
- busca global é visualmente apresentada, mas desabilitada até existir endpoint/contrato real.

## Evidência

Os registros P02-01 a P02-04 só devem ser finalizados depois do CI do PR da fundação. Não preencher resultado fictício.
