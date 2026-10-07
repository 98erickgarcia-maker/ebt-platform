# P02-08 — demonstração da fundação e G1

Data: 07/10/2026.

Versão funcional validada: `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

Run principal de QA: `37686069941` — **success**.

## Demonstração executada

Em runner limpo do GitHub Actions:

1. SQL Server e Azurite foram iniciados;
2. a solução foi restaurada e compilada;
3. o teste de integração salvou metadado no SQL e binário no Blob;
4. a API EBT foi iniciada em ambiente `QA`;
5. `/health/ready` confirmou SQL e Blob como `healthy`;
6. um registro sintético foi criado via HTTP;
7. o mesmo ID foi relido via HTTP;
8. o anexo foi baixado e comparado byte a byte com o conteúdo esperado;
9. dependências foram auditadas;
10. containers efêmeros foram encerrados.

## Reprodutibilidade

A execução parte de checkout limpo, usa versões fixadas do SDK/actions e digests fixados dos containers do gate. Banco, container e credencial de QA são derivados da própria execução e não dependem de arquivo privado local.

## Cenários

- P02-08-C01 — health e persistência conferidos: **validado**.
- P02-08-C02 — clone reproduz: **validado no runner limpo do CI**.
- P02-08-C03 — nada declarado produção: **validado**; configuração, nomes, documentação e workflow são explicitamente QA.

## Resultado

Os requisitos mínimos de G1 foram demonstrados: ambiente isolado, build reproduzível, CI pertinente, health, massa própria e persistência QA.

A ficha formal está em `evidencias/execucao/P02-GATE/registro.md`.

## Limite

G1 não aprova produção, autenticação, autorização, tenant isolation, onboarding E2E, backup produtivo ou implantação em cliente.
