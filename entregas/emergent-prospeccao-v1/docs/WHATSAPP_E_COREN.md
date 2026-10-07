# WhatsApp oficial e oportunidade COREN-ES

## Edital verificado

Foi localizado e baixado o [edital completo oficial no PNCP](https://pncp.gov.br/pncp-api/v1/orgaos/08332733000135/compras/2026/26/arquivos/3), documento ativo 3, publicado no PNCP em 30/09/2026. O PDF tem 52 páginas. [Página da contratação](https://pncp.gov.br/app/compras/08332733000135/2026/26). Consulta efetuada em 07/10/2026; retificações posteriores precisam ser verificadas antes de participar.

A capa confirma Pregão 18/2026, R$90.000 estimados e sessão de 14/10/2026 às 09h de Brasília. O Termo de Referência, página física 18, descreve período de 12 meses, 1 milhão de mensagens sob demanda, R$0,09 unitário, mínimo de três usuários e um canal/número. A mesma especificação menciona envio ilimitado. R$0,09 é preço de referência do item contratado, não uma tarifa universal da Meta.

O TR, itens 3.1.1–3.1.6 (página física 19), inclui licenciamento, API oficial, suporte, treinamento quando necessário, automação/atendimento e hospedagem/armazenamento. O edital, item 4.3, determina inclusão dos custos operacionais e encargos na proposta. Inferência de precificação: não contar com reembolso separado de tarifas/API/BSP sem previsão expressa esclarecida pelo órgão. O documento consultado não resolveu a composição específica da tarifa Meta nem a regra de excedente.

O TR 3.2/4.6 e outros anexos exigem selo/verificação da Meta para a contratada. Isso precisa ser esclarecido por escrito: verificação de empresa no Business Manager, conta oficial/OBA, condição de parceiro/provedor ou outra certificação não são automaticamente equivalentes. A entrega deste código não concede selo nem prova habilitação.

## O que verificar antes de montar o preço

- O que é uma mensagem faturável: aceita, enviada, entregue, recebida, template, atendimento ou tentativa? Qual é a evidência de medição?
- Se R$0,09 inclui tarifas Meta/BSP, plataforma, implantação, suporte, treinamento, hospedagem e impostos. Os componentes de software/operação aparecem no TR; o mecanismo de repasse da tarifa precisa ser confirmado.
- Como conciliar “ilimitado” com 1 milhão sob demanda; política de excedente, categorias Meta e câmbio/reajuste.
- Que documento comprova exatamente o selo exigido e em que fase. Não afirmar que EBT já atende a exigência.
- SLA de implantação/suporte/disponibilidade, backups, recuperação, retenção e exportação; número de usuários e filas; propriedade do número, WABA e dados.

O TR 4.10–4.18 inclui bot, automações, integração, múltiplos atendentes, histórico, notificações, templates/mídias e relatórios. O TR 4.20–4.25 trata dados do órgão, restrição de uso, opt-in/out, perfis de acesso e infraestrutura. A extensão entregue contém uma base de prospecção/e-mail e conector WhatsApp para aprendizado; não cobre integralmente plataforma multiatendente nem garante escala de um milhão de mensagens. Os pedidos 3 e 4 de `PEDIDOS_EMERGENT.md` delimitam esses próximos trabalhos.

## Aprender automações sem gastar com IA

1. Configurar aplicativo Meta, WABA e número de teste oficial. Definir webhook HTTPS e validar seu desafio/assinatura. A [política oficial](https://www.whatsapp.com/legal/business-policy/) é referência para opt-in e passagem para humano.
2. Receber mensagem de teste e guardar `wamid`, número da conta, remetente e data. Repetir o webhook e confirmar que ele não duplica o registro. O pacote já implementa essa deduplicação.
3. Criar template de apresentação/apresentação solicitada no WhatsApp Manager; aguardar a aprovação e usar seu nome, idioma e parâmetros. Template textual local ainda não é template Meta aprovado.
4. Solicitar o template pelo conector com confirmação e evidência de opt-in. A resposta da API indica aceitação; aguardar `sent`, `delivered` e `read` pelo webhook. Esses eventos são separados e podem chegar fora de ordem.
5. Acrescentar regras de menu: “1 — serviços”, “2 — orçamento”, “3 — atendente”. Nenhuma IA é necessária. Persistir estado da conversa e sair da automação quando o humano assumir.
6. Automatizar respostas somente dentro da janela válida e segundo a política. Fora dela, usar template aprovado quando permitido. Respeitar “parar/sair” e nunca contornar limitação com WhatsApp Web/QR.
7. Depois acrescentar filas/perfis/auditoria/relatórios e testes de carga/recuperação. Somente evidência específica pode sustentar capacidade contratual.

## Modelo de custo para a oportunidade

Preço anual precisa cobrir: mensagens por categoria/mercado e taxas BSP, infraestrutura/storage/backup, implantação, suporte/SLA, manutenção, impostos e margem. Dividir R$90.000 por 12 dá R$7.500 mensais de receita de referência antes desses custos; dividir pelo milhão dá R$0,09 como teto médio estimado do conjunto. Não usar os dois números como garantia de margem ou faturamento integral, porque a demanda, medição e composição precisam ser esclarecidas.

Os [preços oficiais da plataforma](https://business.whatsapp.com/products/platform-pricing) informam cobrança por mensagens entregues, categorias e situações de gratuidade. A calculadora do pacote aceita uma tarifa média informada e torna as premissas visíveis; não contém uma tabela inventada de preços Meta.
