"""Fresh-schema rehearsal beside a sentinel of another app, synthetic localhost only."""
import json, os, re, subprocess, uuid
from pathlib import Path
from datetime import datetime, timezone
root=Path(__file__).resolve().parents[1]
config=json.loads((root/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
source=config['ConnectionStrings']['Platform']
if not re.match(r'Server=localhost;Database=EbtPlatformQa_[A-Za-z0-9_]+;',source,re.I): raise RuntimeError('Only isolated localhost fixture')
target='EbtPlatformQa_Migration_'+uuid.uuid4().hex[:10]
work=root/'tmp/migration'/target;work.mkdir(parents=True)
cases=[]
migration_count=len([p for p in (root/'src/backend/Ebt.Platform.Api/Migrations').glob('*.cs') if p.name[:14].isdigit() and not p.name.endswith('.Designer.cs')])
def sql(db,query=None,file=None):
    args=['sqlcmd','-S','localhost','-E','-C','-b','-d',db,'-y','0']
    args+=['-i',str(file)] if file else ['-Q','SET NOCOUNT ON; '+query]
    result=subprocess.run(args,capture_output=True,check=True,encoding='utf-8',errors='replace')
    return result.stdout.strip()
def check(name):cases.append({'name':name,'result':'passed'});print('PASS',name,flush=True)
sql('master',f"IF DB_ID(N'{target}') IS NOT NULL THROW 51010,'Fixture exists',1; CREATE DATABASE [{target}];")
sql(target,"EXEC(N'CREATE SCHEMA qa_other;');")
sql(target,"CREATE TABLE qa_other.Sentinel(Id int PRIMARY KEY,Marker varchar(20)); INSERT qa_other.Sentinel VALUES(1,'preserve');")
sql(target,file=root/'sql/connect-migrations.sql')
check('All current migrations create own schema beside another application')
sql(target,file=root/'sql/connect-migrations.sql')
sql(target,f"IF (SELECT COUNT(*) FROM ebt_connect.__EFMigrationsHistory)<>{migration_count} THROW 51011,'Migration count',1; IF NOT EXISTS(SELECT 1 FROM qa_other.Sentinel WHERE Marker='preserve') THROW 51012,'Sentinel changed',1;")
check('Second migration run preserves ledger and other-schema sentinel')
config['ConnectionStrings']['Platform']=re.sub(r'Database=EbtPlatformQa_[A-Za-z0-9_]+','Database='+target,source)
config['Bootstrap']={'TenantName':'Migration QA only','AdminName':'Migration QA administrator','Email':'migration-admin@ebt.example','Password':config['Qa']['Password']}
path=work/'config.json';path.write_text(json.dumps(config),encoding='utf-8')
env=os.environ.copy();env['ASPNETCORE_ENVIRONMENT']='Development';env['EBT_RUNTIME_CONFIG']=str(path)
dll=root/'src/backend/Ebt.Platform.Api/bin/Debug/net10.0/Ebt.Platform.Api.dll'
result=subprocess.run(['dotnet',str(dll),'--bootstrap'],env=env,cwd=dll.parents[3],capture_output=True,check=True)
sql(target,"IF (SELECT COUNT(*) FROM ebt_connect.Tenants)<>1 OR (SELECT COUNT(*) FROM ebt_connect.Users)<>1 OR (SELECT COUNT(*) FROM ebt_connect.Memberships WHERE Role='admin')<>1 THROW 51013,'Bootstrap failed',1;")
check('Operator bootstrap creates first administrator without QA seed')
again=subprocess.run(['dotnet',str(dll),'--bootstrap'],env=env,cwd=dll.parents[3],capture_output=True)
if again.returncode==0:raise RuntimeError('Bootstrap should refuse non-empty schema')
sql(target,"IF (SELECT COUNT(*) FROM ebt_connect.Users)<>1 THROW 51014,'Bootstrap overwrote records',1;")
check('Repeated bootstrap refuses existing records')
report={'generatedUtc':datetime.now(timezone.utc).isoformat(),'environment':target,'passed':True,'cases':cases,'limits':['Only synthetic localhost; no Azure changes','Existing databases not overwritten or deleted']}
(root/'evidencias/testes_connect_migration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
