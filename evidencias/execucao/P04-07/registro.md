# P04-07 — Autorização por recurso e carteira

Data: 07/10/2026. Estado: **demonstrado em QA no recorte**, sem homologação operacional ou produção.

Versão funcional: `904a087edab46cb50d5eb787f17859af1ad83a79`. [PR #7](https://github.com/98erickgarcia-maker/ebt-platform/pull/7), empilhado sobre a branch do PR #6; nenhum merge realizado.

[CI fundação 37701191579](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191579): sucesso, 23 testes backend de regra/API local; os 5 testes de SQL são explicitamente ignorados nesse job sem fixture. Frontend 28/28, lint, build e auditorias aprovados.

[CI SQL/Blob 37701191593](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191593): sucesso, **5/5 testes reais de QA, zero falhas e zero ignorados**, além do smoke autenticado da API. SQL Server 2022 Developer e Azurite efêmeros, imagens fixadas no workflow; tenants Orbe/Nexo sintéticos. [Resumo sanitizado](../PAC-06/ci-resumo.json).

Autoria: implementação Codex, revisão independente por agente `review_pac06`. Hora-pessoa real não apontada; manter a estimativa de 3h do ticket e não atribuir consumo da reserva por inferência. G-SEG continua aberto até PAC-07.

## Implementação e cenários

A criação ignora tenant/responsável fornecidos pelo cliente e usa identidade do servidor. Administrador lê os registros de sua empresa; Operador lê somente sua carteira; Consulta lê registros de sua empresa sem escrita; Suporte não acessa registros comerciais. Legado sem responsável fica visível a Administrador/Consulta, sem atribuição fictícia a Operador.

Filtro de responsável é aplicado no SQL antes do limite de 100 registros. GET por ID e download retornam 404 fora da carteira/empresa. Autorização de recurso precede leitura do Blob. Exportação JSON usa a mesma listagem autorizada, limitada a 100; não significa exportação completa do CRM.

| Caso | Observado e prova |
|---|---|
| P04-07-C01 | ID e download Orbe acessados por Nexo respondem 404, listagem Nexo vazia; API com SQL/Blob reais. |
| P04-07-C02 | Operador Orbe não acessa ID/anexo do administrador Orbe (404), mas salva e lista seu registro. `Denied_resource_does_not_read_Blob...` comprova zero leituras do Blob na negativa e responsável do servidor na gravação. |
| P04-07-C03 | Exportação do Operador traz exatamente o ID da carteira autorizada, igual à listagem. |

`Resource_scope_is_enforced` cobre também usuário inativo, legado sem dono e Suporte. Teste real alterna o mesmo cookie jar para Consulta, observa escrita 403, logout 204 e acesso posterior 401.

Limite: autorização implementada no recorte FoundationRecords; não afirmar ACL de módulos CRM/documentos ainda não construídos. Sem edição, exclusão ou delegação de carteira na UI deste pacote.

## Reprodução

Ver [guia PAC-06](../../../docs/execucao/GUIA_PAC06_SQL_RECURSO_CACHE.md) e nomes dos testes em `tests/Ebt.Foundation.Tests` / `src/frontend/src`.
