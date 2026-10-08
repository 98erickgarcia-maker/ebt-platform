# Validação proporcional, gates e execução

## Trilhas

| Trilha | Quando usar | Verificação incluída |
|---|---|---|
| R1, reuso comprovado sem mudança funcional | Mesmo comportamento/contrato e evidência da versão, ou apresentação de baixo impacto | Conferir origem/hash/diff; smoke do caminho; build/lint pertinente; inspeção focal de páginas alteradas. Não repetir uma suíte inteira já válida por hábito. |
| R2, reuso com adaptação | Marca configurável, extração, outro consumidor, vínculo, filtro ou composição diferente | Regressão dos produtores/consumidores afetados, salvar/reload, negativa de perfil/tenant quando aplicável, cache, erro e contrato. |
| N, capacidade ou fronteira nova | Tenancy generalizada, índice, protocolo, workflow, novo storage ou segurança | Regra e happy path, entradas inválidas, acesso por ID, tenant A/B, repetição, concorrência, persistência, integração SQL real e recuperação conforme o risco. |
| RES, capacidade contingente | Defeito ou impedimento comprovado | Usar apenas mediante necessidade; registrar consumo e redução de escopo. Não contabilizar como funcionalidade entregue. |

Os rótulos do backlog são escolhas iniciais de validação, não certificados de código existente. Promoção de R1 para R2/N é obrigatória quando muda contrato, política, schema, dependência ou ambiente relevante. Uma falha bloqueia apenas o recorte dependente; site independente pode prosseguir. Falha de segurança compartilhada bloqueia todos os consumidores afetados.

## Gates por marco

| Gate | O que deve existir | Evidência mínima |
|---|---|---|
| G0 | Fonte e recorte congelados, direitos de uso conferidos | Hashes/árvore local, mapa de contratos e registro do cenário aprovado/pendente. |
| G1 | Ambiente isolado e build reproduzível | CI pertinente, health, massa própria e persistência de QA. |
| G-SITE | Pacote de site essencial | Páginas/links, celular/computador, canal ou formulário confirmado em QA, manual e retorno. |
| G-SEG | Isolamento, sessão e autorização | SQL real com tenants A/B, ID direto, negativa de ação, troca de perfil/cache e onboarding E2E. |
| G-CRM | Cadastro/histórico/próxima ação | Jornada com ID único e segundo consumidor, conflito/repetição e resultado persistido. |
| G-MSG | Recebimento, resposta por API e callback | Assinatura/ACK durável, conversa e outbox, A/B/ID direto, duplicata/ordem/concorrência, status reais, envio incerto e prova do canal de QA. |
| G-GED | Documento privado do recorte | Upload/revisão/versão/download autorizado, negativa de B e restore com hashes. |
| G-TASK | Tarefa ligada ao registro | Prazo/resultado, alteração permitida/proibida e contador reconciliado. |
| G-FLOW | Protocolo e fluxo fixo | Sequência SQL concorrente/idempotente, transição válida/negada, histórico e recuperação. |
| G-RC | Candidato do recorte para piloto | Jornadas integradas, migration/restore ensaiados, manifesto e lista de limites. Não equivale a produção. |

Gates R1 normalmente consomem 15-30 minutos por ticket. R2/N reservam de 30 a 60 minutos ou mais conforme critério. Esses tempos já integram as horas da tarefa; não devem ser somados novamente. O fechamento de marco faz a regressão integrada uma vez, e repete apenas quando houver nova mudança/falha.

## Estados e prova

Backlog -> em execução -> em verificação -> demonstrado em QA -> homologado pelo usuário -> liberado. Bloqueado é usado quando falta uma dependência real. Status “planejado” de todos os tickets indica trabalho futuro, inclusive quando a origem é aprovada. Neste pedido foi entregue o planejamento, não os módulos planejados. G-CRM em 92h, CRM/tarefas em 104h e G-MSG em 140h são marcos de QA; G-RC permanece em 180h. Gates devem identificar a versão final e repetir negativas afetadas por operações novas.

Para cada entrega registrar ID, commit/hash, implementação, critérios, comandos e resultado, evidência sanitizada, ambiente, limitações e próximo passo. Build local, CI, teste autenticado, aceite do piloto e publicação são estados diferentes.

## Regra de orçamento e corte

São 200 horas-pessoa, sem converter em prazo de calendário. Com uma pessoa a 40h/semana, representam cinco semanas de capacidade, não cinco semanas garantidas de entrega. Espera por credencial/aceite não consome hora técnica enquanto ninguém trabalha; reuniões, diagnóstico, teste e retrabalho consomem.

180h estão alocadas a entregas e 20h à reserva. A janela cronológica 180-200h indica capacidade não comprometida; a reserva pode ser utilizada antes de 180h. Não esperar o final do ciclo para corrigir segurança.

Revisão de 07/10/2026: priorizar segurança/CRM/tarefas -> comunicação -> documentos -> candidato. Site e Flow estão adiados fora do ciclo, com IDs/estimativas anteriores preservados. Se extração ou comunicação exigirem mais capacidade, recortar/adiar GED e atualizar candidato/dependências explicitamente. Isolamento, recuperação e comunicação essencial não são dispensados. Não declarar G-MSG/G-GED aprovados sem prova, nem usar reserva para aumentar canais.

Cada item de 1-4h é um timebox para um recorte. Se não fechar, dividir em subtarefas, registrar horas reais e ajustar as próximas. As horas são estimativas internas, sem promessa comercial de preço ou prazo. Não contratar serviço ou publicar em produção por inferência.

## Limites comerciais dos primeiros pacotes

Connect inicial: contatos/organizações, histórico, até cinco etapas, responsável, próxima ação e tarefas; importação sintética delimitada; comunicação de texto por API/webhook e resposta confirmada pelo atendente em um canal homologado. Não inclui financeiro, OS, inbox coletivo avançado, chatbot, campanhas ou omnichannel. GED continua delimitado. Site/Flow foram adiados; suas especificações anteriores permanecem no backlog posterior.

Implantação para cliente real depende de conteúdo e direitos, ambiente, contas, importação autorizada, responsável e aceite específicos. As horas deste ciclo cobrem pacote e QA definidos, não implantação de vários clientes nem operação 24/7. Produto “vendável” significa escopo demonstrável e contratável após seu gate, não conformidade universal.

## Depois das 200h

Primeiro: resolver pendências de aceite/piloto e medir implantação de um cliente. Depois: estabilizar segundo consumidor e extrair capacidades realmente duplicadas. Em seguida: notificações internas/e-mail com adapter, consolidação RH V19 se aceita no Vikings, W3/W4 e Portal/CMS conforme demanda. Só então planejar contratos, integrações oficiais, builders, Legislativo e verticais amplas. Cada integração externa tem sandbox/homologação próprios.

Não incluir revisão completa Vikings V26 antes do gatilho V25 definido no projeto. Ajustes mínimos para o piloto pertencem ao fluxo contratado; este plano não substitui o backlog Vikings.

## Execução autorizada posterior ao plano

Em 07/10/2026, o usuário autorizou programação. O estado de implementação e as provas atuais estão em [STATUS_IMPLEMENTACAO_CONNECT.md](qualidade/STATUS_IMPLEMENTACAO_CONNECT.md). Os critérios acima permanecem; planejamento, QA sintético, CI, canal real, aceite e publicação continuam separados. Não converter os 238 cenários documentais em testes aprovados por inferência.
