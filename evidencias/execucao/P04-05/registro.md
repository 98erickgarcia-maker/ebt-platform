# P04-05 — Migration e índices por tenant

Data: 07/10/2026. Estado: **demonstrado em QA no recorte**, sem homologação operacional ou produção.

Versão funcional: `904a087edab46cb50d5eb787f17859af1ad83a79`. [PR #7](https://github.com/98erickgarcia-maker/ebt-platform/pull/7), empilhado sobre a branch do PR #6; nenhum merge realizado.

[CI fundação 37701191579](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191579): sucesso, 23 testes backend de regra/API local; os 5 testes de SQL são explicitamente ignorados nesse job sem fixture. Frontend 28/28, lint, build e auditorias aprovados.

[CI SQL/Blob 37701191593](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191593): sucesso, **5/5 testes reais de QA, zero falhas e zero ignorados**, além do smoke autenticado da API. SQL Server 2022 Developer e Azurite efêmeros, imagens fixadas no workflow; tenants Orbe/Nexo sintéticos. [Resumo sanitizado](../PAC-06/ci-resumo.json).

Autoria: implementação Codex, revisão independente por agente `review_pac06`. Hora-pessoa real não apontada; manter a estimativa de 3h do ticket e não atribuir consumo da reserva por inferência. G-SEG continua aberto até PAC-07.

## Implementação e cenários

Foram versionadas três migrations: baseline do schema anterior, chave composta/OwnerUserId/índice de carteira e política RLS. `EnsureCreatedAsync` permanece como contrato interno compatível, mas sua implementação SQL chama `Database.MigrateAsync`. Não apagar dados ou migrations preexistentes. Schema anterior sem histórico é adotado apenas após preflight de colunas, PK e índices; divergência é recusada. Downgrade destrutivo foi bloqueado; retorno exige restore validado, sem afirmar que restore já foi ensaiado.

| Caso | Observado e prova |
|---|---|
| P04-05-C01 | Banco vazio sobe com 3 migrations; reexecução não duplica histórico. Snapshot SQL sintético no formato PAC-03/05 sem histórico migra e preserva registro/metadados de anexo. Casos `Empty_database_migrates...` e `Previous_EnsureCreated_snapshot...` em SQL real. |
| P04-05-C02 | Mesmo Id no mesmo tenant recusado por SQL com erro de unicidade 2627/2601. |
| P04-05-C03 | Mesmo Id em Orbe e Nexo gravado de modo independente; chave `(TenantKey, Id)`. |

Índice `(TenantKey, CreatedAtUtc)` preservado e índice `(TenantKey, OwnerUserId, CreatedAtUtc)` criado. Título não é chave única. `Record_identity_and_scope_are_tenant_aware` confirma modelo, índices e ausência de alteração de modelo não coberta por snapshot. Negativa adicional `Legacy_schema_with_missing_index...` observa erro SQL 51000, registro anterior preservado e nenhum histórico falsamente aplicado.

Limite: o snapshot de migration prova metadados SQL, não restore de banco nem arquivo legado externo. O roundtrip Blob real do recorte é coberto no teste de persistência e na API do mesmo workflow.

## Reprodução

Ver [guia PAC-06](../../../docs/execucao/GUIA_PAC06_SQL_RECURSO_CACHE.md) e nomes dos testes em `tests/Ebt.Foundation.Tests` / `src/frontend/src`.
