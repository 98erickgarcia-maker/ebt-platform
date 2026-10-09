"""Revisão documental: Connect primeiro, sem executar módulos ou criar horas."""
import json


CONNECT_PHASES = ['P01', 'P02', 'P04', 'P05', 'P07', 'P11']
PHASE_ORDER = CONNECT_PHASES + ['P06', 'P09', 'P10']


def emit_connect(data, emit):
    phases = {p['id']: p for p in data['fases']}
    items = data['itens']
    tickets = [t['id'] for t in items if t['fase'] in CONNECT_PHASES]
    assert len(tickets) == 54
    assert sum(t['horas'] for t in items if t['id'] in tickets) == 140
    contract = dict(
        revisao='07/10/2026', produto='EBT Connect inicial', estado='planejado',
        evidencia_execucao=None, fonte='planejamento/backlog_200_horas.json',
        fases=CONNECT_PHASES, tickets=tickets, horas_incluidas=140,
        gates=['G0', 'G1', 'G-SEG', 'G-CRM', 'G-TASK', 'G-MSG'],
        marcos_h={'seguranca': phases['P04']['fim_h'],
                  'crm': phases['P05']['fim_h'],
                  'connect_com_tarefas': phases['P07']['fim_h'],
                  'connect_com_comunicacao': phases['P11']['fim_h']},
        natureza='Demonstração em QA; implantação e aceite reais pendentes',
        escopo=['cadastro único', 'organizações e contatos', 'histórico',
                'até cinco etapas', 'responsável e próxima ação',
                'tarefas do contato', 'duas configurações sintéticas',
                'importação fixa de até 100 contatos sintéticos',
                'recebimento de texto por webhook', 'resposta do atendente por API',
                'callbacks de status e tratamento de falha'],
        fora=['inbox coletivo avançado', 'campanhas automáticas',
              'chatbot', 'financeiro', 'OS', 'Connect CON2/CON4/CON5 completos'],
        total_h=data['total_h'], entregas_h=data['entregas_h'],
        reserva_h=data['reserva_h'], horas_adicionais=0,
    )
    emit('planejamento/entrega_connect.json', json.dumps(contract, ensure_ascii=False, indent=2))

    overview = '''# EBT Platform: primeiras 200 horas com Connect primeiro

Revisão de prioridade: 07/10/2026. O usuário pediu revisão começando pelo EBT Connect e autorizou a escolha do planejamento mais válido. Este plano prioriza uma jornada comercial completa antes do site e do GED. Implementação dos módulos permanece planejada.

**70 entregas, 180h; cinco reservas condicionais, 20h. Total: 200 horas-pessoa.** Implementação, verificação e registro estão incluídos. Site e Flow, 14 tickets/36h, ficam no backlog posterior; 12 tickets/36h de comunicação entram no ciclo. IDs existentes são preservados; a numeração de fase/pacote identifica o recorte, não sua posição na fila.

## Primeiras entregas e prova necessária

| Ordem | Resultado candidato | Janela de esforço | Gate e limite |
|---|---|---:|---|
| Preparação | Baseline e fundação isolada | 0-28h | G0/G1; nenhuma jornada comercial homologada |
| 1a | Segurança do Connect | 28-64h | G-SEG; SQL real, onboarding e negativas A/B |
| 1b | Cadastro, histórico, funil e próxima ação | 64-92h | G-CRM; ainda falta a jornada completa de tarefas |
| 1c | Connect com tarefas do contato | 92-104h | G-TASK; checkpoint dentro da primeira entrega |
| 1 | EBT Connect inicial com API e webhook | 104-140h | G-MSG mais G0/G1/G-SEG/G-CRM/G-TASK vigentes; demonstração em QA |
| 2 | Documentos privados | 140-164h | G-GED; upload, versão, revisão, download e recuperação |
| 3 | Candidato integrado e operação | 164-180h | G-RC; migration/restore, manifesto e preparação do aceite |
| Reserva | Correções comprovadas | 20h utilizáveis em qualquer fase | Sem funcionalidade nova ou consumo obrigatório |

As linhas 1a/1b/1c são checkpoints dentro das 140h do Connect, sem dupla contagem. WhatsApp oficial é o primeiro canal candidato, com conta/versão/escopos e homologação a confirmar. Demonstração em QA, homologação do usuário e liberação são estados separados. G-RC integrado permanece em 180h; antecipar uma implantação do Connect exige pacote operacional próprio, provas e replanejamento explícito. Site e Flow não são dependências do candidato deste ciclo.

## Distribuição das 200 horas

| Fase | Horas | Janela | Acumulado | Itens | Saída |
|---|---:|---:|---:|---:|---|
'''
    for p in data['fases']:
        overview += f"| {p['id']} {p['nome']} | {p['horas']}h | {p['inicio_h']}-{p['fim_h']}h | {p['fim_h']}h | {len(p['tickets'])} | {p['resultado']} |\n"
    overview += '''
## Decisões desta revisão

P07 depende do cadastro/CRM e da segurança vigente. A primeira origem da tarefa é o contato; GED deixa de bloquear essa jornada. O contrato pode manter tipos de origem compatíveis com a fonte, mas vínculo documental só é demonstrado após P06-02/P06-08. Próxima ação e tarefa devem usar uma fonte de estado consistente, definida antes de implementar, sem duas cópias editáveis de prazo/responsável. P11 é capacidade nova de 36h, com contratos próprios e gate G-MSG, usando referências oficiais externas ao CASST.

Lista/busca do CRM e criação/lista de tarefas usam R2 como ponto de partida. Qualquer fronteira nova de tenant, autorização, schema, contrato ou storage recebe N nos cenários afetados. R1 fica restrito a componentes e cenários cuja equivalência estiver demonstrada.

O PDF consolidado de 06/10/2026 permanece preservado como histórico, com a ordem antiga. Esta revisão, o backlog JSON e as fichas regeneradas têm precedência para a próxima execução. Nenhuma evidência histórica foi atualizada para aparentar execução nova.

## Leitura e execução futura

- [Contrato da primeira entrega Connect](produtos/ENTREGA_EBT_CONNECT.md).
- [Resposta por API e webhook](arquitetura/CONNECT_API_E_WEBHOOK.md).
- [Site e Flow adiados](../planejamento/backlog_apos_200_horas.json).
- [Revisão do projeto e correções de planejamento](qualidade/REVISAO_PROJETO_CONNECT.md).
- [Backlog detalhado](BACKLOG_200_HORAS.md).
- [Dependências e gates](execucao/DEPENDENCIAS.md).
- [Pacotes na ordem de esforço](execucao/PACOTES_CODEX.md).
- [Validação proporcional](VALIDACAO_E_GATES.md).
- [Fonte de horas e status](../planejamento/backlog_200_horas.json).
- [PDF histórico de 06/10/2026](../output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).
'''
    emit('docs/PLANO_200_HORAS.md', overview)

    backlog = '''# Backlog detalhado: 200 horas

Revisão de prioridade: 07/10/2026. Connect com tarefas e comunicação é a primeira demonstração prevista, em 140h cumulativas, com checkpoint CRM/tarefas em 104h. Site e Flow ficam no backlog posterior. As janelas seguem a nova ordem; nenhuma hora real de execução foi presumida. Todos os itens ativos estão planejados. RES representa capacidade contingente, sem entrega funcional presumida.

'''
    for phase in data['fases']:
        backlog += f"## {phase['id']} | {phase['nome']} | {phase['horas']}h | acumulado {phase['fim_h']}h\n\n"
        backlog += f"Resultado: {phase['resultado']}. Gate: {phase['gate']}. Origem: {phase['origem']}.\n\n"
        for t in (x for x in items if x['fase'] == phase['id']):
            backlog += f"### {t['id']} | {t['titulo']} | {t['horas']}h | {t['trilha']}\n\n"
            backlog += f"- Dependências: {', '.join(t['dependencias']) or 'nenhuma'}.\n"
            backlog += f"- Janela de esforço: {t['inicio_h']}-{t['fim_h']}h.\n"
            backlog += f"- Aceite: {t['criterio_aceite']}\n"
            backlog += f"- Evidência: {t['evidencia_esperada']}.\n"
            backlog += f"- Composição: implementação {t['implementacao_h']:g}h, verificação {t['verificacao_h']:g}h, registro {t['registro_h']:g}h, reserva {t['reserva_h']:g}h.\n"
            backlog += f"- Estado: {t['status']}. Responsável proposto: {t['responsavel_proposto']}.\n\n"
    emit('docs/BACKLOG_200_HORAS.md', backlog)

    emit('docs/produtos/ENTREGA_EBT_CONNECT.md', '''# Primeira entrega: EBT Connect inicial

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
''')

    emit('docs/qualidade/REVISAO_PROJETO_CONNECT.md', '''# Revisão do projeto começando pela entrega EBT Connect

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
''')


