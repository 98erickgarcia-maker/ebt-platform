"""Snapshot somente de codigo/configuracao publica; nunca copia fontes ou dados."""
import hashlib, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'evidencias/inventario_fontes.json').read_text(encoding='utf-8'))
excluded = {'node_modules', '.git', 'bin', 'obj', 'output', 'outputs', 'qa', 'wwwroot', 'publish', '.venv'}
allowed = {'.cs', '.csproj', '.tsx', '.ts', '.css', '.html', '.sql', '.py', '.ps1', '.yaml', '.yml'}
def git(path, *args):
    p = subprocess.run(['git', '-C', str(path), *args], capture_output=True, text=True, encoding='utf-8')
    return p.stdout.strip() if p.returncode == 0 else None
projects = []
for item in catalog['projetos']:
    path = Path(item['path'])
    files = []
    if path.is_dir():
        for f in path.rglob('*'):
            relative = f.relative_to(path)
            if any(p in excluded or p.startswith('.') for p in relative.parts):
                continue
            if f.is_file() and (f.suffix.lower() in allowed or f.name in {'package.json', 'AGENTS.md', 'LICENSE'}):
                # No private settings, exports, databases, env or content JSON.
                files.append({'path': relative.as_posix(), 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
    projects.append({'nome': item['nome'], 'path': str(path), 'head': git(path, 'rev-parse', 'HEAD'),
                     'branch': git(path, 'branch', '--show-current'), 'status': git(path, 'status', '--porcelain'),
                     'files': sorted(files, key=lambda x: x['path'])})
result = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'mode': 'read-only source inventory',
          'projects': projects, 'limits': ['No client data or credentials copied', 'No source tests rerun',
          'No redistribution rights inferred; implementation authored separately using architectural lessons']}
target = root / 'evidencias/baseline_execucao_20261007.json'
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps([{'project': p['nome'], 'head': p['head'], 'files': len(p['files']),
                  'changes': len((p['status'] or '').splitlines())} for p in projects], ensure_ascii=False))
