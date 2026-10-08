"""Verifica organização, rastreabilidade e consistência; não executa aplicações."""
from pathlib import Path
import json,re,hashlib,sys
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def digest(path):
    p=ROOT/path
    data=p.read_bytes() if p.suffix=='.pdf' else p.read_text(encoding='utf-8').encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def main():
    errors=[]
    def check(ok,message):
        if not ok: errors.append(message)
    baseline=load('planejamento/backlog_200_horas.json')
    details=load('planejamento/detalhamento_entregas.json')['itens']
    cases=load('planejamento/cenarios_verificacao.json')['casos']
    gates=load('planejamento/gates_e_dependencias.json')['gates']
    manifest=load('planejamento/manifesto_organizacao.json')
    governance=load('planejamento/governanca.json')
    package_registry=load('planejamento/pacotes_codex.json')
    packages=package_registry['pacotes']
    sources={r['id'] for r in load('evidencias/inventario_fontes.json')['referencias']}
    items={t['id']:t for t in baseline['itens']}
    phases={p['id']:p for p in baseline['fases']}
    case_ids=[c['id'] for c in cases]
    check(len(items)==baseline['total_itens'] and len(details)==len(items),'Quantidade de itens/fichas diverge da baseline')
    check({d['id'] for d in details}==set(items),'IDs detalhados diferem da baseline')
    check(len(set(case_ids))==len(case_ids),'Caso duplicado')
    check(len(gates)==len(phases) and len({g['alias'] for g in gates})==len(phases),'Gates/aliases únicos devem cobrir as fases')
    check(sum(t['horas'] for t in items.values())==200,'Orçamento alterado')
    check(sum(t['horas'] for t in items.values() if t['trilha']!='RES')==180,'Entregas alteradas')
    check(sum(t['horas'] for t in items.values() if t['trilha']=='RES')==20,'Reserva alterada')
    check(governance['total_h']==200 and governance['entregas_h']==180 and governance['reserva_h']==20,'Governança diverge das horas')
    check(package_registry['total_h']==200 and package_registry['entregas_h']==180 and package_registry['reserva_h']==20,'Pacotes alteram orçamento')
    pack_ids={p['id'] for p in packages}
    flat=[tid for p in packages for tid in p['tickets']]
    normal={tid for tid,t in items.items() if t['trilha']!='RES'}
    check(len(packages)==len(pack_ids)==17,'17 pacotes únicos devem existir')
    check(len(flat)==len(set(flat))==baseline['total_entregas'] and set(flat)==normal,'Pacotes devem cobrir cada entrega ativa uma vez')
    check(package_registry['ordem_execucao']==[p['id'] for p in packages],'Ordem explícita de pacotes diverge')
    check([p['inicio_h'] for p in packages]==sorted(p['inicio_h'] for p in packages),'Pacotes fora da ordem de esforço')
    check(set(package_registry['reservas'])==set(items)-normal,'Reservas foram removidas ou absorvidas por pacote')
    check(sum(p['horas'] for p in packages)==180,'Soma dos pacotes difere de 180h')
    connect=load('planejamento/entrega_connect.json')
    check(connect['horas_incluidas']==140 and connect['horas_adicionais']==0,'Contrato Connect altera esforço')
    connect_rows=[items[tid] for tid in connect['tickets'] if tid in items]
    check(len(connect_rows)==54 and sum(t['horas'] for t in connect_rows)==140,'Tickets Connect não totalizam 140h')
    check(connect['estado']=='planejado' and connect['evidencia_execucao'] is None,'Contrato inventa execução')
    check(phases['P07']['dependencias']==['P05'],'GED bloqueia tarefa comercial do contato')
    check(phases['P07']['fim_h']==104 and phases['P11']['fim_h']==140 and phases['P06']['fim_h']==164,'Marcos da revisão divergem')
    check('P03' not in phases and 'P08' not in phases,'Site/Flow continuam alocados no ciclo')
    postponed=load('planejamento/backlog_apos_200_horas.json')
    check(postponed['horas_alocadas_neste_ciclo']==0 and len(postponed['itens'])==14,'Recortes adiados foram absorvidos/excluídos')
    check({t['id'] for t in postponed['itens']}=={t['id'] for t in baseline['adiados']['itens']},'IDs adiados divergentes')
    check(all(t['trilha']=='N' for t in items.values() if t['fase']=='P11'),'Comunicação nova usa verificação reduzida')
    specification=load('planejamento/connect_api.openapi.json')
    check(specification['openapi']=='3.1.0' and specification['x-estado']=='planejado','Contrato API inválido ou declarado executado')
    schemas=specification['components']['schemas']
    def inspect_refs(value):
        if isinstance(value,dict):
            if '$ref' in value:
                reference=value['$ref']
                check(reference.startswith('#/components/schemas/') and reference.rsplit('/',1)[-1] in schemas,'Referência OpenAPI não resolvida: '+reference)
            for child in value.values():inspect_refs(child)
        elif isinstance(value,list):
            for child in value:inspect_refs(child)
    inspect_refs(specification)
    reply=specification['paths']['/api/connect/v1/conversations/{conversationId}/messages']['post']
    check({'Idempotency-Key','If-Match'}<={p['name'] for p in reply['parameters'] if p['required']},'Resposta perdeu repetição/concorrência')
    check('202' in reply['responses'] and '409' in reply['responses'],'API omite fila ou conflito')
    check(not {'tenantId','recipient','to'}&set(schemas['ReplyRequest']['properties']),'Cliente escolhe tenant/destinatário arbitrário')
    check(schemas['ReplyRequest']['additionalProperties'] is False,'DTO de resposta admite campos arbitrários')
    owner={tid:p['id'] for p in packages for tid in p['tickets']}
    for p in packages:
        ids=p['tickets']
        check(all(tid in items for tid in ids),f"Ticket ausente em pacote: {p['id']}")
        if not all(tid in items for tid in ids): continue
        phase=phases[p['fase']]
        check(all(items[tid]['fase']==p['fase'] and items[tid]['trilha']!='RES' for tid in ids),f"Pacote mistura fase/reserva: {p['id']}")
        check(8<=p['horas']<=12 and p['horas']==sum(items[tid]['horas'] for tid in ids),f"Horas incoerentes: {p['id']}")
        for field in ['implementacao_h','verificacao_h','registro_h']:
            check(abs(p[field]-sum(items[tid][field] for tid in ids))<1e-8,f"Composição altera horas: {p['id']}/{field}")
        external={dep for tid in ids for dep in items[tid]['dependencias'] if dep not in ids}
        check(set(p['dependencias_tickets_gates'])==external,f"Pacote perdeu dependência: {p['id']}")
        expected=set()
        for dep in external:
            if dep in owner: expected.add(owner[dep])
            elif dep.endswith('-GATE') and dep[:3] in phases:
                final=phases[dep[:3]]['tickets'][-1]
                if final in owner: expected.add(owner[final])
        expected.discard(p['id'])
        check(set(p['dependencias_pacotes'])==expected,f"Dependência de pacote incoerente: {p['id']}")
        check(p['gate_fase']==phase['gate'] and p['fecha_gate_fase']==(phase['tickets'][-1] in ids),f"Gate antecipado/divergente: {p['id']}")
        check(p['estado']=='planejado' and p['evidencia'] is None,f"Pacote fabrica execução: {p['id']}")
        check((ROOT/p['documento']).is_file(),f"Ficha de pacote ausente: {p['id']}")
    for d in details:
        t=items[d['id']]
        check(d['horas']==t['horas'] and d['trilha']==t['trilha'] and d['status']==t['status'],f"Metadados divergentes: {d['id']}")
        check(d['dependencias']==t['dependencias'],f"Dependência divergente: {d['id']}")
        check(set(d['fontes'])<=sources,f"Fonte não catalogada: {d['id']}")
        check(len(d['passos'])>=3 and len(d['cenarios'])>=3,f"Detalhamento insuficiente: {d['id']}")
        check(bool(d['saida_concreta']) and bool(d['falha_a_evitar']),f"Saída/falha ausente: {d['id']}")
        card=ROOT/d['documento']
        check(card.is_file(),f"Ficha ausente: {d['id']}")
        if card.is_file():
            text=card.read_text(encoding='utf-8')
            check(t['criterio_aceite'] in text,f"Aceite não preservado: {d['id']}")
            check(all(cid in text for cid in d['cenarios']),f"Casos não ligados à ficha: {d['id']}")
        relevant=[c for c in cases if c['ticket']==d['id']]
        check({c['id'] for c in relevant}==set(d['cenarios']),f"Casos divergentes: {d['id']}")
    for c in cases:
        check(c['ticket'] in items,f"Caso sem ticket: {c['id']}")
        if c['ticket'] in items:
            t=items[c['ticket']]
            check(c['fase']==t['fase'] and c['trilha']==t['trilha'],f"Caso fora da fase/trilha: {c['id']}")
        check(c['status']=='nao_executado' and c['evidencia'] is None,f"Catálogo planejado não deve fabricar prova: {c['id']}")
    visited=set();active=set()
    def visit(code):
        if code in active:
            errors.append('Ciclo de fases: '+code);return
        if code in visited:return
        active.add(code)
        for dep in phases[code]['dependencias']:
            if dep not in phases: errors.append('Fase ausente: '+dep)
            else: visit(dep)
        active.remove(code);visited.add(code)
    for code in phases: visit(code)
    for g in gates:
        p=phases[g['fase']]
        check(g['gate']==p['gate'] and g['tickets']==p['tickets'] and g['dependencias']==p['dependencias'],f"Gate diverge: {g['alias']}")
    links=0;markdown=[]
    for file in ROOT.rglob('*.md'):
        rel=file.relative_to(ROOT)
        if any(part in {'.git','tmp','__pycache__','node_modules','bin','obj','playwright-report'} for part in rel.parts):continue
        markdown.append(file);text=file.read_text(encoding='utf-8')
        check(text.count('```')%2==0,f"Bloco aberto: {rel}")
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith(('#','mailto:','tel:')):continue
            path=target.split('#')[0];links+=1
            resolved=(file.parent/path).resolve()
            if resolved==ROOT/'evidencias/verificacao_organizacao.json' and '--no-write' not in sys.argv:
                continue # O relatório deste comando é gravado após conferir o restante.
            check(resolved.exists(),f"Link quebrado: {rel} -> {path}")
    index=(ROOT/'docs/INDICE_GERAL.md').read_text(encoding='utf-8')
    for d in details: check(d['id'] in index,f"Ficha não indexada: {d['id']}")
    for p in packages: check(p['id'] in index,f"Pacote não indexado: {p['id']}")
    generated_paths=[x['path'] for x in manifest['arquivos_gerados']]
    check(len(set(generated_paths))==len(generated_paths),'Manifesto repete arquivo')
    for entry in manifest['arquivos_gerados']+manifest['entradas']:
        path=entry['path'];p=ROOT/path
        check(p.is_file(),f"Arquivo do manifesto ausente: {path}")
        if p.is_file():check(digest(path)==entry['sha256'],f"Gerado/fonte mudou sem reconciliação: {path}")
    check(manifest['total_tickets']==len(items) and manifest['total_cenarios']==len(cases),'Totais do manifesto divergentes')
    workflow=(ROOT/'.github/workflows/validar-planejamento.yml').read_text(encoding='utf-8')
    check('verificar_organizacao.py --no-write' in workflow,'CI documental ausente')
    check('contents: read' in workflow and 'deploy' not in workflow.lower(),'CI amplia permissão ou implanta produto')
    report=dict(passed=not errors,errors=errors,versao_organizacao=manifest['versao'],
        total_h=200,entregas_h=180,reserva_h=20,total_tickets=len(items),
        total_cenarios=len(cases),casos_nao_executados=len(cases),total_fases=len(phases),
        total_gates=len(gates),fichas_individuais=len(details),total_pacotes=len(packages),
        templates=len(list((ROOT/'templates').glob('*.md'))),
        markdown_files=len(markdown),local_links_checked=links,
        generated_files=len(generated_paths),hashes_checked=len(manifest['arquivos_gerados'])+len(manifest['entradas']),
        product_states=dict(Counter(t['status'] for t in items.values())),
        verification_scope='documentos, orçamento, dependências, fichas, casos e hashes; não verifica funcionamento das aplicações')
    if '--no-write' not in sys.argv:
        (ROOT/'evidencias/verificacao_organizacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__':main()
