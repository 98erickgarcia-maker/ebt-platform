# P02-06 — cliente HTTP e padrões de erro

Data: 07/10/2026.

Versão funcional validada: `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

Fonte técnica consultada: `crm-casst-web/src/frontend/src/api/http.ts`, blob `ddfa728f7936b59f52adddf88ca43051ce4ae699` na ref congelada do G0.

## Adaptação realizada

Foram reaproveitados como padrão, e não por cópia integral:

- resposta de problema HTTP;
- tratamento explícito de 401;
- erro de rede;
- validação de resposta antes de declarar sucesso;
- diagnóstico de download inválido.

Autenticação, sessão, CSRF e cliente autenticado completo **não foram trazidos para esta fase**, porque pertencem aos pacotes de segurança/tenant.

## Testes frontend

`src/frontend/src/api/http.test.ts` verifica:

1. 401 retorna erro de tipo `unauthorized`;
2. erro HTTP não é convertido em sucesso;
3. payload do chamador permanece intacto após falha;
4. resposta JSON não é aceita como download;
5. arquivo só é retornado após resposta válida e conteúdo não vazio.

Na suíte final da fundação:

- 2 arquivos de teste aprovados;
- **15 testes aprovados / 0 falhas**;
- lint com **0 warnings / 0 errors**;
- build TypeScript/Vite aprovado.

## Cenários

- P02-06-C01 — 401 tratado: **validado**.
- P02-06-C02 — erro não vira sucesso: **validado**.
- P02-06-C03 — download inválido tem diagnóstico seguro: **validado**.

## Limite

O comportamento de autenticação real, renovação de sessão e CSRF permanece pendente. Este ticket valida o contrato de erro do recorte de fundação, não uma sessão autenticada final.
