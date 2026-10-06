# ADR-003: arquivo privado e decisão por versão

Status: desenho candidato a confirmar em P06. Contexto: banco guarda metadado e storage guarda bytes; os dois não compartilham necessariamente a mesma transação.

Decisão recomendada: upload inicialmente pendente, hash dos bytes efetivos, autorização por recurso no download e revisão associada à versão exata. Falha fora da transação não produz sucesso falso; reconciliação/compensação fica explícita. Restore abrange banco, binários e chaves necessárias.

Alternativas inadequadas: arquivo público com link secreto como única proteção; sobrescrever aprovação passada; chamar aprovação interna de assinatura digital; backup apenas SQL sem conferir bytes.

Consequência: scan/política de liberação ausentes mantêm restrição; provedor privado real é escolhido em P02-05/P06. Tickets: P06-01 a P06-08/P09-06.
