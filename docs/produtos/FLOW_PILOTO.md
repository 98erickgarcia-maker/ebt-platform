# Pacote 4: protocolo e tramitação mínima

## Delimitação

Novo fluxo, tickets P08-01 a P08-08, 24h de capacidade estimada após os gates de segurança, documentos e tarefas. Um tipo de protocolo, numeração por tenant/ano e três estados fixos. Marco até 164h cumulativas, sujeito ao reaproveitamento e à reserva.

## Estado e ação candidata

| Estado atual | Ação | Próximo estado | Requisitos |
|---|---|---|---|
| Ausente | Abrir protocolo | Aberto | Interessado/responsável válidos, tipo/ano, chave da operação |
| Aberto | Iniciar análise | Em análise | Ator autorizado no recurso e versão vigente |
| Em análise | Concluir | Concluído | Resultado, ator autorizado e versão vigente |
| Concluído | Consultar | Concluído | Consulta autorizada; não modifica decisão |

Outras transições ficam negadas no piloto até especificação própria. Reabertura/rejeição/despacho complexo não são acrescentados por estética. O responsável de negócio confirma esta tabela em P08-01.

## Consistência

Número visível não substitui ID interno. Sequência e abertura são transacionais em SQL com unicidade por escopo. Mesma chave/payload retorna o protocolo existente; chave incompatível não cria duplicata. Interessado, documento e responsável de outra empresa são recusados. Estado e movimento confirmado mantêm coerência; versão obsoleta retorna conflito.

## Cenários

Criações concorrentes; reenvio após resposta perdida; duas pessoas tramitem o mesmo registro; estado inválido; usuário consulta tentando alterar; ID de B; anexo privado; falha transacional; reload e restart. SQL real é necessário para índice/concorrência; execução em memória não satisfaz G-FLOW.

## Limite de produto

O recorte é uma tramitação fixa com parte das capacidades iniciais W1/W2. Não implementa W3/W4, designer, condições dinâmicas, timers, e-SIC, sigilo público regulado ou assinatura. Se segurança/reuso consumirem a reserva, transportar este pacote ao ciclo seguinte e não declará-lo entregue.
