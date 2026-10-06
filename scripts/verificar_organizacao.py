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
    sources={r['id'] for r in load('evidencias/inventario_fontes.json')['referencias']}
    items={t['id']:t for t in baseline['itens']}
    phases={p['id']:p for p in baseline['fases']}
    case_ids=[c['id'] for c in cases]
    check(len(items)==77 and len(details)==77,'77 itens/fichas devem existir')
    check({d['id'] for d in details}==set(items),'IDs detalhados diferem da baseline')
    check(len(set(case_ids))==len(case_ids),'Caso duplicado')
    check(len(gates)==10 and len({g['alias'] for g in gates})==10,'Dez gates/aliases únicos devem existir')
    check(sum(t['horas'] for t in items.values())==200,'Orçamento alterado')
    check(sum(t['horas'] for t in items.values() if t['trilha']!='RES')==180,'Entregas alteradas')
    check(sum(t['horas'] for t in items.values() if t['trilha']=='RES')==20,'Reserva alterada')
    check(governance['total_h']==200 and governance['entregas_h']==180 and governance['reserva_h']==20,'Governança diverge das horas')
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
        if any(part in {'.git','tmp','__pycache__'} for part in rel.parts):continue
        markdown.append(file);text=file.read_text(encoding='utf-8')
        check(text.count('```')%2==0,f"Bloco aberto: {rel}")
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            path=target.split('#')[0];links+=1
            resolved=(file.parent/path).resolve()
            if resolved==ROOT/'evidencias/verificacao_organizacao.json' and '--no-write' not in sys.argv:
                continue # O relatório deste comando é gravado após conferir o restante.
            check(resolved.exists(),f"Link quebrado: {rel} -> {path}")
    index=(ROOT/'docs/INDICE_GERAL.md').read_text(encoding='utf-8')
    for d in details: check(d['id'] in index,f"Ficha não indexada: {d['id']}")
    generated_paths=[x['path'] for x in manifest['arquivos_gerados']]
    check(len(set(generated_paths))==len(generated_paths),'Manifesto repete arquivo')
    for entry in manifest['arquivos_gerados']+manifest['entradas']:
        path=entry['path'];p=ROOT/path
        check(p.is_file(),f"Arquivo do manifesto ausente: {path}")
        if p.is_file():check(digest(path)==entry['sha256'],f"Gerado/fonte mudou sem reconciliação: {path}")
    check(manifest['total_tickets']==77 and manifest['total_cenarios']==len(cases),'Totais do manifesto divergentes')
    workflow=(ROOT/'.github/workflows/validar-planejamento.yml').read_text(encoding='utf-8')
    check('verificar_organizacao.py --no-write' in workflow,'CI documental ausente')
    check('contents: read' in workflow and 'deploy' not in workflow.lower(),'CI amplia permissão ou implanta produto')
    report=dict(passed=not errors,errors=errors,versao_organizacao='1.1',
        total_h=200,entregas_h=180,reserva_h=20,total_tickets=77,
        total_cenarios=len(cases),casos_nao_executados=len(cases),total_fases=len(phases),
        total_gates=len(gates),fichas_individuais=len(details),templates=8,
        markdown_files=len(markdown),local_links_checked=links,
        generated_files=len(generated_paths),hashes_checked=len(manifest['arquivos_gerados'])+len(manifest['entradas']),
        product_states=dict(Counter(t['status'] for t in items.values())),
        verification_scope='documentos, orçamento, dependências, fichas, casos e hashes; não verifica funcionamento das aplicações')
    if '--no-write' not in sys.argv:
        (ROOT/'evidencias/verificacao_organizacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__':main()
