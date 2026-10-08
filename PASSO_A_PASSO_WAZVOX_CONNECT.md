# EBT Connect — integração WazVox

**Estado vigente de 07/10/2026:** primeira entrega publicada e 26 verificações ao vivo aprovadas. [Acesso e provas](PASSO_A_PASSO_PUBLICACAO_CONNECT.md). Banco pago compartilhado preservado; valor variável autorizado posteriormente. Referências abaixo a host inexistente/F1/R$30 fixos descrevem o cenário anterior e foram superadas por esta publicação. Fluxo real de texto WazVox demonstrado na 0.1.5; scanner, CI hospedada, restore Azure e aceite continuam pendentes.


Atualização 0.1.5: aplicativo online, canal e assinatura WazVox instalados, keyring SQL cifrado. Recebimento e resposta reais de texto demonstrados; callbacks de envio, entrega e leitura observados. Contrato de status corrigido e três retornos preservados reprocessados sem reenvio. Ver [prova real](evidencias/connect_wazvox_real_015.json) e [publicação e uso](PASSO_A_PASSO_PUBLICACAO_CONNECT.md).

## Resultado

Adaptador WazVox implementado em código e verificado com dados sintéticos. A chave real **EBT Connect** foi criada no workspace EBTenterprise e usada para três consultas HTTP 200: conta, números e assinaturas. Nenhuma mensagem real foi enviada e nenhum callback público foi registrado. Meta está autenticada, mas sem acesso ao portfólio da WABA mostrada pelo WazVox.

## Como funciona

O provedor chama `POST /webhooks/connect/wazvox/{appKey}`, com `appKey` começando por `wz-`. O Connect verifica assinatura HMAC SHA-256 sobre `timestamp + '.' + corpo bruto`, janela de cinco minutos, versão `1`, workspace configurado e igualdade entre `eventId` e `X-BSP-Event-Id`. Guarda o envelope cifrado e confirma `200` somente após o commit. O mesmo ID/corpo retorna sucesso sem duplicar; ID repetido com outro corpo retorna `409`.

O worker converte `message.received` de texto para o processamento comum, resolve empresa/carteira pelo canal cadastrado e coloca eventos incompatíveis em quarentena. `message.sent` do Business App fica fora deste recorte e não abre a janela de resposta. O nome do contato do provedor não é importado automaticamente. Histórico antigo/contatos reais não foram importados.

A resposta continua no contrato Connect: `202` após fila persistida, `200` na repetição da mesma operação, consulta posterior de status. Para WazVox, o backend envia `phoneNumberId/to/type/text`, Bearer privado e `Idempotency-Key: ebt-connect-{operationId}`. Exige janela de 24h. Timeout/erro ou resposta sem `waMessageId` fica `unknown`, sem reenvio automático. O status definitivo exige callback e referência WhatsApp válidos; `accepted` não prova entrega.

## Pré-requisitos reais

HTTPS público do Connect, SQL existente com migration aplicada, administrador/operador/carteira definidos, keyring recuperável, chave WazVox privada e signing secret da assinatura exclusiva. Preparação do Azure e impedimentos em [destino de homologação](docs/execucao/DESTINO_CONNECT_WAZVOX_AZURE.md).

No secret store configurar `WazVox__Enabled`, `WazVox__Apps__wz-ebt__WorkspaceId`, `WazVox__Apps__wz-ebt__SigningSecret` e `WazVox__Connections__ebt-wazvox__ApiKey`. Com `Channel__TenantId/OperatorId/Portfolio/AppKey/AccountId/PhoneNumberId/SecretRef/Name` corretos, executar `dotnet Ebt.Platform.Api.dll --configure-wazvox`. O comando verifica conta/número na API e recusa canal duplicado, workspace diferente ou número desconectado. Não executa migrations nem cria banco.

## Repetir as verificações

1. Consultas reais, sem envio: `powershell -NoProfile -File scripts/Inspect-WazVox.ps1`. Lê a chave DPAPI privada deste usuário; não imprime chave nem conteúdo de mensagens. Saída sanitizada em `evidencias/integracao_wazvox_leitura.json`.
2. Protocolo sem transmissão: definir `MSBuildEnableWorkloadResolver=false`; executar `dotnet run --project tests/WazVox.ProtocolTests`. Registro em `evidencias/testes_wazvox_protocol.json`.
3. QA SQL: aplicar `sql/connect-migrations.sql` **somente** na fixture local `EbtPlatformQa_20261007Migrated`; executar `python scripts/Prepare-WazVoxQa.py` e `powershell -NoProfile -File scripts/Start-WazVoxQa.ps1`. A configuração recusa chaves externas e usa dados sintéticos. Em outro terminal executar `python tests/integration/wazvox_qa.py`.
4. Regressão Connect: com a API local ativa, `python tests/integration/connect_qa.py`. Manter o serviço ativo até a conclusão da rodada.
5. Schema repetível: `python scripts/test_migration.py`. Recuperação local: `python scripts/test_recovery.py`. São bases sintéticas exclusivas; não substituem PITR Azure.

## Arquivos e segurança

Código: `WazVoxProtocol.cs`, `WazVoxEndpoints.cs`, `ConnectWorker.cs`, `MessagingEndpoints.cs`, `Provisioning.cs`, `Program.cs`, modelo/migration de identidade de evento. A migration altera somente `ebt_connect`; a chave e respostas privadas de inspeção ficam em `tmp/private-integrations`, ignorado pelo Git e com ACL restrita. DPAPI é vinculado ao usuário/máquina atual; esse arquivo não deve ser copiado para Linux nem para repositório.

A primeira inspeção falhou por quebra de linha no arquivo DPAPI; leitura agora remove espaços externos antes de decifrar. A preparação sintética inicialmente usou um nome de empresa incorreto; passou a usar os IDs da fixture. Uma rodada de regressão foi interrompida pelo reinício da API e foi repetida; não foi tratada como aprovação do produto.

## Limites e próximos gates

`message.status` foi observado no canal real em 07/10/2026 com `data.id` contendo `wamid.`, `data.status` e `data.recipient_id`. A correção 0.1.5 preserva a alternativa `data.waMessageId/status/to`, rejeita UUID interno como substituto da referência e rejeita aliases WhatsApp conflitantes. Mídia, templates, campanhas, chamadas, sincronização de contatos e mensagens espelhadas do Business App não estão entregues neste recorte. A janela e a autorização de envio também são conferidas pelo WazVox/Meta. Não revogar a chave sem avaliar os consumidores. Não criar callback apontando para localhost, domínio inexistente ou produto de outro cliente.

Se a resposta de envio se perder antes de fornecer `waMessageId`, o callback WazVox não traz no contrato consultado a referência interna da operação EBT. Os fatos de status ficam preservados, mas esse `unknown` exige conciliação operacional; não foi implementada atribuição por semelhança de texto/destinatário nem retry automático. O fluxo Meta direto de callback com referência opaca não comprova essa conciliação no WazVox.

Contrato público consultado em 07/10/2026: [OpenAPI WazVox](https://wazvox.com/openapi/wazvox-v1.json). [Guia base Connect](PASSO_A_PASSO_EBT_CONNECT.md).
