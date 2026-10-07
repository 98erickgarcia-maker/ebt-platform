# P02-06 — cliente HTTP e padrões de erro

Data: 07/10/2026.

Versão validada: `3804302233cc72bfef29e5c5cbbb62f6aeb548be`.

## Implementação

Foi criado `src/frontend/src/api/http.ts` com:

- erro tipado `ApiError`;
- tratamento explícito de 401, 403 e 404;
- erro HTTP nunca vira sucesso;
- `traceId` preservado a partir do header;
- JSON aceito somente com content-type compatível;
- download rejeitado quando retorna JSON/HTML ou arquivo vazio.

O cliente não expõe corpo interno de erro ao usuário.

## Testes

`src/frontend/src/api/http.test.ts` cobre:

- 401 tratado e detalhe interno não vazado;
- 500 continua sendo falha;
- download inválido não é aceito como sucesso;
- JSON só é retornado após resposta confirmada.

Suíte frontend no run `37690576723`: **15/15 testes aprovados**.

## Cenários

- P02-06-C01 — 401 tratado: **validado**.
- P02-06-C02 — erro não vira sucesso: **validado**.
- P02-06-C03 — download inválido possui diagnóstico seguro: **validado**.

## Limite

Autenticação real ainda não existe. O teste valida o contrato do cliente HTTP para quando a camada autenticada for conectada.
