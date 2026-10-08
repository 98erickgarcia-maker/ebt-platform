"""Create an allowlisted public build context; never copy private configuration."""
from pathlib import Path
import hashlib,json,shutil,uuid
from datetime import datetime,timezone

root=Path(__file__).resolve().parents[1]
target=root/'tmp/container-context'/uuid.uuid4().hex
target.mkdir(parents=True)
sources=[root/'deployment/connect/Dockerfile']
api=root/'src/backend/Ebt.Platform.Api'
sources += [p for p in api.rglob('*') if p.is_file() and not any(x in ('bin','obj','wwwroot') for x in p.relative_to(api).parts) and (p.suffix in ('.cs','.csproj') or p.name in ('packages.lock.json','appsettings.json'))]
front=root/'src/frontend'
sources += [p for p in (front/'src').rglob('*') if p.is_file() and p.suffix in ('.ts','.tsx','.css')]
sources += [front/name for name in ('package.json','package-lock.json','index.html','tsconfig.json','vite.config.ts')]
records=[]
for path in sources:
    relative=Path('Dockerfile') if path.name=='Dockerfile' else path.relative_to(root)
    dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    records.append({'path':relative.as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(target/'.dockerignore').write_text('**/bin\n**/obj\n**/node_modules\n**/.env*\n**/tmp\n**/*.pfx\n**/*.dpapi\n',encoding='utf-8')
report={'generatedUtc':datetime.now(timezone.utc).isoformat(),'context':str(target.relative_to(root)),'sourceFiles':records,'privateFilesIncluded':False,'remoteBuildExecuted':False,'imageVerified':False,'limits':['Allowlist source preparation only; Docker/ACR build pending','No credential, data, QA config, certificate, or keyring included']}
(root/'evidencias/connect_container_preparado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Prepared {len(records)} allowlisted source files in {target.relative_to(root)}; no remote build.')
