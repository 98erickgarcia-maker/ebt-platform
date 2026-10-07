# P04-06 — RLS de SQL com filtro e bloqueio

Data: 07/10/2026. Estado: **demonstrado em QA no recorte**, sem homologação operacional ou produção.

Versão funcional: `904a087edab46cb50d5eb787f17859af1ad83a79`. [PR #7](https://github.com/98erickgarcia-maker/ebt-platform/pull/7), empilhado sobre a branch do PR #6; nenhum merge realizado.

[CI fundação 37701191579](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191579): sucesso, 23 testes backend de regra/API local; os 5 testes de SQL são explicitamente ignorados nesse job sem fixture. Frontend 28/28, lint, build e auditorias aprovados.

[CI SQL/Blob 37701191593](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191593): sucesso, **5/5 testes reais de QA, zero falhas e zero ignorados**, além do smoke autenticado da API. SQL Server 2022 Developer e Azurite efêmeros, imagens fixadas no workflow; tenants Orbe/Nexo sintéticos. [Resumo sanitizado](../PAC-06/ci-resumo.json).

Autoria: implementação Codex, revisão independente por agente `review_pac06`. Hora-pessoa real não apontada; manter a estimativa de 3h do ticket e não atribuir consumo da reserva por inferência. G-SEG continua aberto até PAC-07.

## Implementação e cenários

A política `ebt_security.FoundationTenantPolicy` filtra SELECT/UPDATE/DELETE e bloqueia AFTER INSERT/AFTER UPDATE quando o TenantKey não coincide com SESSION_CONTEXT. Contexto ausente não permite linhas. Interceptor sem estado compartilhado define contexto com parâmetro SQL a cada abertura lógica, inclusive reabertura por retry. Contexto EF não pode ser reatribuído; chave SQL é somente leitura durante a conexão. A reutilização física do pool foi observada via mesmo @@SPID.

| Caso | Observado e prova |
|---|---|
| P04-06-C01 | Consulta EF de tabela inteira, sem filtro LINQ de tenant, retorna apenas Orbe/Nexo conforme a conexão; conexão sem contexto retorna vazio. |
| P04-06-C02 | Insert com tenant Nexo em contexto Orbe e UPDATE de TenantKey para Nexo recusados pelo próprio SQL, erro 33504. Tentativa de reatribuir a chave de sessão recusada, erro 15664. |
| P04-06-C03 | 5 testes reais aprovados e 0 ignorados; sucesso de setup/compile precede os casos de proteção. |

O teste usa pool de tamanho 1 e confirma mesmo SPID para Orbe -> Nexo -> sem contexto -> Orbe, sem herança de linhas. Identidade da API deriva do catálogo do servidor e headers não a trocam.

Referências técnicas: [RLS Microsoft](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security), [sp_set_session_context](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-set-session-context-transact-sql).

Limite: QA usa principal administrativo sintético para criar/migrar banco; a política também é aplicada às consultas desse principal. Isso não prova segregação de credenciais/DDL de produção ou governança administrativa. Não liberar G-SEG/produção com esta evidência isolada.

## Reprodução

Ver [guia PAC-06](../../../docs/execucao/GUIA_PAC06_SQL_RECURSO_CACHE.md) e nomes dos testes em `tests/Ebt.Foundation.Tests` / `src/frontend/src`.
