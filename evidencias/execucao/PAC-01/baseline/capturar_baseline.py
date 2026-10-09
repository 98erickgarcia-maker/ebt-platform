"""Somente leitura na fonte; grava exclusivamente metadados sanitizados neste diretório."""
from pathlib import Path
import hashlib, json, subprocess, datetime, re, xml.etree.ElementTree as ET

SOURCE = Path(r'C:\Users\Ivair Silva\Documents\Codex\2026-08-18\CRM_CASST_WEB\.worktrees\crm-casst-foundation')
OUT = Path(__file__).resolve().parent
def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args]).decode('utf-8', 'replace').strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def technical(path):
    if path in {'src/frontend/package.json','src/frontend/package-lock.json','global.json','Directory.Build.props','Directory.Packages.props','CrmCasst.Web.sln'}:
        return True
    return path.startswith(('src/', 'tests/', '.github/workflows/')) and Path(path).suffix.lower() in {'.cs','.csproj','.ts','.tsx','.css','.sln','.props','.targets','.yml','.yaml'} and not any(x in path.split('/') for x in ('bin','obj','node_modules','dist','test-results','playwright-report')) and not re.search(r'(?i)(secret|credential|appsettings|\.env|customers?[-_].*\d)',path)

before = git('status','--porcelain=v1','--untracked-files=all')
tracked = git('ls-files').splitlines()
untracked = git('ls-files','--others','--exclude-standard').splitlines()
status = {line[3:].replace('\\','/'):line[:2] for line in before.splitlines()}
rows=[]
for name in sorted(set(tracked+untracked)):
    if not technical(name):
        continue
    path=SOURCE/name
    if path.is_file():
        local_hash=sha(path)
        head_hash=None
        if name in tracked:
            result=subprocess.run(['git','-C',str(SOURCE),'show','HEAD:'+name],capture_output=True)
            if result.returncode==0:
                head_hash=hashlib.sha256(result.stdout).hexdigest()
        rows.append(dict(path=name, sha256=local_hash, bytes=path.stat().st_size, tracked=name in tracked, git_status=status.get(name,'  '), head_sha256=head_hash, differs_from_head=local_hash!=head_hash))
verified=all(sha(SOURCE/row['path'])==row['sha256'] for row in rows)
after=git('status','--porcelain=v1','--untracked-files=all')
dump('manifesto-fonte.json',dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_alias='CASST/crm-casst-foundation',head=git('rev-parse','HEAD'),scope='superset técnico src/tests/workflows; produtores/consumidores do recorte devem apontar para estes hashes',files=rows,second_hash_pass=verified,source_status_unchanged=before==after))
dump('status-fonte.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),all_status_count=len(before.splitlines()),technical_status=[dict(path=name,status=state) for name,state in status.items() if technical(name)],other_status=[dict(path_sha256=hashlib.sha256(name.encode()).hexdigest(),status=state) for name,state in status.items() if not technical(name)],note='Caminhos fora do recorte técnico substituídos por hash para não divulgar nomes de clientes. Nenhum diff/conteúdo copiado.',status_unchanged=before==after))
evidence=[]
folder=SOURCE/'outputs/melhorias-operacionais-2026-10-05'
for path in sorted(folder.rglob('*.trx')):
    root=ET.parse(path).getroot()
    counters=next((node.attrib for node in root.iter() if node.tag.endswith('Counters')), {})
    times=next((node.attrib for node in root.iter() if node.tag.endswith('Times')), {})
    evidence.append(dict(path=path.relative_to(SOURCE).as_posix(),sha256=sha(path),times=times,counters=counters,level='histórico/local',version_binding='Não há manifesto da árvore executada no TRX; hash do log não certifica equivalência ao snapshot atual.'))
for name in ['infra-sql-final.log','infra-sql-retest.log','infra-sql-conclusivo.log','testes-backend-final.log','e2e-quarta.log','e2e-hardening-final.log']:
    path=folder/name
    if not path.exists():
        continue
    content=path.read_text(encoding='utf-8',errors='replace')
    summary=re.findall(r'\b\d+\s+(?:passed|failed|did not run|skipped)\b',content)
    summary += re.findall(r'\b(?:tests|pass|fail|cancelled|skipped)\s+\d+\b',content)
    evidence.append(dict(path=path.relative_to(SOURCE).as_posix(),sha256=sha(path),file_modified_utc=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),level='histórico/local',summary_counts=summary[-12:],mentions_onboarding=bool(re.search(r'(?i)onboarding|activation|ativação|activate',content)),mentions_cancelled=bool(re.search(r'(?i)cancelled|canceled|cancelad',content)),version_binding='Ausente; mtime é metadado, não horário confirmado da execução. Conteúdo privado não copiado.'))
dump('evidencias-historicas.json',evidence)
print(json.dumps(dict(manifest_files=len(rows),untracked_technical=sum(not r['tracked'] for r in rows),hashes_reproduced=verified,source_status_unchanged=before==after,historical_records=len(evidence))))
