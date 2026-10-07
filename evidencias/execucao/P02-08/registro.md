# P02-08 — demonstração da fundação e G1

Data: 07/10/2026.

Versão validada: `3804302233cc72bfef29e5c5cbbb62f6aeb548be`.

## Demonstração automatizada

O teste integrado inicia a EBT Platform em `QA`, usando massa sintética e destinos temporários exclusivos.

Fluxo demonstrado:

1. aplicação inicia em QA;
2. `/health` retorna 200 com banco e storage saudáveis;
3. probe sintético é persistido;
4. resposta retorna ID único e SHA-256;
5. leitura pelo ID devolve o mesmo conteúdo;
6. metadado e binário ficam separados;
7. host Production é recusado pelo guard.

## Reprodutibilidade

O mesmo repositório possui:

- `global.json`;
- solution real;
- configuração QA versionada sem segredo;
- comandos de build/test no workflow;
- fixture sintética;
- teste integrado sem dependência de serviço externo.

## Cenários

- P02-08-C01 — health e persistência conferidos: **validado**.
- P02-08-C02 — clone/CI reproduz a fundação: **validado no GitHub Actions**.
- P02-08-C03 — nada declarado produção: **validado**; QA é explicitamente bloqueado em Production.

## Resultado

**G1 aprovado para avançar ao próximo bloco.**

Isto significa somente: ambiente isolado, build reproduzível, health, massa própria e persistência QA demonstrados.

Não aprova produção, identidade, tenancy, SQL Server/Azure SQL real, RLS, deploy ou dados de cliente.
