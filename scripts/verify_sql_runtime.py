"""Prevent MongoDB returning to the supported EBT Connect build/runtime."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
patterns = re.compile(r'mongodb|pymongo|motor\.motor|AsyncIOMotorClient|MONGO_URL', re.I)
files = []
for directory in ['src/backend/Ebt.Platform.Api','src/frontend/src','deployment/connect']:
    for path in (ROOT/directory).rglob('*'):
        if path.suffix not in ('.cs','.csproj','.ts','.tsx','.json','.yml','.yaml') and path.name != 'Dockerfile': continue
        if any(part in ('bin','obj','node_modules','wwwroot') for part in path.parts): continue
        files.append(path)
files += [ROOT/'src/frontend/package.json',ROOT/'src/frontend/package-lock.json',ROOT/'scripts/Start-Local.ps1']
findings=[str(p.relative_to(ROOT)).replace('\\','/') for p in files if patterns.search(p.read_text(encoding='utf-8'))]
report={'runtime':'EBT Connect .NET / EF Core / SQL Server / React','filesChecked':len(files),'mongodbDependencies':findings,'passed':not findings,'archiveSources':'Historical Mail/Emergent packages preserved outside supported runtime; no real-data import'}
(ROOT/'evidencias/runtime_sql_20261009.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(bool(findings))
