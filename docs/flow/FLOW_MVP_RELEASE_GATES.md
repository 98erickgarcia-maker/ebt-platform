# EBT Flow — primeiro recorte executável (candidato, não implantado)

Base da branch: PR #22 (FLOW + AURA visual) que depende do PR #15 (navegação mobile).
Esta branch não modifica as tabelas, credenciais ou schemas da CASST.
O SQL é uma migração **separada e manual**, NÃO executada por nenhum inicializador de produção.

## Escopo técnico incluído
- `GET /api/flow/v1/protocols`: até 100 registros, filtrados por tenant e carteira.
- `POST /api/flow/v1/protocols`: assunto + Idempotency-Key, número sequencial por tenant/ano, gravação transacional e movimento.
- `POST /api/flow/v1/protocols/{id}/transition`: transição open→in_review→complete, If-Match e resultado obrigatório ao concluir.
- EBT AURA é a linguagem visual (não aplicação independente); EBT FLOW é o motor de protocolos e tramitação.

## Obrigações antes de liberar
1. Revisão independente do isolamento de tenant/carteira, idempotência, concorrência e permissões.
2. Em banco SQL **exclusivo de QA**, aplicar o SQL duas vezes, testar criação simultânea, replay de chave, mismatch, If-Match incorreto, tenant B, carteira alheia, leitor e rollback.
3. Nunca marcar Flow disponível no catálogo e nunca publicar antes de build .NET, CI e integração UI completos.
4. O sistema original Connect 0.3.0 permanece publicado; esta branch é apenas candidata.
5. A autorização de deploy ou migração para produção é etapa separada.
