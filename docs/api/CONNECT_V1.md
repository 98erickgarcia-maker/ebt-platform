# Contrato implementado do EBT Connect v1

Candidato local revisado em 08/10/2026, a partir da baseline Connect 0.1.5; sem nova publicação. Fonte: `src/backend/Ebt.Platform.Api`. A especificação em `planejamento/connect_api.openapi.json` permanece como proposta histórica; este documento descreve o runtime. Teste sintético não homologa a Meta.

## Autenticação e contexto

Sessão humana: obter `GET /api/security/csrf`, preservar cookies e enviar o token retornado em `X-CSRF-TOKEN` nas operações POST/PUT/DELETE, inclusive login. `POST /api/auth/login` recebe `{email,password}`. `GET /api/auth/me` retorna usuário, empresa, perfil, carteira e vínculos autorizados. `POST /api/auth/context/{id}` troca empresa e revoga a sessão anterior; `POST /api/auth/logout` também revoga a sessão no servidor. Sessões duram oito horas. Cookie HttpOnly/SameSite Strict; Secure em produção.

Integrações técnicas: chave criada por administrador em `POST /api/admin/api-keys`, exibida uma vez, validade de 30 dias. Enviar `Authorization: Bearer <token>`. Seu uso fica restrito a `/api/connect/v1`, empresa e permissões atuais do titular. Revogação em `DELETE /api/admin/api-keys/{id}`. Chave não concede acesso administrativo. Cookie humano continua exigindo CSRF.

`GET /api/admin/api-keys` exige administrador e retorna somente metadados desta empresa: id, name, userId, ownerName, ownerEmail, expiresAt, active e state (active/expired/revoked). Não retorna token ou hash. Revogar uma chave já revogada retorna 204; ID de outra empresa retorna 404. A interface preserva o ID para revogar depois de recarregar a página.

`POST /api/admin/invitations` prepara convite individual de 48 horas; não envia e-mail. Novo usuário ativa em `/api/auth/activate`. Conta existente entra com a senha original e usa `POST /api/auth/invitations/accept-existing` com `{token}` e CSRF. O e-mail deve corresponder ao da conta autenticada (403 em divergência); expirado/usado retorna 400, vínculo já ativo retorna 409. Tokens distintos do mesmo titular são serializados para impedir vínculos duplicados. O aceite acrescenta a empresa ao seletor, sem trocar silenciosamente a sessão nem redefinir senha.

O cliente não escolhe tenant por corpo/query. `X-Expected-Tenant` pode prevenir uma mutation de formulário antigo: divergência retorna 409. Não é fonte de autoridade. `X-Access-Scope` identifica o contexto aplicado na resposta; a interface limpa dados ao mudar contexto, carteira ou perfil. Leitor consulta, operador altera sua carteira, administrador administra sua empresa, suporte não recebe acesso comercial por padrão.

## Resposta na conversa

Consultar `GET /api/connect/v1/conversations?contactId=<uuid>` e `GET /api/connect/v1/conversations/{id}/messages?limit=50`. A página começa pelas mensagens recentes, apresentadas em ordem cronológica. `nextCursor` busca mensagens anteriores; limite máximo 100. A versão da conversa vem no corpo e no ETag.

A lista de conversas inclui `contactName` autorizado e `recipient` da própria conversa, além dos metadados existentes. Não depende da página/filtro de contatos. Alterar o telefone do cadastro não muda o destino de uma conversa existente. A interface mostra o destino antes da confirmação e bloqueia resposta sem identificação.

```http
POST /api/connect/v1/conversations/<id>/messages
Content-Type: application/json
Idempotency-Key: comando-unico-estavel
If-Match: "3"
Authorization: Bearer <token>

{"content":"Recebemos sua solicitação. Vou conferir os detalhes.","contentType":"text"}
```

Não incluir `tenantId`, `to` ou destinatário: campos extras são rejeitados. O destinatário e o canal vêm da conversa autorizada. Texto até 4.000 caracteres. `replyToMessageId`, opcional, mantém um vínculo interno com uma mensagem da mesma conversa; não representa citação visual homologada no provedor.

Primeira gravação: **202**, somente depois de mensagem e operação de envio serem persistidas atomicamente:

```json
{
  "messageId": "<uuid>",
  "operationId": "<uuid>",
  "status": "queued",
  "statusUrl": "/api/connect/v1/messages/<uuid>",
  "version": "\"4\""
}
```

