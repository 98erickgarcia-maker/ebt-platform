"""Confere orçamento, dependências, links e integridade do plano, sem fontes locais."""
from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]

def main():
    data=json.loads((ROOT/'planejamento/backlog_200_horas.json').read_text(encoding='utf-8'))
    items=data['itens']; phases=data['fases']; ids=[x['id'] for x in items]
    permitted={'planejado','em_execucao','em_verificacao','demonstrado_qa','homologado_usuario','liberado','bloqueado'}
    errors=[]
    def check(ok,message):
        if not ok: errors.append(message)
    check(len(ids)==77 and len(set(ids))==77,'Quantidade/IDs dos itens incorretos')
    check(sum(x['horas'] for x in items)==200,'Orçamento não totaliza 200h')
    check(sum(x['horas'] for x in items if x['trilha']!='RES')==180,'Entregas não totalizam 180h')
    check(sum(x['reserva_h'] for x in items)==20,'Reserva não totaliza 20h')
    check(len([x for x in items if x['trilha']=='RES'])==5,'Reservas condicionais incorretas')
    gates={p['id']+'-GATE':p for p in phases}
    seen=set();elapsed=0
    for t in items:
        check(1<=t['horas']<=4,f"Timebox fora do limite: {t['id']}")
        check(t['status'] in permitted,f"Estado inválido: {t['id']}")
        if t['status'] in {'demonstrado_qa','homologado_usuario','liberado'}:
            proof=t.get('evidencia_execucao')
            target=(ROOT/proof).resolve() if proof else None
            check(bool(target) and target.is_relative_to(ROOT/'evidencias/execucao') and target.is_file(),f"Estado exige prova de execução local sanitizada: {t['id']}")
        if t['status']=='bloqueado': check(bool(t.get('motivo_bloqueio')),f"Bloqueio sem causa: {t['id']}")
        check(t['inicio_h']==elapsed and t['fim_h']==elapsed+t['horas'],f"Janela inconsistente: {t['id']}")
        check(sum(t[x] for x in ['implementacao_h','verificacao_h','registro_h','reserva_h'])==t['horas'],f"Composição inválida: {t['id']}")
        check(bool(t['criterio_aceite']) and bool(t['evidencia_esperada']),f"Aceite/evidência ausente: {t['id']}")
        if t['trilha']!='RES':
            for dep in t['dependencias']:
                if dep.endswith('-GATE'):
                    check(dep in gates and gates[dep]['fim_h']<=t['inicio_h'],f"Gate fora da ordem: {t['id']} -> {dep}")
                else: check(dep in seen,f"Dependência ausente/futura: {t['id']} -> {dep}")
        seen.add(t['id']);elapsed=t['fim_h']
    for p in phases:
        rows=[x for x in items if x['fase']==p['id']]
        check(sum(x['horas'] for x in rows)==p['horas'],f"Horas divergentes: {p['id']}")
        check([x['id'] for x in rows]==p['tickets'],f"Itens divergentes: {p['id']}")
    broken=[];links=0
    for f in [ROOT/'README.md',*(ROOT/'docs').glob('*.md')]:
        text=f.read_text(encoding='utf-8')
        check(text.count('```')%2==0,f"Bloco de código aberto: {f.name}")
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'): continue
            target=target.split('#')[0];links+=1
            if not (f.parent/target).exists(): broken.append(f'{f.relative_to(ROOT)} -> {target}')
    check(not broken,'Links locais quebrados: '+str(broken))
    backlog=(ROOT/'docs/BACKLOG_200_HORAS.md').read_text(encoding='utf-8')
    for ident in ids: check(backlog.count('### '+ident+' |')==1,f"Ticket ausente/duplicado no Markdown: {ident}")
    pdf=ROOT/'output/pdf/EBT_Plano_Primeiras_200_Horas.pdf'
    check(pdf.exists() and pdf.stat().st_size>10000,'PDF não foi gerado')
    try:
        import pymupdf
        doc=pymupdf.open(pdf);text='\n'.join(p.get_text() for p in doc)
        for ident in ids: check(ident in text,f"Ticket ausente no PDF: {ident}")
        check(all(p.get_text().strip() for p in doc),'PDF tem página vazia')
        page_count=len(doc)
    except ImportError: page_count=None
    report=dict(passed=not errors,errors=errors,total_h=200,entregas_h=180,reserva_h=20,
        total_itens=len(ids),entregas=72,reservas=5,local_links=links,pdf_pages=page_count,
        pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        verification_scope='integridade documental, orçamento, dependências, links e conteúdo PDF; não testa aplicações',
        visual_review='Conferir separadamente as páginas renderizadas antes de entregar o PDF.')
    old_report=ROOT/'evidencias/verificacao_plano.json'
    if old_report.exists():
        previous=json.loads(old_report.read_text(encoding='utf-8'))
        if previous.get('pdf_sha256')==report['pdf_sha256']:
            for key in ('visual_review','visual_review_passed','layout_bounds_issues','credential_pattern_hits','files_checked'):
                if key in previous: report[key]=previous[key]
    (ROOT/'evidencias/verificacao_plano.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
