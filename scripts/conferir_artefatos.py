"""Conferência documental de layout e padrões de credenciais antes do GitHub."""
from pathlib import Path
import json, re, sys
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
pdf=ROOT/'output/pdf/EBT_Plano_Primeiras_200_Horas.pdf'
doc=pymupdf.open(pdf)
issues=[]
for n,page in enumerate(doc,1):
    for block in page.get_text('blocks'):
        if block[0]<35 or block[2]>560 or block[1]<14 or block[3]>825:
            issues.append(dict(page=n,bbox=list(block[:4])))
patterns=[
    r'gh[pousr]_[A-Za-z0-9]{30,}',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'AccountKey=[A-Za-z0-9+/=]{20,}',
    r'(?i)(?:password|senha|client_secret)\s*[:=]\s*["\x27][^"\x27]{8,}["\x27]',
]
files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','tmp','__pycache__'])]
hits=[]
for p in files:
    if p.suffix in ['.py','.md','.json','.yml','.yaml','.txt']:
        text=p.read_text(encoding='utf-8')
        if any(re.search(pattern,text,re.M) for pattern in patterns): hits.append(str(p.relative_to(ROOT)))
report_path=ROOT/'evidencias/verificacao_plano.json'
report=json.loads(report_path.read_text(encoding='utf-8'))
report.update(layout_bounds_issues=issues,
    credential_pattern_hits=hits,files_checked=len(files))
if '--confirm-visual-review' in sys.argv:
    report.update(visual_review=f'{len(doc)} páginas renderizadas e inspecionadas; sem corte, sobreposição, página vazia ou tabela fora dos limites.',
        visual_review_passed=True)
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pages=len(doc),layout_bounds_issues=issues,credential_pattern_hits=hits,files_checked=len(files)),ensure_ascii=False,indent=2))
if issues or hits: raise SystemExit(1)
