# PASSO A PASSO — EBT Platform PAC-03 / G1

## O que foi concluído

A EBT Platform agora possui uma fundação QA demonstrável:

- aplicação inicia em QA;
- health representa banco/storage QA;
- dado sintético é salvo e relido;
- metadado e binário são separados;
- Production é recusado;
- cliente HTTP trata falhas sem falso sucesso;
- CI reproduz tudo.

## Commit de prova

`3804302233cc72bfef29e5c5cbbb62f6aeb548be`.

## Validação

GitHub Actions:

- aplicação: run `37690576723` — success;
- documentos: run `37690576729` — success.

Resultados:

- backend: 5/5 testes;
- frontend: 15/15 testes;
- build: verde;
- lint: verde;
- auditorias: sem vulnerabilidades conhecidas reportadas;
- secret-pattern scan: verde.

## Como executar QA

```bash
ASPNETCORE_ENVIRONMENT=QA dotnet run --project src/backend/Ebt.Api/Ebt.Api.csproj
```

A configuração QA padrão grava somente sob `./tmp/ebt-qa`.

Para validar o frontend:

```bash
cd src/frontend
npm ci --ignore-scripts
npm test -- --run
npm run lint
npm run build
```

## Proteções

- QA não inicia em host Production;
- banco precisa terminar em `.qa.db`;
- destinos precisam estar identificados como `ebt-qa`;
- health não mostra caminhos/segredos;
- endpoint de probe só é mapeado quando QA está habilitado.

## Próximo passo

G1 está aprovado.

Não tratar esta persistência SQLite como solução final multiempresa. O próximo gate de segurança exige SQL real, tenants A/B, acesso direto por ID, negativa de ação e onboarding/isolamento próprios.
