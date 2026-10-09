"""Reconfere metadados da baseline; não escreve nas fontes nem testa aplicações."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
SOURCE = Path(r'C:\Users\Ivair Silva\Documents\Codex\2026-08-18\CRM_CASST_WEB\.worktrees\crm-casst-foundation')
manifest = json.loads((OUT / 'baseline/manifesto-fonte.json').read_text(encoding='utf-8'))
errors = []
for row in manifest['files']:
    target = (SOURCE / row['path']).resolve()
    if not target.is_relative_to(SOURCE.resolve()) or not target.is_file():
        errors.append({'path': row['path'], 'reason': 'ausente ou fora da fonte'})
    elif hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
        errors.append({'path': row['path'], 'reason': 'hash divergiu'})
head = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
if head != manifest['head']:
    errors.append({'reason': 'HEAD divergiu'})
if not manifest['second_hash_pass'] or not manifest['source_status_unchanged']:
    errors.append({'reason': 'captura original não estável'})
report = dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              passed=not errors, hashes_checked=len(manifest['files']), head=head,
              errors=errors, scope='metadados atuais da fonte; não é backup, teste funcional ou G0 aprovado')
(OUT / 'verificacao_hashes.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if not errors else 1)
