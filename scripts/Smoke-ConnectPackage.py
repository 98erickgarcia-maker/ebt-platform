"""Smoke only the exported package, synthetic localhost SQL, and no provider key."""
from pathlib import Path
import json,os,subprocess,time,urllib.request,urllib.error,uuid
from datetime import datetime,timezone

root=Path(__file__).resolve().parents[1]
config=json.loads((root/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
if config['ConnectionStrings']['Platform']!='Server=localhost;Database=EbtPlatformQa_20261007Migrated;Integrated Security=True;Encrypt=True;TrustServerCertificate=True':raise RuntimeError('Exclusive localhost QA required')
if any(name.startswith(('Meta__Connections__','WazVox__Connections__')) for name in os.environ):raise RuntimeError('Provider environment credentials forbidden')
config['Platform']['RunWorkers']=False;config['Meta']={'Enabled':False};config['WazVox']={'Enabled':False}
work=root/'tmp/package-smoke'/uuid.uuid4().hex;work.mkdir(parents=True)
path=work/'config.json';path.write_text(json.dumps(config),encoding='utf-8')
package=root/'tmp/release/connect-azure-0.1.2'
env=os.environ.copy();env['ASPNETCORE_ENVIRONMENT']='Development';env['EBT_RUNTIME_CONFIG']=str(path)
env.pop('EBT_SQL_ACCESS_TOKEN',None);env.pop('ConnectionStrings__Platform',None)
base='http://127.0.0.1:5189'
checks=[]
with (work/'runtime.log').open('w',encoding='utf-8') as log:
    process=subprocess.Popen(['dotnet',str(package/'Ebt.Platform.Api.dll'),'--urls',base],cwd=package,env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for _ in range(35):
            try:
                with urllib.request.urlopen(base+'/health/ready',timeout=2) as response:assert response.status==200
                break
            except Exception:time.sleep(.4)
        else:raise RuntimeError('Exported package not ready')
        checks.append('Exported package reads migrated synthetic SQL')
        with urllib.request.urlopen(base+'/',timeout=4) as response:
            assert response.status==200 and b'<div id="root"></div>' in response.read()
            assert response.headers['X-Content-Type-Options']=='nosniff'
        checks.append('Exported frontend and security headers served')
        try:urllib.request.urlopen(base+'/api/contacts',timeout=4);raise RuntimeError('Anonymous access accepted')
        except urllib.error.HTTPError as exc:assert exc.code==401
        checks.append('Anonymous access to contacts denied')
    finally:process.terminate();process.wait(timeout=15)
report={'generatedUtc':datetime.now(timezone.utc).isoformat(),'passed':True,'cases':len(checks),'checks':checks,'artifact':str(package.relative_to(root)),'limits':['Synthetic localhost only; no hosted availability proof','No real provider credentials loaded or messages sent']}
(root/'evidencias/testes_connect_pacote_runtime.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for item in checks:print('PASS',item)
