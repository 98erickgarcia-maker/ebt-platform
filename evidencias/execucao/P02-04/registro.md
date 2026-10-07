# P02-04 — massa sintética A/B

Data: 07/10/2026.

Versão executada: `03e0928d2670fe14fa7d96c20037efee0ddbcab7`.

## Consumidores sintéticos

### A — Orbe

- chave: `orbe`;
- nome: `Orbe Industrial Demo`;
- tenant ID determinístico: `11111111-1111-4111-8111-111111111111`.

### B — Nexo

- chave: `nexo`;
- nome: `Nexo Serviços Demo`;
- tenant ID determinístico: `22222222-2222-4222-8222-222222222222`.

Usuários e contatos são fictícios. O frontend usa endereços `.invalid` para evitar confusão com e-mail real.

## Prova automatizada

Teste `Synthetic_consumers_are_distinct_and_reproducible` verifica:

- exatamente dois perfis;
- tenant IDs diferentes;
- chaves diferentes;
- marca de configuração compartilhada;
- usuários sintéticos ativos.

A suíte backend terminou com **3/3 testes aprovados**; a suíte frontend com **11/11**.

## Casos

- P02-04-C01 — dados próprios em A/B: **validado no catálogo sintético**.
- P02-04-C02 — cópia de cadastro real ausente: **validado por construção do fixture e nomes/domínios fictícios**.
- P02-04-C03 — fixtures reproduzíveis: **validado**; IDs e dados estão versionados e determinísticos.

## Limite

Isto não prova isolamento de linha SQL. Essa prova pertence ao PAC-03 e aos pacotes de tenant/segurança.
