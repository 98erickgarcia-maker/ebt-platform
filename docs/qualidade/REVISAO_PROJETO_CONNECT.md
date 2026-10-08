# Revisão do projeto começando pela entrega EBT Connect

Data: 07/10/2026. Escopo: planejamento, contratos candidatos, dependências, cenários, pacotes, geradores e preservação da árvore local. Não é auditoria nova das aplicações CASST/Vikings, teste autenticado ou prova de produção. O usuário autorizou escolher o planejamento mais válido; a distribuição 180h + 20h foi mantida.

## Resultado

Connect passa a ser a primeira demonstração útil, incluindo tarefas do contato e comunicação. Baseline/fundação 28h, segurança 36h, CRM 28h e tarefas 12h formam o checkpoint de 104h; API/webhook tem bloco próprio de 36h até 140h. GED vem em 164h e candidato integrado em 180h. Site e Flow, 14 tickets/36h, foram adiados; 12 tickets de comunicação/36h entraram. O ciclo ativo tem 70 entregas e cinco reservas. Estas são estimativas de esforço futuro.

## Achados documentais e tratamento

| Prioridade | Referência na versão anterior | Cenário e impacto | Ajuste realizado |
|---|---|---|---|
| Alto | P07-01: entrada G-CRM/G-GED; dependência P06-GATE | Tarefa comercial de contato aguarda upload/revisão documental, adiando a jornada básica do Connect até 140h | P07 passa a depender de P05; primeira origem é contato. Composição documental fica em P06-02/P06-08 |
| Médio | P05-03 e P07-02: R1, 15 minutos de verificação | Um novo consumidor, filtro/vínculo ou policy pode receber apenas smoke por causa do rótulo inicial; as fichas já exigiam reavaliar, mas a capacidade não reservava R2 | R2 inicial e 30 minutos de verificação por item, compensados dentro das mesmas horas; N nas fronteiras novas |
| Médio | P05-03-C01 a C03 | Aceite previa exportação com escopo, mas casos enumerados cobriam busca, estados e paginação. Uma exportação poderia ficar fora da demonstração específica | Acrescentadas negativas A/B/carteira, preservação de filtro e contrato de exportação quando incluída |
| Médio | P05-09-C01 a C03 | Preview/erro/reenvio simples não explicavam lote alterado, duas confirmações ou perda de resposta; o aceite exigia ausência de gravação parcial | Acrescentados cenários de confirmação revalidada, payload/chave, concorrência e falha transacional; lote segue sintético e até 100 contatos |
| Médio | P05-05/P07-05 e modelo de próxima ação/tarefa | Dois registros editáveis de responsável/prazo podem deixar lista, detalhe e painel divergentes; isto é risco de implementação, não defeito observado em código | Decisão de fonte coerente antes da implementação e cenário de sincronismo/fechamento em P07 |
| Médio | P05-10 e G-RC em P09 | Confundir G-CRM com entrega completa do Connect ou liberação operacional ignora tarefas e ensaios de release posteriores | Ficha de entrega combina P05/P07 e gates na versão final; 104h é QA, G-RC permanece 180h |

As correções são de planejamento. R1 nas fichas antigas tinha uma regra de promoção, portanto a revisão não afirma que uma fronteira insegura foi implementada. Não foi constatado defeito funcional das bases por estes achados.

## Revisão dos demais recortes

P01/P02 continuam obrigatórios: árvore real, direitos de uso, contratos, massa própria, ambiente e build reproduzível. Falha histórica de onboarding é uma pendência de origem, sem reexecução nesta revisão; G-SEG continua bloqueando os consumidores quando faltam provas.

Site e Flow mantêm especificações/IDs/estimativas no backlog posterior, com zero horas alocadas neste ciclo. GED preserva 24h, storage privado, autorização por ID, revisão por versão e restore. Tarefa não concede acesso ao arquivo; ligação documental só é exercitada após seu gate. P09 mantém 16h e exige resultados integrados de CRM/tarefas/comunicação/documentos na versão candidata. Se comunicação/extração exigir mais capacidade, recortar GED e replanejar o candidato explicitamente.

O PDF mestre usa CON1 para contatos/organizações/histórico/tarefas e CON2-CON5 para inbox, WhatsApp, automação e campanhas. A versão final deste plano combina um recorte de CON1 e um adapter limitado de CON3, sem CON2/CON4/CON5 completos. O Core integral permanece posterior. [Desenho de comunicação e fontes oficiais](../arquitetura/CONNECT_API_E_WEBHOOK.md). PDF consolidado anterior é histórico; não deve ser usado como fila atual.

## Evidência e preservação

Antes das alterações, verificar_organizacao.py --no-write passou: 77 tickets planejados, 234 casos não executados, 17 pacotes e 200h. Foi preservado snapshot local dos 189 arquivos existentes e do estado Git em tmp/revisao-connect-20261007/antes. Projetos-fonte, PDF e snapshots históricos não foram alterados. Complementos de frontend preexistentes permanecem no gerador e nos documentos.

A verificação final, hashes e diferenças permitidas são registrados em [evidencias/revisao_connect_planejamento.json](../../evidencias/revisao_connect_planejamento.json). Ela comprova coerência documental e preservação conferida, sem mudar status de produto. Nenhum ticket foi marcado executado; nenhum cenário recebeu evidência fictícia.

[Entrega Connect](../produtos/ENTREGA_EBT_CONNECT.md) | [Plano](../PLANO_200_HORAS.md) | [Validação e gates](../VALIDACAO_E_GATES.md)
