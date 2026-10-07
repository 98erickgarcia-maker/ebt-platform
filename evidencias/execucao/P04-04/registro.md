# P04-04 — escopo em consultas e gravações

Data: 07/10/2026.

Versão funcional validada: `f9492219407707e23ff7611c58e69ec4726e8dac`.

## Implementação

- POST ignora `tenantKey` enviado pelo cliente e grava com o tenant da identidade;
- GET por ID filtra por `Id + TenantKey`;
- listagem filtra por tenant;
- download filtra por tenant;
- autorização é avaliada no servidor antes da operação.

## Prova SQL/Blob real de QA

Workflow `37697473874`: **success**.

A prova executou SQL Server + Azurite efêmeros e confirmou:

1. login como Orbe;
2. header adulterado não altera `tenantKey`;
3. criação grava como Orbe;
4. reload e download como Orbe funcionam;
5. login como Nexo;
6. tentativa de consultar diretamente o ID de Orbe retorna **404**;
7. listagem de Nexo não inclui o registro de Orbe.

O teste de persistência também valida diretamente que `GetAsync(id, "nexo")` e download cruzado retornam nulo.

## Cenários

- P04-04-C01 — A não lê B: **validado no banco real de QA**.
- P04-04-C02 — listagem e ID direto equivalentes: **validado**.
- P04-04-C03 — mutação recebe tenant somente do servidor: **validado para criação do recorte**.

## Limite

RLS de banco, update/delete e autorização por recurso completa ainda pertencem ao PAC-06. G-SEG permanece pendente.
