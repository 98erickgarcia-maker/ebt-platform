# PASSO A PASSO — EBT Platform PAC-05

## O que foi feito

O PAC-05 adicionou a primeira fronteira de identidade e tenant da EBT Platform, sem ativar identidade de produção.

## Fluxo candidato

```text
QA/Development login
  -> cookie de sessão
  -> UserId assinado
  -> catálogo servidor revalida usuário
  -> TenantContext obtém tenant/role
  -> matriz autoriza operação
  -> consulta/gravação usa TenantKey do contexto
```

Headers e JSON não têm autoridade para trocar tenant.

## Perfis sintéticos

- `admin.orbe@demo.invalid`
- `operador.orbe@demo.invalid`
- `consulta.orbe@demo.invalid`
- `admin.nexo@demo.invalid`
- `operador.nexo@demo.invalid`
- `consulta.nexo@demo.invalid`
- `suporte@demo.invalid`

O código de login QA vem exclusivamente da variável `EBT_QA_LOGIN_CODE`.

## Validação

Commit funcional: `f9492219407707e23ff7611c58e69ec4726e8dac`.

Runs:

- `37697473803` documentação;
- `37697473804` build/test/auditoria;
- `37697473874` SQL + Blob + API QA.

Todos concluíram com sucesso.

## Segurança observada

- produção não expõe login sintético;
- header debug não autentica;
- header de tenant não troca empresa;
- create ignora tenant enviado pelo cliente;
- Nexo não lê registro de Orbe por ID;
- Nexo não vê registro de Orbe na lista;
- suporte técnico não recebe permissão de conteúdo por padrão.

## Próximo passo

PAC-06:

1. migration/índices;
2. RLS real;
3. autorização por recurso;
4. isolamento de cache/sessão e troca de perfil.

Depois, PAC-07 fecha auditoria, cookies/tokens/CSRF, onboarding e G-SEG.