Repetir o mesmo comando com a mesma chave retorna **200** e os mesmos IDs, com estado atual. Conteúdo diferente com a mesma chave retorna 409. Preservar chave e conteúdo após timeout; antes de tentar novamente consultar o resultado. `If-Match` ausente retorna 428; versão divergente, 409. IDs de outra empresa/carteira retornam 404. Perfil sem escrita recebe 403. Nova resposta por Meta exige canal habilitado e última entrada dentro de 24 horas; a política concreta depende da homologação da conta.

`GET /api/connect/v1/messages/{id}` retorna `messageId`, `conversationId`, `direction`, `content`, `status`, `providerId`, `failureCode`, `createdAt`, `replyToMessageId`, `actorId`, `version`.

| Estado da mensagem | Significado |
|---|---|
| received | Entrada recebida e registrada |
| queued | Resposta persistida, aguardando processamento |
| accepted | Provedor devolveu uma referência de aceite |
| sent / delivered / read | Evento correspondente recebido pelo webhook |
| failed | Bloqueio de política/acesso, rejeição determinística do adapter de QA ou falha informada pelo provedor |
| unknown | Resultado externo não confirmado; não reenviar automaticamente |

Um callback tardio pode reconciliar uma operação unknown. Fatos de status ficam registrados separadamente; leitura/entrega confirmadas não retrocedem por evento fora de ordem. Aceite HTTP não prova entrega ou leitura. O adapter `qa` só funciona em Development e não transmite nada para clientes.

## Webhook Meta

Rota `GET/POST /webhooks/connect/meta/{appKey}`. A verificação GET usa `hub.mode=subscribe`, `hub.verify_token` e devolve `hub.challenge` como texto. Token inválido: 401; aplicativo não configurado: 404.

POST: envelope bruto até 1 MiB, header `X-Hub-Signature-256: sha256=<hex>` calculado por HMAC-SHA256 sobre **os bytes exatos**. Assinatura inválida retorna 401 sem persistir eventos. Após autenticar, o servidor cifra e grava o envelope antes do ACK `200 {"received":true}`. Falha de gravação/quota retorna 503, sem fingir recebimento.

O ACK não espera processamento. O worker percorre todos os entry/changes/messages/statuses, resolve `(appKey, accountId, phoneNumberId)` em cadastro confiável e então aplica a empresa. Nunca confia em tenant enviado no evento. Mensagens são deduplicadas por empresa/canal/ID externo, com IDs externos sensíveis a maiúsculas. Envelope exato é deduplicado por aplicativo/hash; callbacks guardam identidade sem depender da ordem das propriedades JSON.

Metadado desconhecido, tipo incompatível ou conteúdo inválido gera quarentena. Eventos conhecidos do mesmo envelope são processados; diagnóstico não libera conteúdo de outro tenant. Envelopes ficam cifrados com chaves persistentes, vinculados ao aplicativo/hash; os antigos permanecem legíveis pelo formato anterior. Falha de chave coloca o item em quarentena para investigação, preservando seu conteúdo cifrado. Retenção automática do corpo de envelopes processados: sete dias; ledger de hash permanece. Quarentena é limitada pela quota global de 100 MiB e não tem reenvio automático.

Processamento usa sinal após commit e verificação a cada 15 segundos quando ocioso. Lock transacional, índice único, lease e fencing protegem repetição/concorrência. Interrupção depois da tentativa gera unknown ou preserva o callback confirmado. Reiniciar não retransmite operações unknown/terminadas.

## Demais rotas implementadas

Todas as rotas abaixo usam prefixo `/api/connect/v1` e autorização por empresa/carteira.

| Operação | Contrato principal |
|---|---|
| GET /summary | Totais de contatos, tarefas abertas/vencidas e cinco etapas |
| GET /contacts | search, stage, page, limit; items/total; máximo 100 por página |
| POST /contacts | name, email?, phone?, externalKey?, organizationId?, ownerId?, portfolio?, stage?; Idempotency-Key; 201 novo/200 repetição |
| GET/PUT /contacts/{id} | PUT com mesmo DTO, If-Match obrigatório; ID/externalKey preservados |
| GET/POST /organizations | POST name/externalKey/portfolio?; conflito se chave representar conteúdo divergente |
| GET/POST /contacts/{id}/history | POST content/occurredAt? e Idempotency-Key; autoria e instante de registro preservados |
| GET /tasks | contactId, ownerId, state, dueFrom inclusivo, dueTo exclusivo; máximo 100; X-Total-Count |
| POST /contacts/{id}/tasks | title/dueAt/ownerId? e Idempotency-Key |
| POST /tasks/{id}/close | state done ou cancelled, result obrigatório, If-Match e Idempotency-Key |
| POST /imports/preview | rows de 1–100 contatos; sem cadastro definitivo; retorno id/payloadHash/rows |
| POST /imports/{id}/confirm | payloadHash, Idempotency-Key; valida contexto/dados atuais e grava o lote inteiro ou nada |
| GET /imports/{id} | Resultado persistido do lote próprio |
| GET /documents | contactId opcional; metadados autorizados |
| POST /contacts/{contactId}/documents | multipart title/file/taskId?, Idempotency-Key; PDF ou UTF-8, até 2 MiB |
| POST /documents/{id}/versions | multipart file, Idempotency-Key e If-Match; mantém versões anteriores |
| GET /documents/{id}/versions | Metadados, hash, autoria, revisão e motivo por versão |
| POST /documents/{id}/review | Administrador: state approved/rejected, reason obrigatório na rejeição, If-Match |
| GET /documents/{id}/download/{number} | Download privado, hash conferido; leitor baixa somente versão aprovada |

