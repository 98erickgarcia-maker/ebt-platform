# P04-08 — Isolamento de sessão e respostas privadas

Data: 07/10/2026. Estado: **demonstrado em QA no recorte**, sem homologação operacional ou produção.

Versão funcional: `904a087edab46cb50d5eb787f17859af1ad83a79`. [PR #7](https://github.com/98erickgarcia-maker/ebt-platform/pull/7), empilhado sobre a branch do PR #6; nenhum merge realizado.

[CI fundação 37701191579](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191579): sucesso, 23 testes backend de regra/API local; os 5 testes de SQL são explicitamente ignorados nesse job sem fixture. Frontend 28/28, lint, build e auditorias aprovados.

[CI SQL/Blob 37701191593](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37701191593): sucesso, **5/5 testes reais de QA, zero falhas e zero ignorados**, além do smoke autenticado da API. SQL Server 2022 Developer e Azurite efêmeros, imagens fixadas no workflow; tenants Orbe/Nexo sintéticos. [Resumo sanitizado](../PAC-06/ci-resumo.json).

Autoria: implementação Codex, revisão independente por agente `review_pac06`. Hora-pessoa real não apontada; manter a estimativa de 3h do ticket e não atribuir consumo da reserva por inferência. G-SEG continua aberto até PAC-07.

## Implementação e cenários

Trilha aplicada **N**, promovida da sugestão R2: mudou a fronteira de segurança/concorrência do cliente HTTP. Estimativa permanece 3h.

Respostas de auth/registros (inclusive 401/403/404/erros) usam no-store/private. Cliente envia cache no-store e cookies same-origin. Não foi introduzido cache de registros no servidor ou armazenamento privado em localStorage. Estado de sessão vive em memória, com fingerprint de tenantId/tenantKey/userId/role e geração que invalida requisições.

Troca de identidade, perfil, logout e 401 atual abortam pedidos e descartam respostas/corpos antigos, mesmo quando o fetch ignora aborto. 401 antigo não apaga uma nova identidade. Operações de cookie são serializadas e executadas até conclusão; obsolescência impede publicar identidade anterior, sem eliminar um logout solicitado.

| Caso | Observado e prova |
|---|---|
| P04-08-C01 | Logout limpa identidade e desmonta lista privada imediatamente; API real confirma 204 seguido de 401 e no-store. |
| P04-08-C02 | Testes trocam tenant, usuário e perfil; teste de componente entra Orbe, sai, entra Nexo e só mostra carteira Nexo. |
| P04-08-C03 | Resposta Orbe atrasada não aparece em Nexo; corpo JSON, download e 401 atrasados descartados. Refresh automático não cancela logout enfileirado. |

Nova rota `/seguranca-qa` demonstra sessão e registros reais sintéticos. As demais telas continuam com massa ilustrativa independente; não apresentá-las como CRM privado autenticado. Login QA continua bloqueado no backend Production. Frontend: 28/28 no CI, incluindo teste de componente de troca de carteira; não houve revisão visual em navegador de produção.

Falha local inicial: worker threads do Vitest no Windows expirou antes de rodar todos os arquivos. Execução com forks passou; configuração agora usa forks no Windows e mantém threads no Linux. Codex Process Jobs retornou Unsupported platform win32; testes executados no terminal. A falha de ambiente não foi contada como aprovação.

## Reprodução

Ver [guia PAC-06](../../../docs/execucao/GUIA_PAC06_SQL_RECURSO_CACHE.md) e nomes dos testes em `tests/Ebt.Foundation.Tests` / `src/frontend/src`.
