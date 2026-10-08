"""Contrato e backlog candidatos de comunicação; não são servidor ou conector."""
import json

PHASE = dict(id='P11', nome='Comunicação Connect por API e webhook', horas=36,
             resultado='Receber, responder e acompanhar status de texto no canal homologado',
             dependencias=['P04', 'P05', 'P07'],
             origem='Desenho EBT; referências oficiais Chatwoot, Meta, Stripe e Microsoft',
             gate='G-MSG')
CONTEXT = dict(inputs='G-SEG/G-CRM/G-TASK, canal de QA próprio e contratos versionados.',
               output='Jornada de mensagem recebida, resposta por API e status por webhook.',
               refs=['F26'], product='comunicacao',
               risk='Resposta duplicada, evento perdido, tenant cruzado ou entrega inferida.',
               exclude='Somente texto e resposta do atendente; sem campanha, chatbot, omnichannel ou fila coletiva avançada.')
ROWS = [
('Fixar canal, conta de QA e versão do provedor', 'Conta/conexão pertence ao tenant; versão, escopos, janela/template, direitos e custos estão registrados; sem contratação ou conta real por inferência.'),
('Definir mensagens, conversas e contrato de resposta', 'Uma conversa referencia contato/empresa/canal; API tem idempotência, concorrência, paginação e erro seguro; nota interna não gera envio.'),
('Validar assinatura e handshake do webhook', 'Assinatura é conferida nos bytes originais antes de efeitos; desafio GET é separado do POST; conexão/tenant vêm do mapeamento confiável do canal.'),
('Persistir entrada e deduplicar eventos', 'ACK somente após recebimento durável; repetição e lote não duplicam mensagens; falha antes do commit permite retry; tipos novos não desaparecem silenciosamente.'),
('Processar evento e vincular contato e conversa', 'Worker idempotente normaliza mensagem; IDs externos são escopados por conexão/tenant; remetente não une pessoas de empresas diferentes.'),
('Registrar resposta e outbox na mesma transação', 'Resposta autorizada e intenção de envio persistem juntas; 202 informa fila, mesma chave/payload retorna a mesma operação e payload diferente conflita.'),
('Enviar texto pelo adapter oficial delimitado', 'Worker valida conexão, autorização/política vigente e destinatário da conversa; conserva ID externo; aceite do provedor não significa entrega.'),
('Conciliar callbacks e eventos fora de ordem', 'Sent/delivered/read/failed são eventos distintos; duplicata não duplica histórico; callback anterior à resposta da API fica pendente e depois é conciliado.'),
('Tratar timeout, retry e envio desconhecido', 'Timeout após POST não reenvia automaticamente sem prova de idempotência do provedor; estado desconhecido e diagnóstico seguro permitem reconciliação auditada.'),
('Mostrar conversa e resposta na interface Connect', 'Histórico tem direção/autor/instante e estados reais; rascunho sobrevive à falha; conflito e consulta negada são visíveis; notas permanecem internas.'),
('Validar jornada e negativas do canal', 'Receber/responder/status passa em QA A/B, assinatura inválida, ID direto, repetição, queda de worker e restore; mock não homologa Meta.'),
('Demonstrar G-MSG e manual de operação', 'Versão final reúne G-SEG/G-CRM/G-TASK/G-MSG, prova do canal, pendências e runbook; sem acesso externo, gate fica pendente e entrega local é identificada como tal.'),
]
DETAILS = '''
P11-01|Ficha de conexão e dependências externas|Identificar canal/versão/conta de QA; mapear conexão/tenant; registrar políticas e aprovação pendente|Massa/conta próprias; conexão de B negada; ausência de credencial mantém homologação pendente|Provedor escolhido por inferência vira conta contratada
P11-02|Contrato neutro de conversa e mensagem|Fixar IDs e vínculos; revisar API e estados; validar schemas de request/response|IDs internos estáveis; nota sem envio; contrato desconhecido recusado|Telefone vira identidade global da conversa
P11-03|Webhook autenticado|Separar handshake; conferir assinatura nos bytes originais; resolver conexões confiáveis|Assinatura ausente/inválida recusada; corpo alterado recusado; conexão desconhecida não cria tenant|Re-serializar JSON antes de validar assinatura
P11-04|Ledger durável de recebimento|Persistir envelope e eventos; definir chaves únicas; responder ACK depois do commit|Duplicata/lote sem perda; falha SQL não retorna ACK de sucesso; evento novo guardado sem envio|HTTP 200 confirma evento ainda em memória
P11-05|Normalização e conversa persistidas|Executar worker idempotente; resolver contato e canal; persistir mensagem e histórico|Dois workers não duplicam; restart recupera entrada; mesmo remetente A/B fica isolado|Webhook cria cadastro diferente a cada recebimento
P11-06|Resposta enfileirada com outbox|Autorizar recurso; conferir versão/idempotência; salvar mensagem e intenção na mesma transação|Mesmo payload/chave recupera operação; chave com payload diferente conflita; rollback não deixa intenção órfã|API responde enviado antes do commit
P11-07|Adapter de texto e resultado externo|Conferir política/conta vigente; transmitir por API oficial; guardar vínculo da operação com ID externo|Canal indisponível não envia; aceite não marca entregue; destinatário de B negado|Client escolhe arbitrariamente destinatário fora da conversa
P11-08|Ledger de status conciliado|Persistir callback; ligar ID externo à mensagem; reduzir estado sem regressão indevida|Read antes de sent preserva read observado; callback antes do retorno é conciliado; status de B não altera A|Último callback recebido rebaixa status
P11-09|Falhas e reconciliação auditadas|Classificar erro seguro/incerto; aplicar retry limitado somente seguro; resolver envio desconhecido com prova|Timeout depois de aceite não dispara segunda mensagem; restart retoma lease; falha terminal tem diagnóstico|Retry local promete envio externo exatamente uma vez
P11-10|Tela de conversa e resposta|Manter lista/detalhe no mesmo contato; mostrar fila e estados observados; preservar rascunho e negar ação indevida|Reload mantém conversa; consulta não responde; nota privada não aparece em mensagem externa|Toast de sucesso simula entrega
P11-11|Jornada do canal em QA|Validar cenário ponta a ponta; disputar workers/chaves; conferir A/B e recuperação|Recebida/resposta/status ligados; banco/worker falhos recuperam; ID direto e assinatura inválida negados|Adapter mock tratado como WhatsApp homologado
P11-12|Ficha G-MSG e runbook|Reconciliar casos e versão; registrar canal e prova externa; documentar reprocessamento/limites|Gate não passa sem evidência externa exigida; nenhum caso pendente escondido; manual distingue fila e entrega|Fim do timebox vira aceite fictício
'''