Próxima ação é calculada a partir da primeira tarefa aberta, sem campo duplicado no contato. Importação é delimitada e não importa clientes reais automaticamente. Documentos: quota de 20 MiB por empresa e 100 MiB total no piloto. Produção bloqueia aprovação sem scan clean da versão específica; QA local não prova ClamAV.

`PUT /contacts/{id}` recusa mudança de carteira de contato com conversa vinculada: 409 `contact_channel_transfer_required`, sem alterar cadastro/versão/histórico. Editar na mesma carteira continua permitido. Transferência completa de canal/histórico requer operação futura própria. O worker mantém a negativa de carteira divergente e serializa o primeiro vínculo de canal com a edição do contato.

Erros usam `application/problem+json`: type/title/status/code/traceId. Não incluem SQL, senha, token ou corpo privado de provedor. Informar traceId ao suporte. Respostas são no-store. A chave técnica pode acessar todas as rotas Connect permitidas ao seu titular, inclusive cadastro/documentos; crie um usuário próprio de integração se precisar separar essa permissão.

## Provedor WazVox (0.1.1, QA)

`POST /webhooks/connect/wazvox/{appKey}` usa namespace `wz-`, `X-BSP-Timestamp`, `X-BSP-Event-Id` e `X-BSP-Signature`. HMAC SHA-256 inclui timestamp, ponto e corpo bruto; janela de cinco minutos. Versão `1`, workspace configurado e eventId igual ao header são obrigatórios. ACK `200` somente após envelope cifrado persistido; repetição do mesmo ID/corpo retorna `200`, conteúdo divergente retorna `409`. Sem assinatura válida retorna `401`; workspace/versão/header incompatíveis retornam `400`; limite de 1 MiB retorna `413` e storage indisponível retorna `503`.

`message.received` de texto alimenta o processamento comum. O callback real observado em 07/10/2026 usa `message.status` com `data.id` contendo a referência `wamid.`, `data.status` e `data.recipient_id`. A versão 0.1.5 também aceita o contrato anterior `data.waMessageId/status/to`; um UUID interno em `data.id` não substitui a referência WhatsApp, e duas referências WhatsApp divergentes são rejeitadas. Os estados aceitos são `sent`, `delivered`, `read` e `failed`. Outros eventos ficam em quarentena. Workspace do provedor não é o tenant interno EBT; vínculo depende de app/WABA/número previamente cadastrado por operação administrativa. Respostas humanas mantêm o contrato `202`/`200` da fila Connect. Backend envia REST WazVox com chave privada e idempotência por operationId; erro/timeout ou ausência de referência WhatsApp permanece `unknown`, sem reenvio automático.

[Guia e limites da integração](../../PASSO_A_PASSO_WAZVOX_CONNECT.md). A [prova histórica 0.1.5](../../evidencias/connect_wazvox_real_015.json) registra texto real recebido/respondido e estados de entrega/leitura em 07/10. Esta revisão local não repetiu essa prova e não homologa Meta direto, mídia, templates ou campanhas.

Se o envio WazVox perder a resposta antes da referência WhatsApp, callbacks preservados não identificam automaticamente a operação EBT: o contrato consultado não mostrou eco de operationId. Esse caso exige conciliação operacional sem retry automático. Não confundir com o mecanismo de referência opaca do adapter Meta direto.

## Referências de desenho originais

[Chatwoot: canal de API](https://www.chatwoot.com/hc/user-guide/articles/1677839703-how-to-create-an-api-channel-inbox), [Stripe: webhooks](https://docs.stripe.com/webhooks), [Microsoft: outbox transacional](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos), [Meta: referência oficial da Cloud API](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api) e [RFC 9457](https://www.rfc-editor.org/info/rfc9457/) orientaram os padrões. Não foram copiados serviços, contas ou código dessas plataformas. Versão Meta/conta/status reais continuam dependências externas.
