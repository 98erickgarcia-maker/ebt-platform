# PAC-03 — QA, persistência, diagnóstico e fechamento G1

Data: 07/10/2026.

Versão validada: `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

Status: **implementado e demonstrado em QA efêmero**.

Gate: **G1 aprovado para a fundação QA**.

## Resultado

A fundação EBT Platform passou a ter uma prova real e reproduzível de:

- SQL Server para metadados;
- Blob Storage compatível via Azurite para binários;
- separação entre metadado e arquivo;
- ambiente QA por execução;
- recusa automática de alvo não QA;
- cliente HTTP com tratamento de erro/401/download;
- health live/ready;
- traceId sanitizado;
- CI que compila, testa, audita e demonstra a API.

## Ambiente de prova

O gate usa containers efêmeros no GitHub Actions. Não utiliza credenciais, banco ou storage de cliente.

Por execução são gerados:

- `EbtQa_<run_id>`;
- `ebt-qa-<run_id>`;
- senha SQL sintética derivada do `run_id`.

As imagens do gate estão fixadas por digest para impedir variação silenciosa.

## Provas finais

- planejamento: run `37686069789` — success;
- fundação: run `37686069814` — success;
- persistência QA: run `37686069941` — success.

Na prova QA:

- SQL Server: healthy;
- Azurite: healthy;
- build: 0 warnings / 0 errors;
- integração real SQL + Blob: 1 passed;
- API iniciada em QA;
- readiness: SQL/Blob healthy;
- POST sintético: aprovado;
- reload pelo ID: aprovado;
- download e comparação do anexo: aprovado;
- auditoria .NET: sem pacotes vulneráveis reportados pelas fontes atuais;
- containers encerrados ao final.

Na fundação do mesmo commit:

- backend: build/test/audit/secret scan/diff-check verdes;
- frontend: **15 testes**, lint, build e audit verdes.

## Cliente HTTP

A adaptação foi guiada pelo comportamento observado na fonte técnica congelada, especialmente o blob `ddfa728f7936b59f52adddf88ca43051ce4ae699`.

Foram trazidos somente padrões compatíveis com o recorte:

- problema HTTP;
- 401;
- falha de rede;
- resposta confirmada antes de sucesso;
- download inválido.

Sessão real/CSRF continuam para a fase de segurança.

## Diagnóstico

`/health/live` indica processo vivo.

`/health/ready` indica prontidão das dependências do recorte e pode retornar indisponível quando SQL/Blob não estão saudáveis.

Problemas internos devolvem traceId técnico e mensagem segura; detalhes brutos de exceção permanecem no servidor sem serem enviados ao cliente.

## Correções feitas durante a verificação

1. correção de literal C# detectado pelo build;
2. adequação do cliente HTTP ao `erasableSyntaxOnly` do TypeScript;
3. credencial QA tornou-se efêmera por execução;
4. imagens SQL/Azurite foram fixadas pelos digests observados e revalidadas.

## Limites

G1 significa “fundação reproduzível em QA”. Não significa:

- produção;
- tenancy segura;
- autenticação final;
- conformidade;
- onboarding de cliente;
- backup/restore produtivo.

Ver ficha formal em `evidencias/execucao/P02-GATE/registro.md`.