def new_tasks():
    result = []
    for n, (title, acceptance) in enumerate(ROWS, 1):
        ident = f'P11-{n:02}'
        result.append(dict(id=ident, fase='P11', titulo=title, horas=3,
            implementacao_h=1.75, verificacao_h=1, registro_h=0.25, reserva_h=0,
            trilha='N', origem=PHASE['origem'],
            dependencias=[f'P11-{n-1:02}'] if n > 1 else ['P04-GATE', 'P05-GATE', 'P07-GATE'],
            criterio_aceite=acceptance,
            evidencia_esperada=f'Registro {ident}: versão/hash, ambiente, cenário e resultado conforme trilha N',
            status='planejado', horas_reais=0, responsavel_proposto='desenvolvimento EBT', gate='G-MSG'))
    return result


def openapi():
    ref = lambda name: {'$ref': f'#/components/schemas/{name}'}
    response = lambda name, description: {'description': description,
        'content': {'application/json': {'schema': ref(name)}}}
    problem = {'description': 'Erro seguro, código e traceId; sem segredos/conteúdo privado',
               'content': {'application/problem+json': {'schema': ref('Problem')}}}
    common = {'400': problem, '401': problem, '403': problem, '404': problem,
              '409': problem, '422': problem, '429': problem, '503': problem}
    identifier = {'type': 'string', 'minLength': 1}
    path_id = lambda name: {'name': name, 'in': 'path', 'required': True, 'schema': identifier}
    return {
        'openapi': '3.1.0',
        'info': {'title': 'EBT Connect - contrato candidato', 'version': '0.1.0-planejado',
                 'description': 'Especificação futura. Nenhum endpoint foi implementado. DTO/policy da fonte precisam ser confrontados em P01/P11.'},
        'x-estado': 'planejado',
        'paths': {
            '/api/connect/v1/conversations/{conversationId}/messages': {
                'parameters': [path_id('conversationId')],
                'get': {'operationId': 'listConversationMessages', 'security': [{'bearerAuth': []}],
                    'parameters': [{'name': 'cursor', 'in': 'query', 'schema': {'type': 'string'}},
                                   {'name': 'limit', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1}}],
                    'responses': {'200': response('MessagePage', 'Página autorizada, cursor estável'), **common}},
                'post': {'operationId': 'queueConversationReply', 'security': [{'bearerAuth': []}],
                    'parameters': [{'name': 'Idempotency-Key', 'in': 'header', 'required': True, 'schema': identifier},
                                   {'name': 'If-Match', 'in': 'header', 'required': True, 'schema': identifier}],
                    'requestBody': {'required': True, 'content': {'application/json': {'schema': ref('ReplyRequest')}}},
                    'responses': {'202': response('QueuedReply', 'Persistida/enfileirada; não significa envio/entrega'),
                                  '200': response('QueuedReply', 'Repetição da mesma operação já existente'),
                                  '428': problem, **common}},
            },
            '/api/connect/v1/messages/{messageId}': {
                'get': {'operationId': 'getMessageState', 'security': [{'bearerAuth': []}],
                        'parameters': [path_id('messageId')],
                        'responses': {'200': response('Message', 'Estado observado e evidência disponível'), **common}},
            },
            '/webhooks/connect/meta/{appConnectionKey}': {
                'parameters': [path_id('appConnectionKey')],
                'get': {'operationId': 'verifyMetaWebhook', 'security': [],
                        'parameters': [{'name': n, 'in': 'query', 'required': True, 'schema': identifier}
                                       for n in ['hub.mode', 'hub.verify_token', 'hub.challenge']],
                        'responses': {'200': {'description': 'Somente desafio validado; sem efeitos de mensagem',
                            'content': {'text/plain': {'schema': {'type': 'string'}}}}, '403': problem}},
                'post': {'operationId': 'receiveMetaWebhook', 'security': [{'metaSignature': []}],
                         'description': 'Validar assinatura nos bytes originais, mapear conta/conexão e persistir duravelmente antes de ACK. JSON do provedor permanece externo ao domínio.',
                         'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object', 'additionalProperties': True}}}},
                         'responses': {'200': {'description': 'Envelope recebido duravelmente ou duplicata já durável; não é resposta ao cliente'},
                                       '400': problem, '403': problem, '413': problem, '503': problem}},
            },
        },
        'components': {
            'securitySchemes': {
                'bearerAuth': {'type': 'http', 'scheme': 'bearer',
                    'description': 'Credencial candidata da API; estratégia de sessão/provedor deve ser fechada em P04. Não embutir token.'},
                'metaSignature': {'type': 'apiKey', 'in': 'header', 'name': 'X-Hub-Signature-256',
                    'description': 'Representação documental de assinatura HMAC; não é uma API key. Validar bytes originais e segredo de app conforme contrato vigente do provedor.'},
            },
            'schemas': {
                'ReplyRequest': {'type': 'object', 'additionalProperties': False,
                    'required': ['content', 'contentType'],
                    'properties': {'content': {'type': 'string', 'minLength': 1},
                        'contentType': {'type': 'string', 'const': 'text'},
                        'replyToMessageId': identifier}},
                'QueuedReply': {'type': 'object', 'required': ['messageId', 'operationId', 'status', 'statusUrl'],
                    'properties': {'messageId': identifier, 'operationId': identifier,
                        'status': {'type': 'string', 'enum': ['queued', 'accepted', 'sent', 'delivered', 'read', 'failed', 'unknown']},
                        'statusUrl': {'type': 'string'}, 'version': identifier}},
                'Message': {'type': 'object', 'required': ['id', 'conversationId', 'direction', 'status'],
                    'properties': {'id': identifier, 'conversationId': identifier,
                        'direction': {'type': 'string', 'enum': ['incoming', 'outgoing', 'internal']},
                        'content': {'type': 'string'}, 'status': {'type': 'string',
                            'enum': ['received', 'queued', 'accepted', 'sent', 'delivered', 'read', 'failed', 'unknown']},
                        'providerMessageId': {'type': ['string', 'null']},
                        'occurredAt': {'type': 'string', 'format': 'date-time'},
                        'receivedAt': {'type': 'string', 'format': 'date-time'}}},
                'MessagePage': {'type': 'object', 'required': ['items', 'nextCursor'],
                    'properties': {'items': {'type': 'array', 'items': ref('Message')},
                        'nextCursor': {'type': ['string', 'null']}}},
                'Problem': {'type': 'object', 'required': ['type', 'title', 'status', 'code', 'traceId'],
                    'properties': {'type': {'type': 'string', 'format': 'uri'}, 'title': {'type': 'string'},
                        'status': {'type': 'integer'}, 'code': identifier, 'traceId': identifier,
                        'detail': {'type': 'string'}}},
            },
        },
    }


