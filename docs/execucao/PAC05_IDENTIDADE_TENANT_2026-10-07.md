# PAC-05 — Identidade e escopo de tenant

Data: 07/10/2026.

Status: **implementado e validado no recorte candidato**.

Versão funcional: `f9492219407707e23ff7611c58e69ec4726e8dac`.

## Workflows

- planejamento: `37697473803` — success;
- fundação: `37697473804` — success;
- persistência QA: `37697473874` — success.

## Resultado

A EBT Platform agora possui uma fronteira candidata de identidade/tenant que:

- autentica perfis sintéticos somente em QA/Development;
- usa cookie de sessão;
- mantém expiração e logout;
- deriva tenant da identidade conhecida pelo servidor;
- ignora headers/body para escolher tenant;
- aplica matriz de acesso;
- filtra leitura/listagem/download por tenant;
- grava usando o tenant do contexto, não o recebido no JSON;
- prova negativa A/B com SQL Server + Blob reais de QA.

## Resultados do CI

### Fundação

- backend: **17/17 testes**;
- frontend: **15/15 testes**;
- lint: 0 warnings / 0 errors;
- auditoria npm: 0 vulnerabilities;
- auditoria .NET: nenhum pacote vulnerável reportado.

### Persistência QA

- SQL Server e Azurite: inicializados;
- teste de persistência: **1/1 aprovado**;
- login Orbe: aprovado;
- salvar/reler/download Orbe: aprovado;
- tentativa Nexo -> ID Orbe: 404;
- listagem Nexo: vazia para o registro de Orbe;
- auditoria de dependências/diff: aprovada.

## Estado dos tickets

- P04-01: validado no recorte;
- P04-02: validado para sessão sintética QA/Development;
- P04-03: validado no contexto servidor;
- P04-04: validado para create/read/list/download do registro de fundação.

## Gate

**G-SEG permanece pendente.**

Faltam, entre outros:

- migration e índices finais;
- RLS SQL;
- autorização por recurso;
- isolamento de cache/troca de perfil;
- auditoria;
- CSRF/session hardening final;
- onboarding A/B real do recorte.
