# PAC-02 — Fundação executável da EBT Platform

Data: 07/10/2026.

Status: **implementado e validado no CI de fundação**.

Versão funcional validada: `03e0928d2670fe14fa7d96c20037efee0ddbcab7`.

Workflow de aplicação: run `37671307509` — **success**.

Workflow documental: run `37671307545` — **success**.

## Resultado demonstrado

A EBT Platform agora possui uma primeira árvore executável com:

1. solution .NET real;
2. API mínima e health;
3. configuração sem segredo versionado;
4. dois consumidores sintéticos determinísticos;
5. frontend React/TypeScript/Vite;
6. Design System EBT aplicado às nove rotas-base;
7. testes de fundação;
8. CI próprio de backend/frontend;
9. auditoria de dependências;
10. verificação automática de padrões de segredo rastreados.

## Arquitetura

Ver `docs/arquitetura/adr/ADR-005_CORE_INICIAL_EBT.md`.

A decisão continua sendo monólito modular mínimo. SQL é a próxima fronteira, não uma capacidade simulada nesta fase.

## Consumidores sintéticos

- `orbe` — Orbe Industrial Demo;
- `nexo` — Nexo Serviços Demo.

Nenhum cadastro real é necessário para executar a fundação.

## Configuração

- base sem segredo;
- Development com massa sintética;
- Production sem massa sintética e com configuração privada obrigatória;
- ausência de configuração privada falha com mensagem segura.

## Frontend

Rotas-base validadas por teste de montagem:

- `/login`;
- `/dashboard`;
- `/empresas`;
- `/empresas/:companyId`;
- `/contatos`;
- `/prospeccao`;
- `/pipeline`;
- `/agenda`;
- `/relatorios`.

O teste também impede a marca do produto-fonte de aparecer nessas rotas.

Controles que ainda não possuem backend real permanecem desabilitados.

## Resultados do CI

### Backend

- restore: aprovado;
- build: aprovado com **0 warnings / 0 errors**;
- testes: **3 passed / 0 failed**;
- auditoria de pacotes: nenhum vulnerável reportado;
- varredura de padrões de segredo: aprovada;
- `git diff --check`: aprovado.

### Frontend

- `npm ci`: aprovado;
- testes: **11 passed / 0 failed**;
- lint: **0 warnings / 0 errors**;
- build: aprovado;
- `npm audit --audit-level=high`: **0 vulnerabilities**.

## Estado dos tickets

- P02-01: validado — ADR e limites.
- P02-02: validado — estrutura e builds reproduzíveis no CI.
- P02-03: validado — configuração/segredos da fundação.
- P02-04: validado — massa sintética A/B.

## O que não foi validado

- banco SQL;
- row-level security;
- autenticação real;
- isolamento real por tenant;
- storage;
- integrações externas;
- deploy/produção;
- teste visual em navegador real.

Essas fronteiras permanecem bloqueadas para os pacotes próprios. **G1 ainda não está fechado**, porque PAC-03 precisa provar persistência/diagnóstico/CI de dados.
