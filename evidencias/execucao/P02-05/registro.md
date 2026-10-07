# P02-05 — banco e storage exclusivos de QA

Data: 07/10/2026.

Versão funcional validada: `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

Workflow de persistência QA: run `37686069941` — **success**.

## Implementação

A prova de persistência usa serviços efêmeros e exclusivos da execução de CI:

- SQL Server 2022 para metadados;
- Azurite 3.37.0 para binários;
- banco por execução: `EbtQa_<run_id>`;
- container por execução: `ebt-qa-<run_id>`;
- credencial SQL sintética gerada a partir do ID da execução;
- nenhum ambiente de cliente ou produção é consultado.

As imagens usadas no gate estão fixadas por digest no workflow:

- SQL Server: `sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090`;
- Azurite: `sha256:830430c1da1a2d537e08f3e6764dd1f5ae00cf0346bcaf625b968ec3f0971fd5`.

## Proteção de destino

`QaTargetGuard` aceita somente:

- banco no padrão `EbtQa_*`;
- container no padrão `ebt-qa-*`;
- destinos sem a palavra `prod`.

Os testes negativos recusam nomes de produção e nomes fora do padrão QA com mensagem sanitizada.

## Separação de metadado e binário

O teste de integração `Qa_persists_metadata_and_binary_in_separate_stores` prova que:

- metadados são persistidos no SQL;
- conteúdo binário é persistido no Blob;
- o modelo SQL não contém propriedade `byte[]`;
- o anexo é baixado novamente com bytes idênticos;
- SQL e Blob respondem como saudáveis.

## Destruição/recriação

O ambiente do gate é criado por execução e destruído quando os containers de serviço do GitHub Actions são encerrados. Recriar significa executar novamente o workflow, gerando novos nomes de banco/container vinculados ao novo `run_id`.

Não existe comando de destruição apontando a ambiente externo ou produtivo.

## Cenários

- P02-05-C01 — destino exclusivo conferido: **validado**.
- P02-05-C02 — tentativa com alvo produção recusada: **validado por testes negativos**.
- P02-05-C03 — binário e metadado separados: **validado por integração SQL + Blob real de QA**.

## Limite

A prova cobre a fundação QA. Não representa Azure SQL/Storage produtivos, backup de produção, tenant isolation ou dados reais.
