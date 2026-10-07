# ADR-005: Core inicial da EBT Platform

Status: **em verificação no PAC-02**.

## Contexto

O repositório `ebt-platform` continha planejamento e evidências, mas ainda não possuía runtime do produto. O PAC-01 congelou o primeiro recorte e definiu o EBT Connect como módulo inicial de relacionamento.

A plataforma precisa de uma base executável que preserve a direção já aprovada (.NET, React/TypeScript e SQL), sem copiar integralmente sistemas-fonte e sem antecipar microserviços, filas ou cache distribuído.

## Decisão

Adotar **monólito modular mínimo** com fronteiras explícitas:

- `Ebt.Domain`: modelos e invariantes que não dependem de UI ou infraestrutura;
- `Ebt.Application`: contratos de caso de uso e configuração;
- `Ebt.Infrastructure`: implementações de persistência/adapters; no PAC-02 contém somente catálogo sintético;
- `Ebt.Api`: composição HTTP e health;
- `src/frontend`: React/TypeScript/Vite com Design System EBT;
- `tests/Ebt.Foundation.Tests`: testes da fundação.

Stack inicial:

- .NET 10 / SDK fixado por `global.json`;
- React 19 + TypeScript 6 + Vite 8;
- SQL Server/Azure SQL permanece direção para PAC-03, não é simulado como pronto no PAC-02.

## Limites

PAC-02 não implementa:

- autenticação/tenant real;
- banco SQL;
- documentos/storage;
- CRM persistente;
- automação de mensagens;
- proposta/financeiro/OS;
- integrações externas.

Os endpoints `/api/foundation/consumers` são estritamente para dados sintéticos e ficam desligados fora de Development pela configuração padrão.

## Segurança de configuração

Nenhum segredo é versionado. Produção exige explicitamente a presença de configuração privada e falha com mensagem genérica caso ela não exista. Development não consulta segredo de produção.

## Consequências

Positivas:

- primeira árvore real e reproduzível da plataforma;
- fronteiras compatíveis com extração gradual;
- dois consumidores sintéticos sem dados reais;
- Design System começa na própria EBT Platform.

Trade-offs:

- duplicação de alguns conceitos pode existir até o segundo uso provar a abstração;
- persistência/tenant continuam pendentes até os pacotes próprios;
- a UI desta fase demonstra estrutura e estados, não funcionalidade comercial persistida.

## Alternativas rejeitadas

- copiar integralmente o CRM-fonte: acopla marca e regras específicas;
- reescrever tudo em outra stack: retrabalho sem benefício demonstrado;
- microserviços/filas/Redis agora: complexidade sem requisito medido;
- usar banco/contatos reais no bootstrap: viola isolamento do pacote e aumenta risco.
