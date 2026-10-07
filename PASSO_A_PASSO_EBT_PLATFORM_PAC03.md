# PASSO A PASSO — EBT Platform PAC-03 / G1

## Resultado atual

A fundação da EBT Platform já pode ser reproduzida com banco e storage **de QA**, sem tocar produção.

Gate G1: **aprovado para fundação QA** no commit `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

## O que existe

- SQL Server para metadados;
- Blob/Azurite para binários;
- guardas de destino QA;
- health live/ready;
- traceId seguro;
- endpoints sintéticos para provar persistência;
- cliente HTTP com tratamento de erro;
- workflow completo de QA.

## Execução normal da fundação

Backend:

```bash
dotnet restore EBT.Platform.sln --nologo
dotnet build EBT.Platform.sln --no-restore --nologo
dotnet test EBT.Platform.sln --no-build --no-restore --nologo
```

Frontend:

```bash
cd src/frontend
npm ci --ignore-scripts
npm test -- --run
npm run lint
npm run build
```

## Execução QA com persistência

A prova oficial está no workflow `Validar persistência QA EBT`.

Ele executa automaticamente:

1. SQL Server efêmero;
2. Azurite efêmero;
3. build;
4. integração SQL/Blob;
5. API em ambiente QA;
6. health/readiness;
7. gravação de registro sintético;
8. releitura por ID;
9. download do anexo;
10. auditoria;
11. encerramento dos containers.

## Configuração necessária fora do CI

A aplicação QA espera somente nomes de variáveis privadas; valores não são versionados:

- `EBT_QA_SQL_PASSWORD`;
- `EBT_QA_BLOB_CONNECTION`.

O alvo também deve obedecer obrigatoriamente aos padrões `EbtQa_*` e `ebt-qa-*`.

## Evidência

Runs finais:

- `37686069789` — planejamento: success;
- `37686069814` — fundação: success;
- `37686069941` — persistência QA/API: success.

## Problemas encontrados e resolvidos

- build C# bloqueou um literal inválido;
- build TypeScript bloqueou parameter properties incompatíveis;
- senha QA estática foi eliminada;
- imagens de containers foram fixadas por digest.

O CI só ficou verde após essas correções.

## Próxima fronteira

Não usar G1 como justificativa para cadastrar cliente real.

Antes de uso multiempresa real, executar os pacotes de segurança/tenant e fechar **G-SEG**, incluindo negativas entre tenants, autorização, sessão e onboarding E2E.
