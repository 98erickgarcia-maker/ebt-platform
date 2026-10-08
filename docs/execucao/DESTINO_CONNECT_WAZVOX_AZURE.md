# Destino EBT Connect e WazVox

07/10/2026: primeira entrega online em [https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io](https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io). Banco pago existente sqldb-crm-casst-dev-v2, schema ebt_connect, sem novo banco/SKU. Container App próprio no ambiente/registro existentes, identidade id-ebt-connect-hml com DML somente no schema próprio. Recursos: 0,25 vCPU, 0,5 GiB, uma réplica; valor variável autorizado pelo usuário posteriormente à limitação fixa.

Oito migrations aplicadas anteriormente. Bootstrap real realizado com administrador da EBT; fixtures técnicas criadas em empresas próprias e desativadas após os testes. Keyring SQL cifrado por certificado privado, sessão preservada após reinício, proxy restrito aos endereços observados. Regra temporária do firewall removida. Outros schemas com catálogo preservado.

WazVox: assinatura específica criada e armazenada privadamente, callback público instalado para message.received/message.status, canal conferido e processamento ativado. Recebimento, resposta pela API e leitura reais demonstrados na 0.1.5. O contrato real usa data.id com referência wamid e recipient_id; três callbacks preservados foram reprocessados sem novo envio. [Prova real](../../evidencias/connect_wazvox_real_015.json). Histórico não foi importado, callbacks de outros produtos foram preservados. Acesso direto Meta ao portfólio permanece pendente.

[Guia de publicação](../../PASSO_A_PASSO_PUBLICACAO_CONNECT.md) · [Prova ao vivo](../../evidencias/connect_primeira_entrega_online.json) · [SQL próprio](../../evidencias/connect_sql_runtime_verificado.json).
