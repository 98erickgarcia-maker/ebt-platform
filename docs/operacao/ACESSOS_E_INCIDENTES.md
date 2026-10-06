# Runbook candidato: acesso e incidente

## Acesso

Confirmar organização, vínculo, perfil, carteira e categoria de documento. Convite individual tem uso/expiração/revogação conforme implementação; usuário define própria senha. Não criar conta real presumida, senha compartilhada ou aprovação em nome de terceiro. Suporte recebe diagnóstico minimizado, não acesso clínico/administrativo irrestrito.

## Incidente

1. Registrar ação, URL/rota sem dados sensíveis, instante, perfil/contexto, status e traceId.
2. Distinguir esperado, observado e tipo: acesso, persistência, arquivo, migração, contrato ou serviço externo.
3. Reproduzir em QA com massa sintética, preservando a fonte e o resultado original.
4. Avaliar consumidores e dados afetados. Vazamento de tenant/categoria suspende a capacidade afetada até conter e provar correção.
5. Aplicar menor correção adequada; registrar teste pertinente e efeito em migration/contrato/cache.
6. Repetir o cenário e regressões afetadas; usar reserva se houver trabalho extra registrado.
7. Fechar com causa, versão corrigida, resultado, medida preventiva e pendências.

Falha simulada prova recuperação da simulação, não reprodução do incidente histórico. Erro “SQL” não determina causa sozinho. Notificação ao usuário/cliente, quando necessária, depende de autorização e destinatário definidos; este runbook não envia mensagens.
