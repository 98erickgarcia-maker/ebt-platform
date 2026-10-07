# P04-02 — sessão/login com limites claros

Data: 07/10/2026.

Versão funcional validada: `f9492219407707e23ff7611c58e69ec4726e8dac`.

## Implementação

- cookie `ebt.session` HttpOnly;
- SameSite Strict;
- sessão não persistente;
- expiração candidata de 30 minutos;
- logout invalida o cookie;
- login sintético exige código privado e só existe em Development/QA;
- Production responde 404 ao endpoint de login sintético;
- headers de debug não autenticam requisições.

## Prova

Run de fundação `37697473804`: **success**.

Testes incluem:

- login sintético válido;
- leitura de `/api/auth/me`;
- logout e acesso posterior negado;
- claim de sessão expirada recusada;
- headers debug sem cookie continuam 401;
- endpoint de login sintético indisponível em Production.

## Cenários

- P04-02-C01 — sessão válida acessa o recorte: **validado**.
- P04-02-C02 — expirada é negada: **validado na validação de claim de sessão**.
- P04-02-C03 — mecanismo debug fora de Dev/QA não autentica: **validado**.

## Limite

Esta identidade é sintética para QA/Development. Não é o provedor de identidade de produção e não fecha G-SEG.
