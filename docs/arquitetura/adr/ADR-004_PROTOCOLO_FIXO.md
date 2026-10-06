# ADR-004: protocolo com fluxo fixo antes do engine

Status: proposta de recorte a confirmar em P08-01. Contexto: um engine configurável excede a capacidade reservada ao primeiro Flow.

Decisão recomendada: um tipo, estados abertos/em análise/concluídos, ator definido, número único por tenant/ano e mudança de estado/histórico coerentes. Concorrência e idempotência são provadas no SQL real. Não usar max+1 sem proteção.

Alternativas adiadas: designer, branching, formulários dinâmicos, timers, W3/W4 e portal externo. Consequência: produto é piloto manual delimitado; futuras capacidades recebem novo escopo. Se a reserva se esgotar, adiar este pacote em vez de cortar testes de segurança.

Tickets: P08-01 a P08-08. Reavaliar após demanda recorrente e resultado do piloto.