def emit_communication(emit):
    emit('planejamento/connect_api.openapi.json', json.dumps(openapi(), ensure_ascii=False, indent=2))
    emit('docs/arquitetura/CONNECT_API_E_WEBHOOK.md', DOCUMENT)


DOCUMENT = '''# EBT Connect: respostas por API e webhook

Revisão em 07/10/2026. Este é um desenho e contrato candidato, com backlog P11 de 36h, não um serviço implementado. O usuário pediu que o fluxo de resposta fosse planejado com mais cuidado e autorizou pesquisar referências. WhatsApp oficial é o primeiro canal candidato escolhido nesta revisão técnica; a conta/provedor final e sua homologação ficam pendentes em P11-01.

## Como funciona para o atendente

O cliente manda uma mensagem. O Connect recebe o aviso pelo webhook e vincula a mensagem ao contato/conversa corretos. O atendente abre essa conversa, digita e confirma a resposta. A API registra a intenção; um worker transmite ao canal. Os callbacks atualizam os estados observados. A tela mostra conversa, responsável, rascunho, mensagem e motivo de falha sem obrigar o operador a entender detalhes técnicos.

Nota interna fica no histórico interno. Resposta externa tem ação própria. A primeira versão tem atendimento por responsável designado; distribuição inteligente, inbox coletivo avançado, campanhas, chatbot e outros canais ficam depois deste ciclo.

## Referências e decisão de arquitetura

Chatwoot documenta canal API com contato/conversa/mensagem, distinção incoming/outgoing e callbacks. Sua API cria mensagens dentro da conversa. É a referência de organização escolhida, sem copiar o produto inteiro, sua stack ou concluir que o nosso canal está homologado. [Canal API](https://www.chatwoot.com/hc/user-guide/articles/1677839703-how-to-create-an-api-channel-inbox), [criar mensagem](https://developers.chatwoot.com/api-reference/messages/create-new-message).

Stripe documenta duplicatas, ausência de ordem garantida e ACK rápido para seus webhooks. A recomendação EBT é receber com persistência durável e processar depois; as políticas de retry e resposta HTTP do provedor escolhido continuam específicas. [Webhooks Stripe](https://docs.stripe.com/webhooks).

Microsoft explica gravar objeto de negócio e outbox na mesma transação, inclusive em persistência relacional. Aplicaremos o padrão ao SQL do recorte; o exemplo consultado usa Cosmos DB e não obriga troca de banco. [Transactional Outbox](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos).

Meta publica seus contratos de mensagens e status na coleção oficial. O SDK histórico da Meta documenta validação X-Hub-Signature-256; a configuração exata, versão e payload vigente serão confirmados em P11-01/P11-03. As páginas novas de developers.facebook.com tentadas nesta consulta retornaram erro de acesso; não foram tratadas como documentação lida. [Coleção Meta](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api), [payload de webhook](https://www.postman.com/meta/whatsapp-business-platform/folder/tduohwq/webhook-payload-reference), [assinatura no SDK histórico](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/types/webhookCallbackFunction/).

O desenho EBT usa .NET/React/SQL e um worker inicialmente no mesmo serviço, com inbox/outbox duráveis no SQL. Não exige Redis, broker separado ou microserviços neste recorte. CASST é fonte seletiva: cada contrato/componente precisa passar pela baseline. A insatisfação relatada pelo usuário não foi convertida em alegação de defeito técnico sem inspeção.

## Três respostas diferentes

| Resposta | Quem recebe | Significado |
|---|---|---|
| ACK HTTP do webhook | Provedor | Envelope autenticado foi armazenado; não é mensagem ao cliente |
| 202 da API do Connect | Interface/consumidor autorizado | Intenção de resposta persistida e enfileirada; ainda não entregue |
| Mensagem enviada pela API do canal | Cliente, se o canal a entregar | Texto externo; callbacks fornecem provas de status disponíveis |

```mermaid
sequenceDiagram
  participant C as Cliente
  participant P as Canal oficial
  participant W as Webhook EBT
  participant S as SQL inbox/outbox
  participant J as Worker
  participant A as Atendente
  participant API as API Connect
  C->>P: Mensagem
  P->>W: Evento assinado
  W->>S: Recebimento durável e deduplicação
  W-->>P: ACK após commit
  J->>S: Normalizar contato/conversa/mensagem
  A->>API: Confirmar resposta autorizada
  API->>S: Mensagem + intenção na mesma transação
  API-->>A: 202 e ID da operação
  J->>P: Transmitir pela API do canal
  P-->>J: ID externo ou falha/incerteza
  P->>W: Callback de status
  W->>S: Ledger e conciliação
  A->>API: Consultar status persistido
```

## Modelo e fronteiras

ChannelConnection: tenant, provedor, conta/número/canal, versão, estado, referência segura de credencial. ContactChannelIdentity: contato interno e identificador opaco do remetente no escopo dessa conexão. Conversation: ID interno, contato, conexão, responsável, estado e versão. Message: conversa, direção, conteúdo autorizado, autor/origem, instante do evento e recebimento, ID externo e estado observado. WebhookReceipt/InboxEvent: hash/identidade do evento, versão, estado de processamento, tentativas e erro sanitizado. OutboxOperation: mensagem, chave/hash do comando, payload autorizado, lease, tentativa e resultado. DeliveryEvent: fato externo de status, referência externa e timestamps.

ID externo, telefone, ID interno do contato e ID da conversa são diferentes. Não unir cadastros de tenants distintos pelo telefone. O webhook resolve contexto por app/conexão e conta/número registrados, depois de autenticar o evento; TenantId do corpo não dá autoridade. A API exige permissão no contato/conversa e no canal. Admin técnico não recebe automaticamente conteúdo.

A assinatura é validada em tempo constante nos bytes originais, antes da desserialização com efeitos; segredo não aparece em logs. Handshake GET não autentica mensagens POST. Não exigir um header de timestamp que o provedor não emite; repetição legítima é tratada pelo ledger/dedupe. Limites de corpo, retenção, tamanho de texto, rate limit e prazos são parâmetros fechados em P11-01/P11-03, conforme contrato vigente.

## Contrato da resposta

Paths novos são propostas: POST /api/connect/v1/conversations/{conversationId}/messages, GET dessa coleção e GET /api/connect/v1/messages/{messageId}. O JSON da resposta recebe content, contentType=text e replyToMessageId opcional; não recebe tenant ou destinatário arbitrário. O servidor resolve canal/destinatário pelo recurso autorizado e confirma que replyTo pertence à mesma conversa.

Idempotency-Key e If-Match são obrigatórios para confirmar envio. Unicidade: tenant + conversa + ação + chave. Guardar hash canônico do comando e resultado. Mesma chave/payload recupera a operação; mesma chave com outro texto retorna 409; versão obsoleta retorna conflito; precondição ausente retorna 428. Destino sem sessão/permissão recebe erro seguro conforme a policy, sem enumerar IDs alheios. Paginação usa cursor estável e limite configurado no servidor.

Exemplo sintético de retorno inicial:

```json
{"messageId":"msg-qa-001","operationId":"op-qa-001","status":"queued","statusUrl":"/api/connect/v1/messages/msg-qa-001","version":"qa-v2"}
```

Erros próprios usam application/problem+json, code e traceId, sem texto sensível do provedor; seguir [RFC 9457](https://www.rfc-editor.org/info/rfc9457/). Códigos internos distinguem forbidden, stale_version, idempotency_mismatch, channel_unavailable, reply_policy_blocked e provider_result_unknown. Estratégia de sessão humana/credencial técnica deve ser fechada em P04; OpenAPI não implanta um mecanismo de autenticação.

## Recebimento e confirmação do webhook

Validar assinatura e envelope; armazenar recebimento e trabalho pendente; ACK somente após commit. Falha de persistência retorna erro transitório adequado ao provedor. Envelope pode conter várias entradas, changes, messages e statuses: percorrer todos os itens. Duplicata já durável recebe ACK sem nova mensagem. Mensagem usa chave tenant/conexão/provedor/ID externo; status usa identidade própria com referência, status e dados do evento, sem colapsar todos os callbacks da mensagem em uma única chave.

Evento autenticado de conexão desconhecida ou tipo não suportado fica em quarentena durável e gera diagnóstico; não inventa tenant, não envia resposta e não se perde em silêncio. Um envelope misto preserva os itens conhecidos e a quarentena de forma durável antes do ACK. Retenção do corpo bruto é minimizada e protegida, com política e acesso administrativo; não usar o corpo como log público.

Worker retoma eventos após restart. Alteração de conversa/mensagem e checkpoint de processamento têm limite transacional definido. Concorrência usa índice único e lease com fencing/versionamento; dois workers não geram duas mensagens ou duas operações por uma chave. Reprocessamento do ledger é auditado e não remove os registros que sustentam dedupe.

## Envio, callbacks e incerteza

Salvar mensagem e outbox no mesmo commit. Worker revalida conexão, permissão vigente e política de resposta antes de transmitir. Janela de atendimento, templates e identificadores permitidos são conferidos na documentação/conta do canal na homologação; custo, aprovação de template e infraestrutura não estão contratados por este plano. Texto livre bloqueado pela política permanece como rascunho/erro de ação e não é enviado fora das condições permitidas.

Estado interno queued indica fila. accepted significa aceite comprovado do provedor com referência externa. sent, delivered e read dependem dos callbacks específicos; ausência de read não prova falta de leitura. failed preserva erro sanitizado. unknown representa POST com resultado ambíguo. Guardar fatos/instantes recebidos; uma redução determinística preserva read/delivered já observados quando chega sent atrasado, e conflito de fatos fica registrado, sem simplesmente ordenar estados como números.

Callback pode chegar antes da resposta da API: guardar evento não conciliado por conexão/ID externo e conciliar quando o vínculo estiver disponível. IDs/status de outra conexão ou tenant não alteram mensagem. Retenção e alertas de eventos órfãos precisam ser definidos; não descartar porque ainda não existe a mensagem correspondente.

Idempotência da API EBT não garante idempotência da chamada externa. Se o canal não aceitar chave idempotente ou permitir consultar a operação incerta, timeout após POST exige unknown e reconciliação, sem resend automático. Mesmo erro 5xx pode ser ambíguo; adapter precisa distinguir rejeição comprovada de resultado desconhecido. Retry com backoff/jitter tem limite e só acontece quando é seguro pela semântica do provedor. Falha de processamento local é repetível com dedupe; ela é diferente de repetir um envio externo.

Replay/retry administrativo exige ação específica, contexto e trilha. Resolver mensagem desconhecida não cria chave nova silenciosamente; eventual reenvio é decisão explícita com risco de duplicata registrado. Reiniciar worker, restaurar banco ou clicar duas vezes não deve disparar nova mensagem por conta própria.

## Limites da primeira versão e testes obrigatórios

Somente texto, conversa ligada ao contato, um adapter e resposta confirmada pelo atendente. Projeto deixa contratos prontos para integrações autenticadas e para eventos próprios futuros. Webhook genérico de saída para destinos arbitrários, robôs, chatbot/IA, broadcast e integração de e-mail ficam fora desta implementação inicial.

P11-11/P11-12 devem provar entrada assinada, duplicata/lote, ordem invertida, callback antes do retorno, confirmação simultânea, perda de resposta, tenant A/B/carteira/ID direto, sessão revogada, política de canal, falha SQL, restart do worker, replay autorizado, restore com ledger/outbox e UI que conserva rascunho. Callback de status não gera nova resposta, evitando loop. Fixtures locais são próprias; homologação do canal exige prova no destino real de QA permitido. Sem acesso ao provedor, registrar capacidade local e manter G-MSG pendente.

## Encaixe nas 200h

CRM/tarefas: 104h acumuladas. Comunicação P11: 36h, fechando em 140h se todos os gates passarem. GED: 24h, até 164h. Candidato integrado: 16h, até 180h. Reserva: 20h. Site (12h) e Flow (24h) foram adiados para liberar as mesmas 36h; não foram declarados entregues nem apagados do backlog posterior.

36h é um timebox técnico de recorte, sem promessa de homologação externa ou prazo. Se acesso/canal ou generalização exigir mais, registrar estimativa real e priorizar a comunicação essencial; o GED pode ser recortado/adiado mediante replanejamento explícito. Não consumir a reserva em ampliação de canal. O marco de 140h é QA; liberação real requer G-RC e aceite próprios.

[OpenAPI candidato](../../planejamento/connect_api.openapi.json) | [Entrega Connect](../produtos/ENTREGA_EBT_CONNECT.md) | [P11](../execucao/fases/P11.md) | [Gates](../VALIDACAO_E_GATES.md)
'''
