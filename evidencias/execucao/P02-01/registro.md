# P02-01 — arquitetura e limite do Core inicial

Data: 07/10/2026.

Versão executada: `03e0928d2670fe14fa7d96c20037efee0ddbcab7`.

## Resultado

Foi criado o ADR `docs/arquitetura/adr/ADR-005_CORE_INICIAL_EBT.md`.

Decisão: monólito modular mínimo com:

- `Ebt.Domain`;
- `Ebt.Application`;
- `Ebt.Infrastructure`;
- `Ebt.Api`;
- frontend React/TypeScript/Vite;
- testes de fundação.

SQL permanece direção para o PAC-03. Microserviços, Redis e filas continuam fora sem requisito medido.

## Casos

- P02-01-C01 — ADR identifica decisões e limites: **validado**.
- P02-01-C02 — site preserva stack existente: **validado**; nenhum arquivo do repositório `ebt-enterprise-site` foi alterado.
- P02-01-C03 — Core não promete C0-C13: **validado**; o ADR declara explicitamente o que não foi implementado.

## Evidência

Workflow de aplicação: run `37671307509`, conclusão **success**.

Workflow documental: run `37671307545`, conclusão **success**.

## Limite

Arquitetura aprovada para fundação; não é aprovação de produção, tenant, SQL ou integrações.
