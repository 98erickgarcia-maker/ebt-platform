# Estado de implementação do Connect

**Revisão vigente de 08/10/2026:** 17 PAC conferidos; R01–R05 e proteções de scanner/liberação aplicados em candidato isolado. CI no SHA `1fef14d4dc9a0ee7ac1ed9ffa6dbeccea48b7def` passou em build, 30 HTTP, sete SQL, 11 browser, ClamAV real/EICAR e dez verificações de restore. [Prova por versão e ambiente](../../evidencias/ci_pac_documental_20261008.json) e [sequência aplicada](../execucao/VERIFICACAO_SEQUENCIA_PAC_20261008.md). Scanner privado em Azure, PITR/certificado Azure e aceite operacional permanecem pendentes; nenhum gate integral foi promovido. O candidato está no [PR #13](https://github.com/98erickgarcia-maker/ebt-platform/pull/13), sem deploy desta revisão.

**Histórico da publicação de 07/10/2026:** primeira entrega publicada e 26 verificações ao vivo aprovadas. [Acesso e provas](../../PASSO_A_PASSO_PUBLICACAO_CONNECT.md). Banco pago compartilhado preservado; valor variável autorizado posteriormente. Referências abaixo a host inexistente/F1/R$30 fixos descrevem o cenário anterior e foram superadas por esta publicação. Fluxo real de texto WazVox demonstrado na 0.1.5. CI hospedada de build/protocolo/proxy/documentos aprovada para o checkpoint `92e4006`, conforme prova ao final.


07/10/2026. O pedido de programação substituiu a restrição anterior de planejamento. Código novo em `src/backend` e `src/frontend`, com fontes existentes preservadas. Estimativa mantida em 180h + 20h; não foi preenchido consumo fictício de horas.

O backlog e as 238 linhas da matriz documental são o plano-base, não o registro desta execução. Não foram promovidos em lote nem tratados como 238 testes aprovados. Evidência atual em [execucao_connect.json](../../evidencias/execucao_connect.json) e [manifesto do candidato](../../evidencias/manifesto_connect_local.json), com hashes, limites e referência aos testes.

## Capacidades locais implementadas

- Cadastro único de contato/organização, cinco etapas, responsável/carteira, nota com autoria e datas, pesquisa e paginação.
- Tarefa com responsável/prazo/resultado; próxima ação derivada das tarefas abertas; filtros de situação, responsável e prazo.
- CSV UTF-8 com preview/confirm delimitado; confirmação atômica e idempotente, sem importar dados dos projetos-fonte.
- Login, ativação por convite, cookie/CSRF, sessão revogável, perfis, troca de empresa, chaves de API e auditoria.
- Conversa, mensagem, fila durável de resposta, HMAC sobre envelope bruto, processamento de lote A/B, deduplicação, status fora de ordem e reconciliação de envio incerto.
- Documento privado com upload, versão, hash, aprovação/rejeição por versão, motivo e download autorizado; quotas do piloto.
- Schema SQL próprio, FKs de tenant, versão otimista, locks e barreira RLS; migration repetível, permissões separadas e comandos administrativos de bootstrap/canal.
- Interface React responsiva e testes HTTP, SQL direto, navegador, migration e restauração com massa sintética.

## Gates e limites

| Gate | Prova disponível | Estado honesto |
|---|---|---|
| G0 | Baseline de nove fontes e hashes preservados; implementação original e decisões | Baseline local registrada; não é cessão de direitos das fontes |
| G1 | Build .NET/frontend, lockfiles, health, fixture SQL; CI integrada no SHA 1fef14d | Provas por cenário; CI aprovada, sem novo aceite operacional ou promoção integral do gate |
| G-SEG | A/B/carteira/ID, CSRF, onboarding, revogação e SQL RLS; navegador troca contexto/perfil | QA sintético, limitado aos cenários registrados |
| G-CRM | ID persistente, concorrência, histórico, importação e consumidor B | QA sintético, sem aceite operacional |
| G-TASK | Próxima ação/encerramento/repetição/contador e jornada na tela | QA sintético; não inclui calendário externo |
| G-MSG | Assinatura, ACK persistido, fila, A/B, eventos, unknown e reinício do adapter local; texto real WazVox na 0.1.5 | Recebimento, resposta, entrega e leitura demonstrados no WazVox; aceite operacional pendente. Meta direto não homologado |
| G-GED | Versões/hashes/revisão/acesso, ClamAV real/EICAR e restore isolado na CI | QA sintético; scanner privado Azure e restore/certificado Azure pendentes |
| G-RC | Fontes, migration/restore isolado, runtime recuperado, download/A-B/traceId e guia | Candidato em CI; homologação externa/aceite pendentes |
| G-SITE / G-FLOW | Especificações anteriores preservadas | Adiados, fora deste recorte |

Build, CI hospedada, autenticação real, demonstração sintética, aceite do usuário e publicação não são equivalentes. Não foi declarado que toda a plataforma/verticais do PDF está pronta.

## Próxima fronteira concreta

Homologar scanner privado e PITR em destino Azure exclusivo, incluindo recuperação do certificado/keyring SQL cifrado, e obter aceite operacional. A fixture aprovada usa keyring de arquivos em Development. Ambiente desta revisão sem identidade/credenciais Azure configuradas; fonte atual de continuidade em [estado_continuidade.json](../../planejamento/estado_continuidade.json). As próximas provas devem registrar a própria versão/ambiente e preservar os outros schemas.

## Histórico ao vivo de 07/10/2026

26 checks ao vivo e sessão preservada após reinício. SQL: identidade limitada, keyring cifrado e catálogo dos outros schemas preservado. [Prova online](../../evidencias/connect_primeira_entrega_online.json).

Continuidade publicada: probes HTTP/SQL de disponibilidade, sem redirecionamento nos caminhos internos exatos de health; correção 0.1.5 do contrato real WazVox. [Dez verificações reais](../../evidencias/connect_wazvox_real_015.json) demonstram recebimento, resposta e leitura, com referência preservada e sem reenvio durante a correção. Próximos passos: scanner privado, restauração Azure e aceite; verificar a CI de cada próxima mudança. A prova vale para essa conversa de texto; não aprova campanhas, templates, mídia ou integração Meta direta.

## CI hospedada observada nesta revisão

Em 07/10/2026, [Build EBT Connect, execução 37712170407](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37712170407) terminou com `success` para `92e4006fc540d9884e412a65755eb032c3dec9bd`. Restore com lockfiles, build .NET Release, protocolo WazVox, proxy, npm ci/build/audit e validadores documentais passaram. [Registro sanitizado](../../evidencias/enterprise_continuidade_20261007.json).

Esse SHA identifica o candidato no GitHub, sem novo deploy. Não reexecutou SQL real, restore Azure ou navegador e não fecha R01–R05 da revisão funcional. O hash de artefato publicado 0.1.5 permanece histórico; texto do checkpoint usa LF conforme Git. Gate, aceite e produção continuam separados.
