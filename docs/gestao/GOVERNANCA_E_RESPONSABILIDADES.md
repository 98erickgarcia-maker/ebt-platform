# Governança e responsabilidades propostas

## Papéis

Os papéis abaixo ainda precisam de pessoas confirmadas. O registro não atribui obrigações a Thaiane, Erick, CASST, Vikings ou cliente por inferência.

| Papel | Responsabilidade | Evidência |
|---|---|---|
| Responsável pelo projeto EBT | Priorizar escopo, resolver decisões e acompanhar orçamento | Registro de decisão e mudança |
| Desenvolvimento EBT | Executar recorte, preservar fontes, registrar versão e resultado | PR/commit e ficha de entrega |
| Revisão técnica | Conferir contrato, segurança, migração e consequências em consumidores | Parecer proporcional ao recorte |
| Responsável de negócio | Confirmar fluxo/campos/resultado esperado | Critérios e motivo das decisões |
| Usuário piloto | Executar cenários e registrar aceite ou rejeição | Ficha de homologação com autoria/data |
| Operação | Preparar ambiente, recuperação e diagnóstico | Runbooks e ensaios |

Uma mesma pessoa pode acumular funções quando adequado, mas não se deve inventar revisão independente ou aceite de cliente. A equipe real e a disponibilidade devem ser registradas antes do piloto operacional.

## Entrada, saída e pausa de trabalho

Entrada: ticket identificado, dependências satisfeitas, fonte congelada, ambiente permitido e critério verificável. Saída: resultado, commit/hash, cenário, ambiente, evidência sanitizada, limitação e tempo real. Impedimento: natureza, dono proposto, próximo passo e recortes que ainda podem avançar.

Um impedimento de site não bloqueia automaticamente CRM. Falha de isolamento compartilhado impede todos os consumidores dessa fronteira. A reserva pode ser usada desde a primeira fase. Não registrar horas de espera como trabalho feito quando ninguém trabalhou.

## Estados

planejado -> em_execucao -> em_verificacao -> demonstrado_qa -> homologado_usuario -> liberado. bloqueado exige causa e dependência. Um caso falho retorna ao trabalho/verificação; um gate aprovado para uma versão não autoriza outra versão sem avaliar o diff.

demonstrado_qa exige registro verificável. homologado_usuario exige autoria, instante e cenário do usuário. liberado exige pacote/ambiente definido e, quando houver implantação, a prova específica da implantação. As duas últimas condições não foram satisfeitas pelo planejamento.

## Controle de esforço

Horas do ticket já incluem implementação, verificação e registro. Registrar horas reais separadamente das estimadas. Trabalho extra deve ter causa e ticket/reserva associados. Não somar as mesmas quatro horas ao ticket original e à reserva. O template de esforço registra um identificador único por sessão para permitir reconciliação.

## Rotina de fechamento

1. Conferir resultado e cenário do ticket.
2. Registrar tempo real e alteração de trilha, se houver.
3. Atualizar a fonte de status do backlog com a prova correspondente.
4. Executar verificadores documentais e revisar diff.
5. Fechar gate quando todas as dependências e casos aplicáveis passaram.
6. Salvar no GitHub o conteúdo revisado, sem presumir deploy ou envio.
