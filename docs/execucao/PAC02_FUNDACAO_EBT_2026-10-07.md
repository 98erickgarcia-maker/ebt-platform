# PAC-02 — Fundação executável da EBT Platform

Data: 07/10/2026.

Status: **em verificação**.

## Resultado pretendido

Criar a primeira árvore executável da EBT Platform com:

1. solution .NET real;
2. API mínima com health;
3. configuração sem segredos;
4. dois consumidores sintéticos reproduzíveis;
5. frontend React/Vite;
6. Design System EBT aplicado às nove rotas-base;
7. CI próprio de backend e frontend.

## Arquitetura

Ver `docs/arquitetura/adr/ADR-005_CORE_INICIAL_EBT.md`.

## Consumidores sintéticos

Dois perfis completamente fictícios são definidos no backend:

- `orbe` — Orbe Industrial Demo;
- `nexo` — Nexo Serviços Demo.

IDs são determinísticos e diferentes. Os e-mails demonstrativos do frontend usam o domínio reservado `.invalid`.

Esses perfis não provam isolamento SQL; servem para testar configuração e impedir dependência de cadastro real antes do pacote de tenant/persistência.

## Configuração

Arquivos versionados:

- `appsettings.json`: base sem segredo;
- `appsettings.Development.json`: habilita dados sintéticos;
- `appsettings.Production.json`: desabilita dados sintéticos e exige configuração privada.

A chave de ambiente esperada em produção é nomeada, mas nenhum valor é versionado.

## Frontend

Rotas-base:

- `/login`;
- `/dashboard`;
- `/empresas`;
- `/empresas/:companyId`;
- `/contatos`;
- `/prospeccao`;
- `/pipeline`;
- `/agenda`;
- `/relatorios`.

Controles sem backend real aparecem desabilitados. A fundação não simula persistência ou notificações.

## Comandos de validação

Backend:

```bash
dotnet restore EBT.Platform.sln --nologo
dotnet build EBT.Platform.sln --no-restore --nologo
dotnet test EBT.Platform.sln --no-build --no-restore --nologo
dotnet list EBT.Platform.sln package --vulnerable --include-transitive
```

Frontend:

```bash
cd src/frontend
npm ci --ignore-scripts
npm test -- --run
npm run lint
npm run build
npm audit --audit-level=high
```

Nesta sessão, o ambiente local não possui .NET e o acesso do npm à rede não está confiável. A prova será obtida pelo workflow `Validar fundação EBT` no GitHub Actions. Nenhum comando será declarado aprovado antes do resultado do CI.

## Critérios P02

- P02-01: ADR registra monólito modular mínimo e limites.
- P02-02: solution e frontend possuem comandos reais de build.
- P02-03: config de produção falha sem segredo e não vaza valor/nome no erro.
- P02-04: dois consumidores sintéticos têm IDs próprios, reproduzíveis e nenhum dado de cliente real.

## Limites

G1 continua pendente até PAC-03, quando SQL, diagnóstico e CI integrado da persistência serão tratados.
