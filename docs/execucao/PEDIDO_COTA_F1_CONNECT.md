# Pedido preparado de cota gratuita — EBT Connect

07/10/2026. Rascunho histórico; **não enviado ao suporte da Microsoft**. O usuário recusou o envio e confirmou manter o banco pago compartilhado. Não enviar esta solicitação nem contratar outra hospedagem por inferência dessa confirmação. A autorização de publicação permanece; hospedagem ainda não resolvida sob o limite de R$ 30 fixos.

## Texto proposto

Solicito a liberação de uma instância/plano Azure App Service **F1 (Free), Windows, na região Brazil South**, para homologação do EBT Connect em .NET 10. A consulta atual de usages da assinatura mostra F1 com limite 0 e uso 0. As tentativas de criação retornaram necessidade de cota 1; nenhum plano ficou criado.

A aplicação utilizará o banco Azure SQL pago já existente. Não solicito banco adicional, mudança de SKU do SQL, mudança nos recursos dos outros projetos ou contratação de suporte/plano pago. A necessidade é exclusivamente disponibilizar a cota gratuita F1. Se essa cota não puder ser liberada gratuitamente, solicito informar a restrição; não aplicar upgrade ou alternativa paga automaticamente.

## Escopo e execução

- Assinatura atual conferida por Azure CLI; identificador será fornecido no campo próprio do pedido autenticado, sem publicar credenciais.
- Região preferida: Brazil South; sistema: Windows; SKU: F1; cota solicitada: 1.
- Não alterar CASST, CRP, Thaiane, seus domínios, imagens, identidades ou configurações.
- A decisão de manter `sqldb-crm-casst-dev-v2` como banco compartilhado permanece vigente.
- O gasto adicional autorizado pelo usuário é somente R$ 30 fixos. Não contratar cobrança variável ou suporte pago.
- Nenhum destinatário/contato foi preenchido por inferência. Conferir os campos exigidos pelo canal de suporte depois da autorização para enviar.
- Liberação da cota não é garantida e não substitui publicação e testes HTTPS/login/webhook.

## Provas

[Rechecagem atual](../../evidencias/azure_connect_publicacao_rechecagem.json), [schema aplicado](../../evidencias/azure_connect_schema_aplicado.json), [banco compartilhado](../arquitetura/BANCO_PAGO_COMPARTILHADO.md) e [guia de publicação](../../PASSO_A_PASSO_PUBLICACAO_CONNECT.md).
