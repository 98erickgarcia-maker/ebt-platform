# P04-01 — matriz usuário, empresa e ação

Data: 07/10/2026.

Versão funcional validada: `f9492219407707e23ff7611c58e69ec4726e8dac`.

## Implementação

A matriz candidata está em `docs/seguranca/MATRIZ_ACESSO_CANDIDATA.md` e no código `EbtAccessMatrix`.

Papéis:

- Administrador: leitura, gravação e download;
- Operador: leitura, gravação e download;
- Consulta: leitura e download, sem gravação;
- Suporte técnico: sem acesso automático a registro/anexo do tenant.

## Prova

A suíte backend do run `37697473804` terminou com **17/17 testes aprovados**.

Os testes parametrizados validam as três operações do recorte para cada papel.

## Cenários

- P04-01-C01 — permissão definida por operação: **validado**.
- P04-01-C02 — negativa explícita: **validado**.
- P04-01-C03 — técnico não recebe documento restrito automaticamente: **validado na matriz do recorte**.

## Limite

A matriz cobre a fundação atual. Autorização por recurso completa e documentos privados gerais pertencem aos PAC-06/PAC-07.
