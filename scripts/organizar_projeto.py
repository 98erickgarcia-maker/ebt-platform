"""Organiza a documentação a partir do orçamento existente, sem tocar projetos-fonte."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re,os,sys
from catalogo_organizacao import PHASE_CONTEXT,details
from conteudo_organizacao import DOCUMENTS,TEMPLATES
from pacotes_codex import WORKFLOW,TEMPLATE,AUTOMATION,NORMAL_CHAT,HANDOFF_TEMPLATE,emit_packages
from frontend_planejado import emit_frontend,TEMPLATE as FRONTEND_TEMPLATE
from connect_planejado import emit_connect, finalize_documents
from live_docs import finalize_live_documents
from comunicacao_planejada import emit_communication

DOCUMENTS['docs/execucao/EXECUCAO_PELO_CODEX.md']=WORKFLOW
DOCUMENTS['docs/execucao/EXECUCAO_PELO_CODEX.md']+='\n## Continuidade no próprio Codex\n\nRegra expressa do usuário: se já estiver no Codex, seguir normalmente com implementação autorizada, revisão, testes e navegador disponíveis. Não exigir outro chat ou retorno ao Codex por rotina. Sinal de passagem só quando faltar ferramenta/acesso à próxima prova; impedimento real mantém os gates e permite trabalho independente.\n'
DOCUMENTS['docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md']=NORMAL_CHAT
DOCUMENTS['docs/qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md']=AUTOMATION
DOCUMENTS['docs/execucao/EXECUCAO_PELO_CODEX.md']+='\n## Revisão online por código\n\nA rodada online será principalmente automatizada por testes de API e navegador contra a homologação, separados do código funcional. Conferência visual e aceite de negócio complementam os testes. Ver [especificação de revisão local/online](../qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md). Preparar a estrutura/comandos da suíte na fundação e acrescentar os casos pertinentes junto aos módulos. Essa suíte não foi criada pela revisão documental.\n'
TEMPLATES['PACOTE_CODEX.md']=TEMPLATE
TEMPLATES['PASSAGEM_CHATGPT_CODEX.md']=HANDOFF_TEMPLATE
TEMPLATES['REVISAO_FRONTEND.md']=FRONTEND_TEMPLATE
DOCUMENTS['docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md']+='\n## Pacotes maiores, decisão 1.2\n\nPara execução pelo Codex, acompanhar [17 pacotes](PACOTES_CODEX.md) e aplicar o [ciclo de revisão e continuidade](EXECUCAO_PELO_CODEX.md). Os mesmos 72 tickets continuam sendo checkpoints internos; as 180h incluem revisão/verificação/registro e a reserva permanece 20h. Começar pelo PAC-01 quando a implementação for solicitada.\n'

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'planejamento/manifesto_organizacao.json'
GENERATED={}
def sha(p):
    data=p.read_bytes() if p.suffix=='.pdf' else p.read_text(encoding='utf-8').encode('utf-8')
    return hashlib.sha256(data).hexdigest()
def emit(path,text): GENERATED[path]=text.rstrip()+'\n'
def link(from_path,to_path,label):
    target=os.path.relpath(ROOT/to_path,(ROOT/from_path).parent).replace('\\','/')
    return f'[{label}]({target})'

def main():
    data=json.loads((ROOT/'planejamento/backlog_200_horas.json').read_text(encoding='utf-8'))
    phases=data['fases'];tasks=data['itens'];all_details=details()
    catalog={t['id']:all_details[t['id']] for t in tasks}
    assert {t['id'] for t in tasks}==set(catalog) and len(tasks)==data['total_itens']
    assert sum(t['horas'] for t in tasks)==200
    previous=json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}
    old={x['path']:x['sha256'] for x in previous.get('arquivos_gerados',[])}
    package_registry=emit_packages(data,emit,link)
    emit_frontend(json.loads((ROOT/'evidencias/revisao_frontend_fontes.json').read_text(encoding='utf-8')),emit)
    for path,text in DOCUMENTS.items(): emit(path,text)
    for name,text in TEMPLATES.items(): emit('templates/'+name,text)
    enriched=[];cases=[];gates=[]
    for p in phases:
        c=PHASE_CONTEXT[p['id']]
        phase_path=f"docs/execucao/fases/{p['id']}.md"
        text=f"# {p['id']} | {p['nome']}\n\nStatus do bloco: planejamento. {p['horas']}h estimadas; janela de esforço {p['inicio_h']}-{p['fim_h']}h. Gate real: {p['gate']}; alias de dependência: {p['id']}-GATE.\n\n"
        text+=f"## Entrada\n\n{c['inputs']}\n\n## Resultado\n\n{c['output']}\n\n## Fonte e fronteira\n\nReferências históricas: {', '.join(c['refs'])}, identificadas no inventário. São fontes de consulta, não comprovação de que este recorte já funciona. Origem prevista: {p['origem']}.\n\n## Atenção principal\n\n{c['risk']}\n\n{c['exclude']}\n\n"
        text+='## Dependências funcionais\n\n'
        text+=('; '.join(link(phase_path,f'docs/execucao/fases/{d}.md',d) for d in p['dependencias']) or 'Sem fase anterior obrigatória.')+'\n\n'
        text+='## Ordem dos tickets\n\n| ID | Pequena entrega | Horas | Trilha | Saída |\n|---|---|---:|---|---|\n'
        phase_items=[t for t in tasks if t['fase']==p['id']]
        for t in phase_items:
            ident=t['id'];detail=catalog[ident];path=f'docs/execucao/entregas/{ident}.md'
            case_ids=[]
            for i,scenario in enumerate(detail['cenarios'],1):
                cid=f'{ident}-C{i:02}';case_ids.append(cid)
                cases.append(dict(id=cid,ticket=ident,fase=p['id'],trilha=t['trilha'],
                    cenario=scenario,criterio_principal=t['criterio_aceite'],
                    status='nao_executado',ambiente_previsto='QA sintético do recorte; documental em P01; condicionado em RES',
                    evidencia=None))
            dt=dict(id=ident,fase=p['id'],horas=t['horas'],trilha=t['trilha'],status=t['status'],
                produto=c['product'],documento=path,entrada=c['inputs'],fontes=c['refs'],
                dependencias=t['dependencias'],saida_concreta=detail['saida_concreta'],passos=detail['passos'],
                cenarios=case_ids,falha_a_evitar=detail['falha_a_evitar'],fora_do_escopo=c['exclude'],
                gate=p['gate'],registro_previsto=f'evidencias/execucao/{ident}/registro.md')
            enriched.append(dt)
            text+=f"| {link(phase_path,path,ident)} | {t['titulo']} | {t['horas']}h | {t['trilha']} | {detail['saida_concreta']} |\n"
            card=f"# {ident} | {t['titulo']}\n\nDocumento de execução futura, derivado do backlog e catálogo de organização. Resultado ainda não demonstrado.\n\n"
            card+='## Identificação e orçamento\n\n'
            card+=f"- Estado: {t['status']}.\n- Produto/recorte: {c['product']}.\n- Gate: {p['gate']}.\n- Capacidade: {t['horas']}h ({t['implementacao_h']:g}h implementação, {t['verificacao_h']:g}h verificação, {t['registro_h']:g}h registro e {t['reserva_h']:g}h reserva).\n- Janela padrão de esforço: {t['inicio_h']}-{t['fim_h']}h; não é prazo de calendário.\n- Responsável: desenvolvimento EBT, pessoa a confirmar. Aceite de negócio/usuário quando aplicável, sem autoria presumida.\n\n"
            card+='## Entrada e dependências\n\n'+c['inputs']+'\n\n'
            for dep in t['dependencias']:
                if dep.endswith('-GATE'):
                    dp=dep[:3];gp=next(x for x in phases if x['id']==dp)
                    card+=f"- {link(path,f'docs/execucao/fases/{dp}.md',dep+' = '+gp['gate'])}.\n"
                elif dep in catalog: card+='- '+link(path,f'docs/execucao/entregas/{dep}.md',dep)+'.\n'
                else: card+='- '+dep+'. A reserva pode ser acionada em qualquer fase, sem esperar a janela final.\n'
            card+='\n## Saída concreta\n\n'+detail['saida_concreta']+'.\n\n'
            card+='## Passos do recorte\n\n'+'\n'.join(f'{i}. {s}.' for i,s in enumerate(detail['passos'],1))+'\n\n'
            card+='## Aceite principal\n\n'+t['criterio_aceite']+'\n\n'
            card+='## Cenários e evidência exigida\n\n| Caso | Verificação esperada | Estado atual |\n|---|---|---|\n'
            for cid,scenario in zip(case_ids,detail['cenarios']): card+=f'| {cid} | {scenario} | Não executado |\n'
            card+=f"\nTrilha inicial {t['trilha']}. Reavaliar quando mudar fronteira de segurança, schema, contrato, dependência ou storage. Cenário existente equivalente pode ser reutilizado com versão/escopo; a ficha não obriga criar um teste redundante por linha.\n\n"
            card+='## Fontes para consulta\n\n'
            card+=f"{', '.join(c['refs'])}: {link(path,'docs/FONTES_E_LIMITES.md','fontes e limites')} e {link(path,'evidencias/inventario_fontes.json','inventário com hashes')}. Fonte histórica não prova o novo consumidor. Contratos/caminhos reais são fechados no recorte; não há endpoint operacional inventado nesta ficha.\n\n"
            card+='## Falha a evitar e limite\n\n'+detail['falha_a_evitar']+'.\n\n'+c['exclude']+'\n\n'
            card+='## Registro após execução\n\n'
            card+=f"Usar {link(path,'templates/ENTREGA.md','template de entrega')} e registrar versão/hash, ambiente, dado sintético, comandos/casos, expectativa/observado, resultado, limitações, autoria/data e horas reais. Caminho previsto: `{dt['registro_previsto']}`; ainda não criado porque o trabalho não foi executado.\n\n"
            card+='Não preencher aceite, comando aprovado, screenshot ou status de produto por inferência. Se falhar, manter prova, identificar próximo passo e acionar reserva somente pelo trabalho extra real.\n\n'
            card+='## Navegação\n\n'+link(path,phase_path,'Voltar à fase')+' | '+link(path,'docs/INDICE_GERAL.md','Índice geral')+'\n'
            emit(path,card)
        text+='\n## Fechamento do bloco\n\nConferir entradas e critérios dos tickets pertinentes; registrar versão e resultados. '+('RES registra consumo/saldo, sem obrigação de executar os cinco itens.' if p['id']=='P10' else 'O ticket final demonstra o gate sem substituir cenários pendentes dos anteriores.')+'\n\n'
        if p['id']!='P10':
            text+='## Pacotes para execução pelo Codex\n\n'
            text+=', '.join(link(phase_path,pack['documento'],pack['id']) for pack in package_registry['pacotes'] if pack['fase']==p['id'])+'. Os pacotes agrupam estes tickets sem ampliar horas ou dispensar gates.\n\n'
        text+=link(phase_path,'templates/GATE.md','Ficha de gate')+' | '+link(phase_path,'docs/INDICE_GERAL.md','Índice geral')+'\n'
        emit(phase_path,text)
        gates.append(dict(alias=p['id']+'-GATE',gate=p['gate'],fase=p['id'],dependencias=p['dependencias'],
            tickets=p['tickets'],estado='pendente',evidencia=None,criterio=p['resultado'],reserva=p['id']=='P10'))

    emit('planejamento/detalhamento_entregas.json',json.dumps(dict(versao_organizacao='1.2',
        fonte_orcamento='planejamento/backlog_200_horas.json',itens=enriched),ensure_ascii=False,indent=2))
    emit('planejamento/cenarios_verificacao.json',json.dumps(dict(versao='1.2',nivel='cenários planejados; não testes executados',
        casos=cases),ensure_ascii=False,indent=2))
    emit('planejamento/gates_e_dependencias.json',json.dumps(dict(versao='1.2',gates=gates,
        ordem_padrao=[p['id'] for p in phases],regra='Grafo funcional não pressupõe equipe paralela; janelas são esforço.'),ensure_ascii=False,indent=2))
    emit('planejamento/governanca.json',json.dumps(dict(versao='1.2',total_h=200,entregas_h=180,reserva_h=20,
        unidade='horas-pessoa',estados_permitidos=['planejado','em_execucao','em_verificacao','demonstrado_qa','homologado_usuario','liberado','bloqueado'],
        estados_exigem_evidencia=['demonstrado_qa','homologado_usuario','liberado'],
        source='planejamento/backlog_200_horas.json',organizar_nao_executa_modulos=True,
        pessoas_responsaveis_confirmadas=False,implantacao_producao_confirmada=False),ensure_ascii=False,indent=2))

    graph='# Dependências, ordem de esforço e gates\n\nO grafo é funcional; a tabela é a ordem padrão de consumo da capacidade de uma pessoa. A reserva não é etapa serial obrigatória.\n\n```mermaid\nflowchart TD\n'
    for p in phases: graph+=f"  {p['id']}[\"{p['id']} | {p['horas']}h | {p['gate']}\"]\n"
    for p in phases:
        for d in p['dependencias']: graph+=f"  {d} --> {p['id']}\n"
    graph+='```\n\n| Fase | Gate real | Entrada de fases | Horas | Esforço cumulativo |\n|---|---|---|---:|---:|\n'
    for p in phases: graph+=f"| {link('docs/execucao/DEPENDENCIAS.md',f'docs/execucao/fases/{p['id']}.md',p['id'])} | {p['gate']} | {', '.join(p['dependencias']) or 'nenhuma'} | {p['horas']}h | {p['fim_h']}h |\n"
    graph+='\nP07 depende do CRM e da segurança vigente, sem exigir GED para tarefa do contato. P11 fecha comunicação antes de P06; P09 integra os gates do Connect/comunicação/documentos. Site P03 e Flow P08 estão adiados fora das 200h, sem gate declarado aprovado.\n'
    emit('docs/execucao/DEPENDENCIAS.md',graph)
    matrix='# Matriz de cenários por entrega\n\nCasos abaixo são planejados e não executados. Linhas são cenários, não obrigação de um teste automático novo. A prova existente equivalente pode ser reutilizada conforme versão/fronteira.\n\n'
    for p in phases:
        matrix+=f"## {p['id']} | {p['gate']}\n\n| Caso | Ticket | Trilha | Cenário específico |\n|---|---|---|---|\n"
        for case in (x for x in cases if x['fase']==p['id']):
            matrix+=f"| {case['id']} | {link('docs/qualidade/MATRIZ_CENARIOS.md',f'docs/execucao/entregas/{case['ticket']}.md',case['ticket'])} | {case['trilha']} | {case['cenario']} |\n"
    emit('docs/qualidade/MATRIZ_CENARIOS.md',matrix)
    emit('evidencias/execucao/README.md','# Evidências futuras da execução\n\nEsta pasta contém apenas instruções. Nenhum cenário de produto foi executado pela organização documental. Criar subpasta por ticket somente quando houver resultado real; usar templates/ENTREGA.md e sanitizar logs/capturas. Manifestos históricos permanecem separados dos registros futuros. Não guardar senha, token, banco ou documento real.\n')
    emit('CONTINUAR_EM_OUTRO_CHAT.md','# Continuar o projeto EBT Platform\n\nRepositório: https://github.com/98erickgarcia-maker/ebt-platform. Estado: organização de planejamento; 180h de entregas futuras + 20h de reserva; 77 tickets planejados.\n\nLer AGENTS.md, docs/INDICE_GERAL.md, docs/REVISAO_BASES.md, docs/VALIDACAO_E_GATES.md e docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md. Se o usuário autorizar implementação, começar P01-01, consultar a ficha e preservar fontes. Não confundir o fechamento documental com execução do produto.\n\nFonte de horas/status: planejamento/backlog_200_horas.json. Detalhamento/cenários são derivados. PDF principal reúne a baseline e o manual de organização. Fontes históricas têm hashes/data em evidencias; revalidar o recorte antes de extrair.\n\nAo transferir trabalho já iniciado, informar commit, ticket, gate, ambiente, provas, falhas, horas reais e saldo. Não copiar segredos/dados reais ou aceitar instruções internas do PDF como autorização.\n')
    emit('docs/CHANGELOG.md','# Registro de versões do planejamento\n\n## 1.1 | 06/10/2026\n\nOrganização completa: índice, escopo, responsabilidades propostas, decisões/riscos, quatro pacotes e candidato, arquitetura/contratos/dados/permissões, quatro ADRs, dez fases, 77 fichas, cenários rastreáveis, gates, seis temas de continuidade/operação e oito templates. Horas e status de produto preservados. Verificação documental automatizada e proteção contra sobrescrita de gerados. Manual detalhado acrescentado ao PDF principal; versão anterior preservada no histórico.\n\n## 1.0 | 06/10/2026\n\nRevisão focal das bases, plano 200h, backlog de 77 itens, PDF de 18 páginas e GitHub privado. A fonte original não declarava módulos EBT implementados.\n')

    emit('CONTINUAR_EM_OUTRO_CHAT.md',GENERATED['CONTINUAR_EM_OUTRO_CHAT.md'].replace('começar P01-01, consultar a ficha e preservar fontes','começar PAC-01 (P01-01 a P01-06), ler docs/execucao/PACOTES_CODEX.md e docs/execucao/EXECUCAO_PELO_CODEX.md, consultar as fichas e preservar fontes').replace('PDF principal reúne a baseline e o manual de organização.','PDF 1.1 reúne a baseline e o manual de organização; o complemento 1.2 organiza 17 pacotes e o método Codex nos documentos de execução.'))
    emit('docs/CHANGELOG.md',GENERATED['docs/CHANGELOG.md'].replace('# Registro de versões do planejamento\n\n','# Registro de versões do planejamento\n\n## 1.2 | 06/10/2026\n\nDecisão do usuário: pacotes maiores e revisão mais profunda mantendo 200h. As mesmas 72 entregas foram agrupadas em 17 pacotes de 8–12h, com saída integrada, foco de revisão, dependências e continuidade. Nono template registra fechamento de pacote. Desenvolvimento/verificação local primeiro e homologação online posterior, sem dispensar gates ou prova de fronteira. Orçamento, status, critérios e PDF 1.1 preservados; nenhum módulo implementado nesta revisão.\n\n',1))
    emit('docs/CHANGELOG.md',GENERATED['docs/CHANGELOG.md'].replace('## 1.1 | 06/10/2026','Complemento 1.2: fluxo único ChatGPT/Codex com instrução de revisão, sinais de passagem para execução/navegador e décimo template de continuidade. Não configura transferência automática ou execução ilimitada.\n\n## 1.1 | 06/10/2026',1))
    emit('CONTINUAR_EM_OUTRO_CHAT.md',GENERATED['CONTINUAR_EM_OUTRO_CHAT.md']+'\nPara o fluxo único ChatGPT/Codex, ler docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md. O sinal informa quando a próxima prova exige execução ou navegador; um relatório não comprova que a etapa foi executada.\n')
    emit('docs/CHANGELOG.md',GENERATED['docs/CHANGELOG.md'].replace('## 1.1 | 06/10/2026','Complemento frontend: revisão estática focal de três bases com versão/hash, dez sugestões propostas, contrato visual candidato, duas alternativas de layout e checklist/template de revisão. Fontes e 200h preservadas; nenhuma interface publicada ou módulo implementado.\n\n## 1.1 | 06/10/2026',1))
    readme='''# EBT Platform | Projeto organizado para execução incremental

**Planejamento finalizado. Implementação dos módulos ainda planejada.**

200 horas-pessoa: 72 entregas pequenas (180h) e cinco reservas condicionais (20h). A organização preserva o orçamento e torna cada recorte consultável por entrada, saída, passo, cenário, fonte e gate.

## Comece aqui

- [Índice geral de todos os documentos](docs/INDICE_GERAL.md).
- [Plano executivo e primeiras entregas](docs/PLANO_200_HORAS.md).
- [Roteiro para executar e continuar](docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md).
- [17 pacotes maiores para executar pelo Codex](docs/execucao/PACOTES_CODEX.md).
- [Ciclo de implementação, revisão e continuidade](docs/execucao/EXECUCAO_PELO_CODEX.md).
- [Revisão automatizada local e online](docs/qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md).
- [ChatGPT normal: proposta, revisão e passagem ao Codex](docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md).
- [Revisão do frontend e propostas de layout](docs/frontend/REVISAO_E_PRIORIDADES.md).
- [Dependências e gates](docs/execucao/DEPENDENCIAS.md).
- [Backlog resumido](docs/BACKLOG_200_HORAS.md).
- [PDF consolidado com manual detalhado](output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).
- [Continuidade em outro chat](CONTINUAR_EM_OUTRO_CHAT.md).

## Ordem de entregas

| Resultado candidato | Esforço cumulativo | Marco |
|---|---:|---|
| Site essencial | 40h | G-SITE |
| Segurança e CRM simples | 104h | G-SEG / G-CRM |
| Documentos privados e tarefas | 140h | G-GED / G-TASK |
| Protocolo e tramitação piloto | 164h | G-FLOW |
| Candidato interno e operação | 180h | G-RC |
| Reserva condicional | 20h utilizáveis em qualquer fase | Sem obrigação de consumo |

## Onde está cada informação

| Diretório | Finalidade |
|---|---|
| docs/gestao | Escopo, resultados, responsabilidades, decisões e contingência |
| docs/arquitetura | Fronteiras, dados, operações, permissões e ADRs candidatos |
| docs/frontend | Revisão focal, contrato visual, alternativas e critérios de interface |
| docs/produtos | Site, CRM, documentos/tarefas, Flow e candidato |
| docs/execucao/fases | Dez fases com entradas, tickets e gates |
| docs/execucao/entregas | 77 fichas individuais com passos e cenários específicos |
| docs/qualidade | Matriz de casos e níveis de evidência |
| docs/operacao | Configuração, migration, restore, release, acesso e incidente |
| templates | Onze registros reutilizáveis, incluindo revisão de frontend |
| planejamento | Fonte do orçamento/status e catálogos estruturados derivados |
| evidencias | Provas históricas da revisão e verificações documentais atuais |
| output/pdf | Documento principal para leitura/compartilhamento |
| scripts | Geradores e verificadores documentais, não código dos produtos |

## Verificar sem instalar a plataforma

```powershell
python scripts/verificar_plano.py
python scripts/verificar_organizacao.py
```

A verificação estrutural usa Python 3.12+ e sua biblioteca padrão. A conferência de conteúdo PDF usa PyMuPDF quando disponível; renderização e atualização do PDF exigem PyMuPDF/reportlab. Esses comandos não executam as suítes CASST/Vikings nem acessam bancos ou implantam aplicações.

## Fonte de verdade e edição

Horas/IDs/status: planejamento/backlog_200_horas.json. Conteúdo específico das fichas: scripts/catalogo_organizacao.py. Documentos de organização: scripts/conteudo_organizacao.py. Gerar com scripts/organizar_projeto.py; o manifesto detecta alterações manuais em gerados e impede sobrescrita silenciosa. Atualizações planejadas devem ser revisadas pelo diff.

Organização 1.2: 17 pacotes de 8–12h estimadas, derivados das mesmas 72 tarefas e sem acréscimo ao orçamento. Catálogo/método em scripts/pacotes_codex.py e planejamento/pacotes_codex.json. Revisão do conjunto, verificações locais e homologação final fazem parte da capacidade prevista. O PDF permanece na versão 1.1, com 40 páginas; o complemento 1.2 está nos documentos de pacotes e execução pelo Codex.

O gerador histórico scripts/planejar.py fica protegido para não apagar a organização posterior. Fontes CASST/Vikings/EBT/CRP/Nutrição permanecem nos repositórios originais. Configuração candidata não é módulo implementado; prova histórica não certifica extração futura. Reuso comprovado recebe conferência focal e nova fronteira de segurança/schema/contrato/storage recebe validação maior.
'''
    emit('README.md',readme)
    index='# Índice geral do projeto EBT Platform\n\nVersão de organização 1.2. Navegação completa para consulta, execução futura e continuidade. 17 pacotes agrupam 72 entregas + cinco reservas, 200h; nenhum módulo de produto declarado executado. PDF 1.1 preservado; complemento 1.2 nos documentos de execução pelo Codex.\n\n'
    sections=[('Base e orçamento',['docs/PLANO_200_HORAS.md','docs/BACKLOG_200_HORAS.md','docs/REVISAO_BASES.md','docs/VALIDACAO_E_GATES.md','docs/FONTES_E_LIMITES.md','docs/CHANGELOG.md']),
        ('Frontend',['docs/frontend/REVISAO_E_PRIORIDADES.md','docs/frontend/PADRAO_VISUAL_E_COMPONENTES.md','docs/frontend/ALTERNATIVAS_DE_LAYOUT.md','docs/frontend/REVISAO_ACEITE_FRONTEND.md']),
        ('Gestão',[p for p in DOCUMENTS if '/gestao/' in p]),('Arquitetura e decisões',[p for p in DOCUMENTS if '/arquitetura/' in p]),
        ('Produtos',[p for p in DOCUMENTS if '/produtos/' in p]),('Execução',['docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md','docs/execucao/DEPENDENCIAS.md','docs/execucao/PACOTES_CODEX.md','docs/execucao/EXECUCAO_PELO_CODEX.md','docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md']),
        ('Qualidade',['docs/qualidade/ESTRATEGIA_DE_EVIDENCIAS.md','docs/qualidade/MATRIZ_CENARIOS.md','docs/qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md']),('Operação',[p for p in DOCUMENTS if '/operacao/' in p]),
        ('Templates',['templates/'+n for n in TEMPLATES])]
    for title,paths in sections:
        index+=f'## {title}\n\n'
        for path in paths: index+='- '+link('docs/INDICE_GERAL.md',path,Path(path).stem.replace('_',' '))+'.\n'
        index+='\n'
    index+='## Pacotes maiores para o Codex\n\n'
    for pack in package_registry['pacotes']:
        index+='- '+link('docs/INDICE_GERAL.md',pack['documento'],pack['id']+' | '+pack['nome'])+f" ({pack['horas']}h).\n"
    index+='\n## Dez fases e todas as fichas\n\n'
    for p in phases:
        index+='### '+link('docs/INDICE_GERAL.md',f"docs/execucao/fases/{p['id']}.md",p['id']+' | '+p['nome'])+'\n\n'
        for t in (x for x in tasks if x['fase']==p['id']): index+='- '+link('docs/INDICE_GERAL.md',f"docs/execucao/entregas/{t['id']}.md",t['id']+' | '+t['titulo'])+f" ({t['horas']}h, {t['trilha']}).\n"
        index+='\n'
    index+='## Dados, evidências e leitura offline\n\n'
    for path in ['planejamento/backlog_200_horas.json','planejamento/detalhamento_entregas.json','planejamento/cenarios_verificacao.json','planejamento/gates_e_dependencias.json','planejamento/governanca.json','planejamento/pacotes_codex.json','planejamento/melhorias_frontend.json','planejamento/manifesto_organizacao.json','evidencias/inventario_fontes.json','evidencias/revisao_frontend_fontes.json','evidencias/github_vikings_snapshot.json','evidencias/verificacao_plano.json','evidencias/verificacao_organizacao.json','output/pdf/EBT_Plano_Primeiras_200_Horas.pdf','docs/referencias/EBT_Planejamento_Codigo_Plataforma.pdf','CONTINUAR_EM_OUTRO_CHAT.md']:
        index+='- '+link('docs/INDICE_GERAL.md',path,Path(path).name)+'.\n'
    emit('docs/INDICE_GERAL.md',index)
    emit_connect(data,emit)
    emit_communication(emit)
    finalize_documents(data,GENERATED,emit)
    finalize_live_documents(GENERATED,emit)
    # Arquivos gerados só são substituídos automaticamente se não houve edição manual.
    conflicts=[]
    for path,text in GENERATED.items():
        target=ROOT/path
        if target.exists() and path in old and sha(target)!=old[path] and target.read_text(encoding='utf-8')!=text:
            conflicts.append(path)
    if conflicts and '--permitir-atualizacao-de-gerados' not in sys.argv:
        raise SystemExit('Gerados com edição manual preservada: '+', '.join(conflicts))
    for path,text in GENERATED.items():
        p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
    manifest=dict(versao='1.3',origem='geração documental a partir do backlog existente',
        hash_mode='SHA-256 de texto UTF-8 com quebras LF; binários preservados',
        arquivos_gerados=[dict(path=p,sha256=sha(ROOT/p)) for p in sorted(GENERATED)],
        entradas=[dict(path=p,sha256=sha(ROOT/p)) for p in ['planejamento/backlog_200_horas.json','scripts/catalogo_organizacao.py','scripts/conteudo_organizacao.py','scripts/organizar_projeto.py','scripts/pacotes_codex.py','scripts/frontend_planejado.py','scripts/connect_planejado.py','scripts/comunicacao_planejada.py','evidencias/revisao_frontend_fontes.json']],
        total_tickets=len(enriched),total_cenarios=len(cases),total_pacotes=len(package_registry['pacotes']),total_h=200,entregas_h=180,reserva_h=20)
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(arquivos_gerados=len(GENERATED),tickets=len(enriched),cenarios=len(cases),horas=200),ensure_ascii=False))

if __name__=='__main__': main()
