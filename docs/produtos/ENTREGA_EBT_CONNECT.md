# Primeira entrega: EBT Connect inicial

Execução autorizada em 07/10/2026: [estado real e provas](../qualidade/STATUS_IMPLEMENTACAO_CONNECT.md). Este documento preserva o plano/contrato candidato; não promover seus estados ou casos em lote.


Revisão de planejamento em 07/10/2026. Estado: planejado; nenhuma implementação, demonstração, homologação ou publicação desta entrega foi observada. Esta ficha compõe tickets existentes e não acrescenta horas.

## Objetivo e recorte

Permitir acompanhar um relacionamento comercial do cadastro ao resultado da tarefa usando o mesmo ID. Inclui organizações/contatos, busca e paginação, histórico com autoria/data, até cinco etapas fixas, responsável, próxima ação e tarefas do contato. Importação: um layout e até 100 contatos sintéticos, com preview e confirmação idempotente. Dois contextos sintéticos consomem o mesmo serviço/componente versionado.

O recorte cobre a entrada de contatos/histórico/tarefas de CON1 e um adapter delimitado de texto/resposta/status de CON3 do PDF mestre. São capacidades a demonstrar, não incrementos completos declarados prontos. Inbox coletivo avançado, automação/chatbot, campanhas, financeiro, OS e implantação de clientes reais ficam fora. [Contrato de API e webhook](../arquitetura/CONNECT_API_E_WEBHOOK.md).

## Etapas dentro da capacidade existente

| Recorte | Horas | Acumulado | Prova necessária |
|---|---:|---:|---|
| P01: baseline, direitos, fluxo e contratos | 12h | 12h | G0; árvore local e cenário por versão |
| P02: fundação e QA próprio | 16h | 28h | G1; clone/build, health, persistência sintética |
| P04: sessão, isolamento e auditoria | 36h | 64h | G-SEG; SQL real, onboarding, A/B, carteira e ID direto |
| P05: jornada CRM | 28h | 92h | G-CRM; cadastro/histórico/etapa/próxima ação persistidos |
| P07: tarefas do contato e composição Connect | 12h | 104h | G-TASK mais G-SEG/G-CRM vigentes na versão final |
| P11: recebimento, resposta e status | 36h | 140h | G-MSG com prova do canal de QA e negativas |

54 tickets, 140h de esforço estimado, todos ainda planejados. CRM/tarefas são checkpoint de 42 tickets/104h. Ordem de pacotes: PAC-01, PAC-02, PAC-03, PAC-05, PAC-06, PAC-07, PAC-08, PAC-09, PAC-10, PAC-13, PAC-18, PAC-19, PAC-20. Site PAC-04 e Flow PAC-14/PAC-15 ficam adiados fora do ciclo; IDs foram preservados.

## Jornada obrigatória para demonstração

1. Ativar/autenticar um operador sintético e selecionar seu contexto autorizado.
2. Criar organização/contato; repetir a operação pertinente e recuperar o mesmo ID após reload.
3. Localizar pela busca, abrir detalhe e retornar conservando filtros/paginação.
4. Registrar conversa ou nota interna com autoria e instante correto; uma conversa antiga mantém sua data e ordenação.
5. Alterar etapa e definir responsável/prazo; recusar versão obsoleta e responsável de outro escopo.
6. Criar/acessar tarefa do mesmo contato; conferir próxima ação sem cópia divergente de prazo/responsável.
7. Concluir com resultado ou cancelar com motivo; repetir o comando sem duplicar histórico; reler em nova sessão.
8. Reconciliar pendências e contador; repetir em B e em perfil de consulta, incluindo negativas por ID e fora da carteira.

9. Receber mensagem de texto pelo webhook autenticado, localizá-la na conversa, confirmar resposta por API e acompanhar os callbacks do canal; disputar/repetir eventos e recuperar falhas sem envio duplicado por inferência.

A confirmação visual de salvar precisa corresponder a estado persistido. Uma nota manual não comprova envio, entrega ou resposta de WhatsApp/e-mail. P11 demonstra a mensagem externa e seus estados separados.

## Pontos de contrato a fechar antes da implementação

P01-04/P05-01: campos, cardinalidade, ID canônico, policies e mecanismo real de concorrência. P05-05/P07-01/P07-05: fonte única/coerente para próxima ação e tarefa, escolha da pendência principal e comportamento após fechamento. A tarefa usa contato como primeira origem; a ligação com documento fica para P06, preservando o contrato da fonte quando compatível.

P05-03: registrar se a exportação já prevista existe na fonte selecionada, formato, colunas, limite e se representa página ou filtro inteiro. Usar o mesmo escopo autorizado na consulta e no resultado; acesso negado, carteira alheia e B recebem negativas específicas. Uma nova exportação ampla não entra por inferência.

P05-09: preview não persiste cadastro definitivo; a confirmação revalida usuário, tenant/carteira, layout e conteúdo preparado. Fixar escopo da chave de repetição e identidade do lote. Repetição após perda de resposta retorna o mesmo resultado; mesma chave com conteúdo diferente, duas confirmações concorrentes, permissão revogada ou dados alterados não geram duplicidade nem gravação parcial. Os resultados por linha/lote permanecem consultáveis.

## Fechamento do Connect em QA

P07-06 reconcilia os critérios/casos de P05 e P07; P05-10 sozinho fecha somente G-CRM. Registrar commit/hash, configurações A/B, fontes/direitos, comandos e resultados por cenário, capturas realmente inspecionadas, manual e pendências. Novas rotas, vínculos, queries ou mutations de P05/P07 exigem negativas na versão final; G-SEG de uma versão anterior não se transfere automaticamente.

P11-12 fecha a composição com comunicação em 140h, incluindo a jornada anterior e G-MSG. Os gates precisam concordar com a versão entregue e não podem conter falha de segurança, identidade, persistência ou critério obrigatório pendente. R2/N é proporcional ao risco; não repetir todas as suítes das fontes por rotina. Se faltar prova externa, G-MSG fica pendente; uma demonstração local parcial não homologa WhatsApp. O orçamento reserva tempo dentro dos tickets para verificação; se o recorte exceder o timebox, registrar horas reais e aplicar reserva/corte, sem declarar caso não executado como aprovado.

## Implantação e próximas entregas

Os marcos de 104h e 140h são demonstrações em QA, condicionadas aos gates. G-RC integrado continua em 180h e inclui migration/restore, manifesto e operação. Implantação real exige candidato do recorte, destino confirmado, retorno/recuperação ensaiados, dados/contas autorizados e aceite com autoria. Se houver demanda de implantação antes de 180h, replanejar parte de P09 para um candidato Connect e registrar impacto nos demais recortes; não adicionar essas horas silenciosamente.

Depois: documentos privados e vínculo documental em 164h; candidato integrado em 180h. Site e Flow estão no backlog posterior, sem consumo nas 200h. A reserva de 20h pode ser usada antes desses marcos. Se faltar capacidade, recortar/adiar GED com impacto explícito no candidato; isolamento, recuperação e comunicação essencial permanecem prioritários.

[Plano atual](../PLANO_200_HORAS.md) | [Cadastro e CRM P05](CRM_CONNECT_INICIAL.md) | [Tarefas P07](../execucao/fases/P07.md) | [Revisão](../qualidade/REVISAO_PROJETO_CONNECT.md) | [Contrato estruturado](../../planejamento/entrega_connect.json)
