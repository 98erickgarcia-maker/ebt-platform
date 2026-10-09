# Estado de implementaÃ§Ã£o do Connect

**Publicacao vigente de 09/10/2026:** EBT Platform 0.2.0 publicada no host existente, com Connect dentro do catalogo e schema `ebt_platform` no mesmo banco compartilhado. Fonte `18a454c`, CI aprovado, sessao preservada, 26 checks HTTP online e navegador desktop/mobile. [Acesso e provas](../../PASSO_A_PASSO_EBT_PLATFORM.md). As referencias abaixo a ausencia de deploy das correcoes e a publicacao 0.1.5 sao historicas. Demais aplicativos planejados; scanner real, restore isolado e aceite continuam pendentes.

**RevisÃ£o incremental de 08/10/2026:** quatro partes verificadas no candidato GitHub `b471eaf8`, com build/continuidade aprovados. R01â€“R05 receberam correÃ§Ãµes e provas nos cenÃ¡rios descritos; cliente protege sessÃµes/downloads tardios e scanner exige resposta completa. [RelatÃ³rio da revisÃ£o](REVISAO_GITHUB_INCREMENTAL_20261008.md). Scanner real, restore Azure e aceite permanecem pendentes; a publicaÃ§Ã£o 0.1.5 abaixo Ã© histÃ³rica e nÃ£o recebeu deploy desta revisÃ£o.

**Estado vigente de 07/10/2026:** primeira entrega publicada e 26 verificaÃ§Ãµes ao vivo aprovadas. [Acesso e provas](../../PASSO_A_PASSO_PUBLICACAO_CONNECT.md). Banco pago compartilhado preservado; valor variÃ¡vel autorizado posteriormente. ReferÃªncias abaixo a host inexistente/F1/R$30 fixos descrevem o cenÃ¡rio anterior e foram superadas por esta publicaÃ§Ã£o. Fluxo real de texto WazVox demonstrado na 0.1.5; scanner, restore Azure e aceite continuam pendentes. CI hospedada de build/protocolo/proxy/documentos aprovada para o checkpoint `92e4006`, conforme prova ao final.


07/10/2026. O pedido de programaÃ§Ã£o substituiu a restriÃ§Ã£o anterior de planejamento. CÃ³digo novo em `src/backend` e `src/frontend`, com fontes existentes preservadas. Estimativa mantida em 180h + 20h; nÃ£o foi preenchido consumo fictÃ­cio de horas.

O backlog e as 238 linhas da matriz documental sÃ£o o plano-base, nÃ£o o registro desta execuÃ§Ã£o. NÃ£o foram promovidos em lote nem tratados como 238 testes aprovados. EvidÃªncia atual em [execucao_connect.json](../../evidencias/execucao_connect.json) e [manifesto do candidato](../../evidencias/manifesto_connect_local.json), com hashes, limites e referÃªncia aos testes.

## Capacidades locais implementadas

- Cadastro Ãºnico de contato/organizaÃ§Ã£o, cinco etapas, responsÃ¡vel/carteira, nota com autoria e datas, pesquisa e paginaÃ§Ã£o.
- Tarefa com responsÃ¡vel/prazo/resultado; prÃ³xima aÃ§Ã£o derivada das tarefas abertas; filtros de situaÃ§Ã£o, responsÃ¡vel e prazo.
- CSV UTF-8 com preview/confirm delimitado; confirmaÃ§Ã£o atÃ´mica e idempotente, sem importar dados dos projetos-fonte.
- Login, ativaÃ§Ã£o por convite, cookie/CSRF, sessÃ£o revogÃ¡vel, perfis, troca de empresa, chaves de API e auditoria.
- Conversa, mensagem, fila durÃ¡vel de resposta, HMAC sobre envelope bruto, processamento de lote A/B, deduplicaÃ§Ã£o, status fora de ordem e reconciliaÃ§Ã£o de envio incerto.
- Documento privado com upload, versÃ£o, hash, aprovaÃ§Ã£o/rejeiÃ§Ã£o por versÃ£o, motivo e download autorizado; quotas do piloto.
- Schema SQL prÃ³prio, FKs de tenant, versÃ£o otimista, locks e barreira RLS; migration repetÃ­vel, permissÃµes separadas e comandos administrativos de bootstrap/canal.
- Interface React responsiva e testes HTTP, SQL direto, navegador, migration e restauraÃ§Ã£o com massa sintÃ©tica.