def finalize_documents(data, generated, emit):
    """Atualiza navegação e preserva os recortes adiados com IDs originais."""
    delayed = data['adiados']
    emit('planejamento/backlog_apos_200_horas.json', json.dumps(dict(
        revisao='07/10/2026', motivo='Priorizar resposta por API/webhook no Connect',
        horas_alocadas_neste_ciclo=0, estimativa_anterior_h=36,
        fases=delayed['fases'], itens=delayed['itens'],
        regra='Estimativas anteriores não são compromisso novo; reestimar antes de executar.'),
        ensure_ascii=False, indent=2))
    for phase in delayed['fases']:
        content = f"# {phase['id']} | {phase['nome']}\n\nRecorte adiado para depois deste ciclo de 200h, por prioridade do Connect com API/webhook. Nenhum módulo executado. IDs e critérios originais preservados; zero horas alocadas neste ciclo. Estimativa anterior: {phase['horas']}h, a reavaliar. A janela antiga não é uma janela vigente.\n\n"
        for item in (t for t in delayed['itens'] if t['fase'] == phase['id']):
            content += f"- [{item['id']}](../entregas/{item['id']}.md): {item['titulo']} ({item['horas']}h anteriores).\n"
            emit(f"docs/execucao/entregas/{item['id']}.md", f"# {item['id']} | {item['titulo']}\n\nAdiado fora das 200h; não executado. Estimativa anterior: {item['horas']}h; zero horas alocadas no ciclo atual.\n\n## Critério preservado para replanejamento\n\n{item['criterio_aceite']}\n\nOrigem: {item['origem']}. Trilha anterior: {item['trilha']}; reavaliar pela versão/fronteira antes de executar.\n\n[Voltar ao recorte](../fases/{phase['id']}.md) | [Backlog posterior](../../../planejamento/backlog_apos_200_horas.json)\n")
        content += '\n[Backlog posterior](../../../planejamento/backlog_apos_200_horas.json) | [Plano vigente](../../PLANO_200_HORAS.md)\n'
        emit(f"docs/execucao/fases/{phase['id']}.md", content)
    for ident, phase in [('PAC-04', 'P03'), ('PAC-14', 'P08'), ('PAC-15', 'P08')]:
        emit(f'docs/execucao/pacotes/{ident}.md', f'# {ident} | Recorte adiado\n\nEste pacote pertence a {phase} e está fora da capacidade atual de 200h. Não foi executado, excluído ou contado como reserva. Reestimar com a fonte/ambiente disponíveis antes da próxima execução.\n\n[Recorte preservado](../fases/{phase}.md) | [Pacotes ativos](../PACOTES_CODEX.md)\n')

    cases = len(json.loads(generated['planejamento/cenarios_verificacao.json'])['casos'])
    for path in ['docs/qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md',
                 'docs/execucao/EXECUCAO_PELO_CODEX.md',
                 'docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md',
                 'docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md']:
        value = generated[path].replace('234 casos', f'{cases} casos')
        value = value.replace('77 tickets', '75 tickets').replace('77 fichas', '75 fichas')
        lines = value.splitlines()
        lines.insert(2, 'Revisão vigente 1.3 (07/10/2026): Connect com API/webhook primeiro; 70 entregas e cinco reservas, 180h + 20h. Site/Flow estão adiados. Seguir [plano atual](../PLANO_200_HORAS.md) e pacotes em ordem de esforço; as decisões de 06/10 abaixo são contexto do método original.\n')
        emit(path, '\n'.join(lines))

    readme = '''# EBT Platform | Planejamento do Connect com API e webhook

Revisão 1.3 em 07/10/2026. Implementação dos módulos ainda planejada. Prioridade: uma jornada de CRM, tarefas e resposta por canal oficial, usando CASST como fonte seletiva e referências oficiais de comunicação.

70 entregas ativas (180h) e cinco reservas condicionais (20h). Site e Flow, 14 tickets/36h, foram adiados; P11 adiciona 12 tickets/36h de comunicação. IDs, critérios dos recortes adiados, fontes e complementos de frontend foram preservados.

## Comece aqui

- [Primeira entrega EBT Connect](docs/produtos/ENTREGA_EBT_CONNECT.md).
- [Como será a resposta por API e webhook](docs/arquitetura/CONNECT_API_E_WEBHOOK.md).
- [Plano atual das 200h](docs/PLANO_200_HORAS.md).
- [Índice geral](docs/INDICE_GERAL.md).
- [Revisão e achados documentais](docs/qualidade/REVISAO_PROJETO_CONNECT.md).
- [17 pacotes ativos na ordem correta](docs/execucao/PACOTES_CODEX.md).
- [Dependências e gates](docs/execucao/DEPENDENCIAS.md).
- [Revisão de frontend preexistente](docs/frontend/REVISAO_E_PRIORIDADES.md).
- [Site e Flow preservados no backlog posterior](planejamento/backlog_apos_200_horas.json).

## Marcos de esforço e limite de prova

| Resultado candidato | Acumulado | Gate |
|---|---:|---|
| Baseline/fundação isolada | 28h | G0/G1 |
| Segurança | 64h | G-SEG |
| Cadastro/histórico/funil/próxima ação | 92h | G-CRM |
| CRM com tarefas do contato | 104h | G-TASK |
| Connect com recebimento/resposta/status | 140h | G-MSG e gates anteriores na versão final |
| Documentos privados | 164h | G-GED |
| Candidato integrado e operação | 180h | G-RC |
| Reserva condicional | 20h em qualquer fase | Consumo mediante necessidade comprovada |

As horas não são prazo de calendário. 104h/140h representam demonstrações em QA, dependentes de provas; não significam aceite de cliente ou produção. WhatsApp oficial é o primeiro canal candidato; conta/versão/políticas e homologação continuam pendentes. Nenhum serviço foi contratado ou conectado.

## Fontes de verdade e documentos

Horas, IDs, status e recortes ativos/adiados: planejamento/backlog_200_horas.json. Fichas: scripts/catalogo_organizacao.py. Conteúdo geral: scripts/conteudo_organizacao.py. Composição da entrega: scripts/connect_planejado.py. Contratos/tickets de comunicação: scripts/comunicacao_planejada.py. Pacotes: scripts/pacotes_codex.py. Gerar com scripts/organizar_projeto.py; o manifesto protege alterações manuais nos gerados.

O [OpenAPI candidato](planejamento/connect_api.openapi.json) documenta paths/schemas futuros, não uma API operacional. A [evidência da revisão](evidencias/revisao_connect_planejamento.json) verifica o planejamento, sem mudar estados de produto. O [PDF de 06/10/2026](output/pdf/EBT_Plano_Primeiras_200_Horas.pdf) permanece histórico, com a ordem anterior; o plano JSON/Markdown revisado tem precedência. O gerador histórico planejar.py permanece protegido.

## Verificar os documentos

```powershell
python scripts/verificar_plano.py
python scripts/verificar_organizacao.py --no-write
```

Esses comandos verificam orçamento, dependências, fichas, schemas e hashes. Não executam aplicações CASST/Vikings, SQL, Meta, browser ou produção. Antes da implementação, ler AGENTS.md, REVISAO_BASES.md e VALIDACAO_E_GATES.md. Fontes históricas precisam de versão/cenário; fronteiras novas exigem N.
'''
    emit('README.md', readme)
    index = generated['docs/INDICE_GERAL.md']
    index = index.replace('Versão de organização 1.2.', 'Versão de organização 1.3, revisão de 07/10/2026.')
    index = index.replace('72 entregas + cinco reservas', '70 entregas + cinco reservas')
    index = index.replace('complemento 1.2 nos documentos de execução pelo Codex.', 'PDF histórico; plano e contratos 1.3 têm precedência para execução futura.')
    index = index.replace('## Dez fases e todas as fichas', '## Nove fases ativas e suas fichas')
    index += '''
## Primeira entrega, comunicação e backlog posterior

- [ENTREGA EBT CONNECT](produtos/ENTREGA_EBT_CONNECT.md).
- [CONNECT API E WEBHOOK](arquitetura/CONNECT_API_E_WEBHOOK.md).
- [REVISAO PROJETO CONNECT](qualidade/REVISAO_PROJETO_CONNECT.md).
- [Contrato estruturado da entrega](../planejamento/entrega_connect.json).
- [OpenAPI candidato](../planejamento/connect_api.openapi.json).
- [Site P03 adiado](execucao/fases/P03.md).
- [Flow P08 adiado](execucao/fases/P08.md).
- [Backlog após 200h](../planejamento/backlog_apos_200_horas.json).
- [Evidência da revisão](../evidencias/revisao_connect_planejamento.json).
'''
    emit('docs/INDICE_GERAL.md', index)
    emit('CONTINUAR_EM_OUTRO_CHAT.md', '''# Continuar EBT Connect

Estado: planejamento 1.3 de 07/10/2026; 70 entregas futuras/180h e cinco reservas/20h. Nenhum módulo implementado. Prioridade: CRM/tarefas em 104h, comunicação por API/webhook em 140h, GED em 164h e candidato em 180h. Site/Flow adiados e preservados no backlog posterior. WhatsApp oficial é candidato; acesso ao canal permanece pendente.

Ler AGENTS.md, docs/PLANO_200_HORAS.md, docs/REVISAO_BASES.md, docs/VALIDACAO_E_GATES.md, docs/produtos/ENTREGA_EBT_CONNECT.md e docs/arquitetura/CONNECT_API_E_WEBHOOK.md. Quando a implementação for autorizada, começar PAC-01 e seguir a ordem de esforço em docs/execucao/PACOTES_CODEX.md, preservando fontes/alterações existentes. Numeração de pacote/fase não é ordem cronológica.

Fonte de horas/status: planejamento/backlog_200_horas.json. OpenAPI é contrato candidato, não endpoint em produção. PDF anterior é histórico. Revalidar versão/cenário antes do reuso; ACK, fila, aceite do provedor, entrega e leitura são provas distintas. Não copiar segredos/dados reais; registrar apenas resultados observados.

Ao continuar execução, informar commit, ticket/gate, ambiente, provas/falhas, horas reais/saldo e próximo passo. Preferência prévia de continuar no próprio Codex preservada; ver docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md.
''')
    change = generated['docs/CHANGELOG.md']
    change = change.replace('# Registro de versões do planejamento\n\n', '''# Registro de versões do planejamento

## 1.3 | 07/10/2026

Revisão solicitada a partir do Connect, com liberdade de escolher o planejamento mais válido e pedido adicional de resposta por API/webhook. CRM/tarefas antecipados; 36h de site/Flow adiadas e realocadas a 12 tickets novos de comunicação N. Ciclo ativo: 70 entregas/180h + cinco reservas/20h. Contrato da primeira entrega, OpenAPI candidato, desenho inbox/outbox/status/retry, referências oficiais e critérios de comunicação. Pacotes existentes preservam IDs; três pacotes P11 entram na fila. Fontes, complementos locais de frontend, estados e PDF histórico preservados; nenhum módulo, envio, conexão ou produção executados.

''', 1)
    emit('docs/CHANGELOG.md', change)

    from pathlib import Path
    execution = Path(__file__).resolve().parents[1] / 'evidencias/execucao_connect.json'
    if execution.exists():
        current = generated['README.md'].splitlines()
        current[0] = '# EBT Platform | EBT Connect implementado em QA local'
        current[2] = '07/10/2026: implementação autorizada e candidato local .NET/React/SQL disponível. Banco de implantação: Azure existente sqldb-crm-casst-dev-v2, schema ebt_connect; nenhum novo banco Azure ou mudança de plano. Produção, canal Meta real, scanner e aceite permanecem pendentes.'
        current[3:3] = ['', '- [Executar e verificar o Connect](PASSO_A_PASSO_EBT_CONNECT.md).', '- [Estado real da implementação e dos gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md).', '- [Contrato API/webhook implementado](docs/api/CONNECT_V1.md).', '- [Implantação preparada no banco existente](docs/execucao/IMPLANTACAO_CONNECT_AZURE.md).', '- [Registro atual de execução](evidencias/execucao_connect.json).', '', 'As seções de orçamento abaixo preservam o plano-base; estados planejados não substituem o registro de execução.', '']
        emit('README.md', '\n'.join(current))
        for path in ['docs/INDICE_GERAL.md','docs/VALIDACAO_E_GATES.md','docs/PLANO_200_HORAS.md','docs/BACKLOG_200_HORAS.md','docs/produtos/ENTREGA_EBT_CONNECT.md','docs/arquitetura/CONNECT_API_E_WEBHOOK.md']:
            if path not in generated: continue
            lines = generated[path].splitlines()
            import os
            link = os.path.relpath(execution.parent.parent/'docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md', execution.parent.parent/Path(path).parent).replace('\\','/')
            lines[1:1] = ['', 'Execução autorizada em 07/10/2026: [estado real e provas]('+link+'). Este documento preserva o plano/contrato candidato; não promover seus estados ou casos em lote.', '']
            emit(path, '\n'.join(lines))
        emit('CONTINUAR_EM_OUTRO_CHAT.md', '# Continuar EBT Connect\n\nProgramação autorizada. Candidato local implementado; banco Azure existente sqldb-crm-casst-dev-v2/schema ebt_connect, sem novo banco ou SKU. Ler [guia](PASSO_A_PASSO_EBT_CONNECT.md), [registro de execução](evidencias/execucao_connect.json), [gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md) e [implantação](docs/execucao/IMPLANTACAO_CONNECT_AZURE.md).\n\nFontes preservadas. SQL local sintético; nenhuma migration Azure, publicação ou mensagem real. Bloqueio SQL40615/firewall; usar acesso autorizado. Meta/ClamAV/CI hospedada/aceite pendentes. Não confundir os 238 cenários planejados com a suíte executada. 180h + 20h são estimativas preservadas, sem consumo fictício. Não criar outro banco Azure, copiar segredos de clientes, resetar fontes ou publicar alterações acumuladas sem isolamento.\n')

        if (execution.parent / "integracao_wazvox_execucao.json").exists():
            wazvox_note = 'Atualização de 07/10: adaptador WazVox 0.1.1 implementado e testado localmente; chave exclusiva criada com autorização e API real conferida para leitura. Webhook público e envio real continuam pendentes. [Guia da integração](PASSO_A_PASSO_WAZVOX_CONNECT.md) · [Destino Azure preparado](docs/execucao/DESTINO_CONNECT_WAZVOX_AZURE.md).'
            continuation_note = 'Atualização: WazVox API real verificada para leitura, chave EBT Connect criada com autorização e cifrada por DPAPI fora do Git. Adaptador 0.1.1, protocolo 14/14 e HTTP/SQL 11/11; regressão 25/25 e migration/restore repetidos. [Integração WazVox](PASSO_A_PASSO_WAZVOX_CONNECT.md), [evidência](evidencias/integracao_wazvox_execucao.json), [destino Azure proposto](docs/execucao/DESTINO_CONNECT_WAZVOX_AZURE.md). Meta sem acesso ao portfólio da WABA; webhook público/envio/callback real e aprovação de implantação/custo pendentes. O usuário autorizou preparar o destino Azure, não publicar. API QA local ativa nesta entrega, sem chave real de provedor.'
            emit("README.md", generated["README.md"].replace("# EBT Platform | EBT Connect implementado em QA local\n\n", "# EBT Platform | EBT Connect implementado em QA local\n\n" + wazvox_note + "\n\n", 1))
            emit("CONTINUAR_EM_OUTRO_CHAT.md", generated["CONTINUAR_EM_OUTRO_CHAT.md"].replace("# Continuar EBT Connect\n\n", "# Continuar EBT Connect\n\n" + continuation_note + "\n\n", 1))

        if (execution.parent / "azure_connect_schema_aplicado.json").exists():
            azure_note = 'Atualização 0.1.2: oito migrations aplicadas no schema ebt_connect do banco Azure existente, catálogo dos outros schemas preservado e regra temporária de firewall removida. Keyring SQL cifrado e proxy verificados; pacote executado localmente. Publicação autorizada com somente R$ 30 fixos. Azure F1 recusado por cota zero; nenhum host/plano pago criado. Webhook público/envio real pendentes. [Publicação e retomada](PASSO_A_PASSO_PUBLICACAO_CONNECT.md) · [Evidência Azure](evidencias/azure_connect_publicacao.json).'
            current = generated['README.md'].replace(wazvox_note, azure_note)
            current = current.replace('# EBT Platform | EBT Connect implementado em QA local', '# EBT Platform | EBT Connect com schema Azure preparado', 1)
            current = current.replace('07/10/2026: implementação autorizada e candidato local .NET/React/SQL disponível. Banco de implantação: Azure existente sqldb-crm-casst-dev-v2, schema ebt_connect; nenhum novo banco Azure ou mudança de plano. Produção, canal Meta real, scanner e aceite permanecem pendentes.', '07/10/2026: candidato .NET/React/SQL 0.1.2 disponível; schema aplicado no SQL Azure existente. Não há aplicação pública. Hospedagem gratuita bloqueada por cota F1 zero; limite de gasto adicional somente R$ 30 fixos. Canal real, scanner e aceite continuam pendentes.')
            emit('README.md',current)
            emit('CONTINUAR_EM_OUTRO_CHAT.md', '# Continuar EBT Connect\n\n' + azure_note + '\n\nLer [publicação](PASSO_A_PASSO_PUBLICACAO_CONNECT.md), [registro de execução](evidencias/execucao_connect.json), [gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md) e [WazVox](PASSO_A_PASSO_WAZVOX_CONNECT.md). Próxima ação: liberar uma instância F1 no Azure ou disponibilizar hospedagem compatível sem cobrança adicional. Não ativar Consumption/build pago como fallback. Runtime identity, certificado privado, bootstrap real, HTTPS e assinatura WazVox dependem do host. Chave WazVox criada e cifrada por DPAPI fora do Git. Meta sem acesso ao portfólio WABA; nenhum envio real. Fontes/alterações preservadas. Oito migrations no SQL existente; nenhuma seed QA ou identidade de outro produto copiada. Firewall temporário removido. Não restaurar/excluir schema no banco compartilhado como rollback. Os 238 casos permanecem planejados; 180h + 20h são estimativas, sem consumo fictício.\n')
