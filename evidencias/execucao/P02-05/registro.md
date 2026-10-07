# P02-05 — banco e storage exclusivos de QA

Data: 07/10/2026.

Versão validada: `3804302233cc72bfef29e5c5cbbb62f6aeb548be`.

## Implementação

A fundação usa, somente no ambiente `QA`:

- SQLite em arquivo com sufixo obrigatório `.qa.db`;
- storage de binários em diretório separado;
- metadado persistido em SQLite;
- binário persistido no filesystem;
- guard que recusa host `Production`;
- guard que exige destino identificado como `ebt-qa`.

O arquivo padrão de QA usa apenas caminhos sob `./tmp/ebt-qa`, já ignorados pelo repositório.

## Prova

Teste integrado `Qa_app_persists_and_reloads_metadata_and_binary_in_separate_targets`:

1. inicia a aplicação em ambiente QA;
2. chama `/health`;
3. grava um probe sintético via API;
4. relê o mesmo ID via API;
5. compara conteúdo e SHA-256;
6. confirma metadado em SQLite e binário em alvo separado.

Teste `Qa_guard_refuses_production_host` confirma recusa de host Production.

## Cenários

- P02-05-C01 — destino exclusivo conferido: **validado**.
- P02-05-C02 — alvo produção recusado: **validado**.
- P02-05-C03 — binário e metadado separados: **validado**.

## Limite

Esta prova fecha **persistência QA do G1**. Não é prova de SQL Server/Azure SQL real, row-level security ou tenancy. Essas exigências pertencem ao G-SEG.