## Gates e limites

| Gate | Prova disponÃ­vel | Estado honesto |
|---|---|---|
| G0 | Baseline de nove fontes e hashes preservados; implementaÃ§Ã£o original e decisÃµes | Baseline local registrada; nÃ£o Ã© cessÃ£o de direitos das fontes |
| G1 | Build .NET/frontend, lockfiles, health, fixture SQL; CI de build/protocolo/proxy/documentos no SHA 92e4006 | Provas por cenÃ¡rio; CI aprovada, sem novo aceite operacional ou promoÃ§Ã£o integral do gate |
| G-SEG | A/B/carteira/ID, CSRF, onboarding, revogaÃ§Ã£o e SQL RLS; navegador troca contexto/perfil | QA sintÃ©tico, limitado aos cenÃ¡rios registrados |
| G-CRM | ID persistente, concorrÃªncia, histÃ³rico, importaÃ§Ã£o e consumidor B | QA sintÃ©tico, sem aceite operacional |
| G-TASK | PrÃ³xima aÃ§Ã£o/encerramento/repetiÃ§Ã£o/contador e jornada na tela | QA sintÃ©tico; nÃ£o inclui calendÃ¡rio externo |
| G-MSG | Assinatura, ACK persistido, fila, A/B, eventos, unknown e reinÃ­cio do adapter local; texto real WazVox na 0.1.5 | Recebimento, resposta, entrega e leitura demonstrados no WazVox; aceite operacional pendente. Meta direto nÃ£o homologado |
| G-GED | VersÃµes/hashes/revisÃ£o/acesso e restore local | QA sintÃ©tico; scanner real e restore Azure pendentes |
| G-RC | Fontes, pacote, migration/restore local, guia e limites | Primeira entrega online; homologaÃ§Ã£o externa/aceite pendentes |
| G-SITE / G-FLOW | EspecificaÃ§Ãµes anteriores preservadas | Adiados, fora deste recorte |

Build, CI hospedada, autenticaÃ§Ã£o real, demonstraÃ§Ã£o sintÃ©tica, aceite do usuÃ¡rio e publicaÃ§Ã£o nÃ£o sÃ£o equivalentes. NÃ£o foi declarado que toda a plataforma/verticais do PDF estÃ¡ pronta.

## PrÃ³xima fronteira concreta

26 checks ao vivo e sessÃ£o preservada apÃ³s reinÃ­cio. SQL: identidade limitada, keyring cifrado e catÃ¡logo dos outros schemas preservado. [Prova online](../../evidencias/connect_primeira_entrega_online.json).

Continuidade publicada: probes HTTP/SQL de disponibilidade, sem redirecionamento nos caminhos internos exatos de health; correÃ§Ã£o 0.1.5 do contrato real WazVox. [Dez verificaÃ§Ãµes reais](../../evidencias/connect_wazvox_real_015.json) demonstram recebimento, resposta e leitura, com referÃªncia preservada e sem reenvio durante a correÃ§Ã£o. PrÃ³ximos passos: scanner privado, restauraÃ§Ã£o Azure e aceite; verificar a CI de cada prÃ³xima mudanÃ§a. A prova vale para essa conversa de texto; nÃ£o aprova campanhas, templates, mÃ­dia ou integraÃ§Ã£o Meta direta.

## CI hospedada observada nesta revisÃ£o

Em 07/10/2026, [Build EBT Connect, execuÃ§Ã£o 37712170407](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37712170407) terminou com `success` para `92e4006fc540d9884e412a65755eb032c3dec9bd`. Restore com lockfiles, build .NET Release, protocolo WazVox, proxy, npm ci/build/audit e validadores documentais passaram. [Registro sanitizado](../../evidencias/enterprise_continuidade_20261007.json).

Esse SHA identifica o candidato no GitHub, sem novo deploy. NÃ£o reexecutou SQL real, restore Azure ou navegador e nÃ£o fecha R01â€“R05 da revisÃ£o funcional. O hash de artefato publicado 0.1.5 permanece histÃ³rico; texto do checkpoint usa LF conforme Git. Gate, aceite e produÃ§Ã£o continuam separados.
