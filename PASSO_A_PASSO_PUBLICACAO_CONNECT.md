# Primeira entrega online do EBT Connect

07/10/2026. Versão vigente 0.1.5 publicada e verificada: [https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io](https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io).

## Acesso

1. Abra a URL HTTPS. O navegador do Codex foi deixado autenticado como administrador da EBT Enterprise.
2. Para entrar em outro navegador, use o e-mail do administrador cadastrado; o acesso inicial está no arquivo privado local `tmp/private-integrations/connect-production.json`, seção Bootstrap. A senha não acompanha ZIP/Git/chat.
3. Leia [guia de uso](PASSO_A_PASSO_EBT_CONNECT.md) e [API](docs/api/CONNECT_V1.md). Contatos reais não foram importados; sua empresa começa vazia.

## Destino confirmado

Aplicação ebt-connect-hml, ambiente existente cae-crm-casst-prod, registro existente acrcrmcasstprod2608.azurecr.io, Brazil South. Consumo mínimo: 0,25 vCPU, 0,5 GiB e uma réplica. O usuário autorizou publicação com valor variável depois da restrição anterior de R$30 fixos; esta não limita mais a hospedagem. Não foi contratado outro banco nem alterado SKU.

Banco pago existente sqldb-crm-casst-dev-v2, schema ebt_connect. Identidade id-ebt-connect-hml: acesso somente ao schema próprio e leitura da imagem. Outros produtos continuam independentes. Certificado privado cifra o keyring SQL, com backup DPAPI no computador; preservar certificado e senha na recuperação.

## Provas desta entrega

26 verificações HTTP ao vivo: TLS/health, login/cookie, cadastro/idempotência, histórico, tarefa/próxima ação, empresas A/B/ID direto, CSRF, assinatura/duplicata/conflito de callback, logout/revogação. Reinício real da revisão preservou a sessão anterior. SQL: keyring persistido e cifrado, grants limitados, catálogo dos outros schemas igual ao original. Fixtures A/B desativadas depois da prova; não aparecem no acesso do administrador real.

Webhook WazVox criado para message.received e message.status em `https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io/webhooks/connect/wazvox/wz-ebt`. Chave/assinatura privadas no host, processamento ativado. A conversa de teste real recebeu texto, respondeu pelo Connect e teve retorno de leitura confirmado no provedor e no Connect. A correção 0.1.5 aceita `data.id` com referência `wamid.` e `recipient_id` observados nos callbacks reais. Três callbacks preservados foram reprocessados, sem novo envio. [Prova real, dez verificações](evidencias/connect_wazvox_real_015.json). O callback sintético anterior conserva seu cenário e não foi usado como prova de origem real.

- [Prova HTTP e reinício](evidencias/connect_primeira_entrega_online.json).
- [Prova de permissões e keyring](evidencias/connect_sql_runtime_verificado.json).
- [Publicação e destino](evidencias/azure_connect_publicacao.json).

## Continuidade do plano

Probes HTTP/SQL de disponibilidade publicados na revisão 0.1.4; teste negativo com SQL indisponível. Fluxo real de texto WazVox demonstrado na 0.1.5, com recebimento, resposta, entrega e leitura. Próximos passos: scanner privado de documentos, ensaio de recuperação Azure, CI hospedada e aceite de negócio. Documento pode ser carregado como pendente; aprovação em produção exige scan clean da versão. Não promover os 238 casos planejados automaticamente. Preservados 180h de entregas e 20h de reserva, sem horas reais inventadas.

## Recuperação

Use imagem anterior do Connect e a mesma identidade/configuração/keyring; não restaurar nem excluir o banco compartilhado como rollback da aplicação. Cópias privadas de certificado/credenciais estão em tmp/private-integrations/connect-production.dpapi, protegidas para o usuário Windows atual. Repetir ready/login após troca de revisão. Nunca copiar credenciais para o frontend, contexto ACR ou ZIP.
