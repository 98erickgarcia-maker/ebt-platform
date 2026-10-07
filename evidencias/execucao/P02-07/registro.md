# P02-07 — CI mínimo e diagnóstico seguro

Data: 07/10/2026.

Versão funcional validada: `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

## CI final

### Fundação

Run `37686069814` — **success**.

- restore backend: aprovado;
- build backend: aprovado;
- testes backend: aprovados;
- auditoria .NET: aprovada;
- varredura de padrões de segredo: aprovada;
- `git diff --check`: aprovado;
- frontend install/test/lint/build/audit: aprovados.

### Persistência QA

Run `37686069941` — **success**.

- SQL Server efêmero: healthy;
- Azurite efêmero: healthy;
- build: **0 warnings / 0 errors**;
- integração SQL + Blob: **1 passed / 0 failed**;
- demonstração HTTP de health/save/reload/download: aprovada;
- auditoria .NET: nenhum pacote vulnerável reportado;
- encerramento dos containers: aprovado.

### Planejamento/rastreabilidade

Run `37686069789` — **success**.

## CI bloqueou falhas reais

Durante a implementação o CI detectou e bloqueou:

- erro de compilação C# no primeiro recorte;
- incompatibilidade TypeScript com `erasableSyntaxOnly`.

Os erros foram corrigidos antes do gate final. Isso prova que o CI não é apenas decorativo.

## Diagnóstico

A API implementa:

- `/health`;
- `/health/live`;
- `/health/ready`;
- `X-Trace-Id`;
- `traceId` técnico em problemas controlados;
- readiness separado de liveness;
- readiness com estado explícito de SQL e Blob;
- middleware que registra tipo da exceção e traceId, sem devolver mensagem bruta da exceção ao cliente.

Teste automatizado verifica que o traceId contém apenas identificador técnico e não cadastro sintético.

A demonstração do CI também verifica que a resposta de health não contém senha ou connection string.

## Cenários

- P02-07-C01 — CI bloqueia falha real: **validado**.
- P02-07-C02 — health representa dependências definidas: **validado com SQL e Blob reais de QA**.
- P02-07-C03 — traceId não contém cadastro: **validado**.

## Limite

Observabilidade produtiva, retenção de logs, APM e alertas externos não fazem parte do G1.
