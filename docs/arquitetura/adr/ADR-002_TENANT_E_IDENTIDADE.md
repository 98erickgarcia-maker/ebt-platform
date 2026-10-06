# ADR-002: empresa e escopo resolvidos no servidor

Status: direção de proteção do planejamento; desenho concreto a confirmar em P04. Contexto: trocar de cliente/tenant é uma nova fronteira mesmo quando o código veio de fonte validada.

Decisão recomendada: contexto derivado de identidade/vínculo ativo, autorização por ação/recurso, índices e cache compatíveis com o tenant. SQL real deve provar negativas e concorrência pertinentes. O modo DevHeader da fonte não deve autenticar fora de Development.

Alternativas rejeitadas para o recorte: TenantId editável como autoridade, isolamento só por UI, cache global sem escopo, admin técnico com acesso irrestrito. Consequência: G-SEG bloqueia consumidores quando há vazamento. Cookie/OIDC/JWT/provedor permanecem escolha específica, sem inventar um novo mecanismo de login.

Revisitar separação por banco se risco/contrato/carga exigir; não está comprometida no ciclo inicial. Tickets: P04-01 a P04-12.
