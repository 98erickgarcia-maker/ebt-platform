# P01-02 — registro de execução

Data: 07/10/2026.

## Classificação de evidências

| Evidência | Versão/data | Classificação | Uso |
|---|---|---|---|
| refs GitHub congeladas | 07/10/2026 | atual/reproduzível | localizar contratos candidatos |
| CI da fonte técnica | commit `ce14f5...`, run `37453203674` | atual para a ref congelada | separar o que realmente passou do que ficou pendente |
| evidências SQL anteriores do planejamento | 06/10/2026 | histórica | contexto; não certifica a EBT Platform |
| onboarding/E2E incompleto da fonte | 06/10/2026 | pendência relevante | impede inferir segurança pronta |
| visual aprovado do EBT Connect | 07/10/2026 | requisito de produto | orientar design; não prova funcionamento |

## Leitura do CI congelado

Na execução `37453203674`:

- backend: restore, build e testes **aprovados**;
- auditoria de pacotes backend e verificação de segredos **aprovadas**;
- frontend: `npm ci`, testes, lint e build **aprovados**;
- frontend: `npm audit --audit-level=high` **reprovado** por `source-map-js 1.2.1` e `undici 8.10.0`;
- SQL/E2E: **cancelado**, portanto não vale como prova de banco real ou onboarding.

A EBT Platform não reutilizará o lockfile da fonte técnica. Dependências serão resolvidas na árvore EBT e auditadas novamente.

## Cenários

- P01-02-C01 — SQL conclusivo separado do anterior: **validado como histórico separado; a execução atual de SQL/E2E foi cancelada e não a substitui**.
- P01-02-C02 — onboarding continua pendente: **confirmado como limite do reuso**.
- P01-02-C03 — provas não se estendem a módulos ausentes: **validado por regra explícita deste baseline**.

Nenhuma evidência da fonte é tratada como aprovação automática da EBT Platform.
