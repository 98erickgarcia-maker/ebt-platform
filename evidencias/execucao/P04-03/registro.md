# P04-03 — TenantContext a partir da identidade

Data: 07/10/2026.

Versão funcional validada: `f9492219407707e23ff7611c58e69ec4726e8dac`.

## Implementação

`CurrentIdentityTenantContext` resolve o usuário pelo `NameIdentifier` da sessão assinada e revalida o vínculo no catálogo conhecido pelo servidor.

O tenant usado pelo servidor vem do perfil encontrado pelo ID do usuário. Headers como `X-EBT-TENANT` e `X-Tenant-Id` não participam da resolução.

Perfis sem tenant ativo, como suporte técnico sintético, não recebem contexto de tenant.

## Prova

No teste HTTP, a sessão de `admin.orbe@demo.invalid` enviou headers adulterados apontando para Nexo; `/api/auth/me` continuou retornando `tenantKey=orbe`.

O workflow QA `37697473874` também autenticou Orbe antes da gravação e manteve o tenant derivado da identidade.

## Cenários

- P04-03-C01 — header/body adulterados não trocam empresa: **validado**.
- P04-03-C02 — usuário sem vínculo não governa recurso de tenant: **validado pela matriz/contexto do suporte técnico**.
- P04-03-C03 — contexto não deriva de nome visual: **validado**; resolução usa UserId e catálogo servidor.

## Limite

O catálogo ainda é sintético. Membership persistida e onboarding real entram no fechamento de G-SEG.
