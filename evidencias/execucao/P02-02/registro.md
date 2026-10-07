# P02-02 — estrutura e comandos reproduzíveis

Data: 07/10/2026.

Versão executada: `03e0928d2670fe14fa7d96c20037efee0ddbcab7`.

## Estrutura criada

- `EBT.Platform.sln`;
- `global.json` com SDK .NET 10.0.400;
- backend modular;
- frontend React/TypeScript/Vite;
- testes;
- workflow `Validar fundação EBT`.

## Comandos provados no CI

Backend:

```bash
dotnet restore EBT.Platform.sln --nologo
dotnet build EBT.Platform.sln --no-restore --nologo
dotnet test EBT.Platform.sln --no-build --no-restore --nologo
dotnet list EBT.Platform.sln package --vulnerable --include-transitive
git diff --check
```

Resultado:

- restore: **success**;
- build: **success**, 0 warnings e 0 errors;
- testes: **3 passed, 0 failed**;
- auditoria .NET: nenhum pacote vulnerável encontrado nas fontes atuais;
- `git diff --check`: **success**.

Frontend:

```bash
npm ci --ignore-scripts
npm test -- --run
npm run lint
npm run build
npm audit --audit-level=high
```

Resultado:

- instalação: **success**;
- testes: **11 passed, 0 failed**;
- lint: **0 warnings, 0 errors**;
- build Vite/TypeScript: **success**;
- auditoria npm: **0 vulnerabilities**.

## Casos

- P02-02-C01 — build backend/frontend reproduzível: **validado no GitHub Actions**.
- P02-02-C02 — arquivo de solução real: **validado**.
- P02-02-C03 — sem arquivo privado implícito: **validado para esta fundação**; configuração privada é variável de ambiente e não arquivo local obrigatório.

## Ambiente

GitHub Actions Ubuntu; Node 24.19.0; .NET SDK 10.0.400.

## Limite

O ambiente desta sessão não possuía .NET local. A prova executável registrada é do CI do repositório, não uma alegação de build local.
