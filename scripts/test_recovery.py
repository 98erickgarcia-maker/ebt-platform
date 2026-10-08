"""Synthetic localhost backup/restore only. Never restores over any existing database."""
import hashlib, json, os, re, shutil, subprocess, time, uuid, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
connection = CONFIG['ConnectionStrings']['Platform']
if not re.search(r'(?:^|;)Server=localhost(?:;|$)', connection, re.I): raise RuntimeError('Localhost QA required')
source = re.search(r'(?:^|;)Database=(EbtPlatformQa_[A-Za-z0-9_]+)(?:;|$)', connection, re.I)
if not source: raise RuntimeError('Exclusive synthetic database required')
source = source.group(1)
run = uuid.uuid4().hex[:10]
target = 'EbtPlatformQa_Restore_'+run
workspace = ROOT/'tmp/recovery'/run
workspace.mkdir(parents=True)
report = {'generatedUtc':datetime.now(timezone.utc).isoformat(),'source':source,'target':target,'passed':False,'cases':[],'limits':['Synthetic localhost only','Not an Azure backup or production restore','No existing database overwritten']}
def quote(value): return "N'"+str(value).replace("'","''")+"'"
def sql(database, text, script=None):
    args=['sqlcmd','-S','localhost','-E','-C','-b','-d',database,'-y','0','-w','65535']
    args+=['-i',str(script)] if script else ['-Q','SET NOCOUNT ON; '+text]
    out=subprocess.run(args,capture_output=True,check=True,encoding='utf-8',errors='replace').stdout
    return ''.join(line.strip() for line in out.splitlines()).lstrip('\ufeff')
def passed(name): report['cases'].append({'name':name,'result':'passed'}); print('PASS',name,flush=True)
def snapshot(database):
    tables=['Tenants','Users','Memberships','UserSessions','Invitations','Credentials','Organizations','Contacts','ContactCreations','Interactions','Tasks','Imports','Connections','Conversations','Messages','Outbox','Receipts','DeliveryEvents','Documents','DocumentVersions','Audit']
    # Obtain actual model table names rather than assume CLR pluralization.
    raw=sql(database,"SELECT t.name FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id WHERE s.name='ebt_connect' ORDER BY t.name FOR JSON PATH")
    result={}
    for row in json.loads(raw):
        table=row['name']
        if not re.fullmatch(r'[A-Za-z_]+',table): raise RuntimeError('Unexpected table name')
        key='MigrationId' if table=='__EFMigrationsHistory' else 'Id'
        data=sql(database,f"EXEC sys.sp_set_session_context @key=N'ebt_system',@value=1; DECLARE @j nvarchar(max)=(SELECT * FROM ebt_connect.[{table}] ORDER BY [{key}] FOR JSON PATH,INCLUDE_NULL_VALUES); SELECT @j;")
        result[table]=hashlib.sha256(data.encode()).hexdigest()
    result['other_schema']=hashlib.sha256(sql(database,'SELECT * FROM qa_other.Sentinel ORDER BY Id FOR JSON PATH').encode()).hexdigest()
    return result
try:
    if sql('master',f'SELECT COUNT(*) FROM sys.databases WHERE name={quote(target)}')!='0': raise RuntimeError('Restore target exists')
    before=snapshot(source)
    folder=sql('master',"SELECT CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultBackupPath'))")
    data_folder=sql('master',"SELECT CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultDataPath'))")
    log_folder=sql('master',"SELECT CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultLogPath'))")
    backup=Path(folder)/(target+'.bak')
    sql('master',f'BACKUP DATABASE [{source}] TO DISK={quote(backup)} WITH COPY_ONLY,CHECKSUM;')
    sql('master',f'RESTORE VERIFYONLY FROM DISK={quote(backup)} WITH CHECKSUM;')
    passed('COPY_ONLY backup checksum verified')
    logical=json.loads(sql(source,'SELECT name,type FROM sys.database_files ORDER BY type FOR JSON PATH'))
    if len(logical)!=2: raise RuntimeError('Unexpected QA file layout')
    moves=','.join('MOVE '+quote(row['name'])+' TO '+quote(Path(data_folder if row['type']==0 else log_folder)/(target+('.mdf' if row['type']==0 else '.ldf'))) for row in logical)
    sql('master',f'RESTORE DATABASE [{target}] FROM DISK={quote(backup)} WITH CHECKSUM,{moves};')
    if before!=snapshot(target): raise RuntimeError('Restored data/metadata differ')
    passed('Restored table fingerprints and other-schema sentinel match')
    sql(target,'',ROOT/'sql/connect-migrations.sql'); sql(target,'',ROOT/'sql/connect-migrations.sql')
    if before!=snapshot(target): raise RuntimeError('Idempotent migration changed records')
    passed('Migration script reapplied twice preserves data and other schema')
    shutil.copytree(Path(CONFIG['Platform']['KeyPath']),workspace/'keys')
    cfg=json.loads(json.dumps(CONFIG));cfg['ConnectionStrings']['Platform']=connection.replace('Database='+source,'Database='+target)
    cfg['Platform']['KeyPath']=str(workspace/'keys');cfg['Qa']['RecoveryReport']=str(ROOT/'evidencias/testes_connect_restore_integridade.json')
    path=workspace/'restore-config.json';path.write_text(json.dumps(cfg),encoding='utf-8')
    env=os.environ.copy();env['EBT_RUNTIME_CONFIG']=str(path);env['ASPNETCORE_ENVIRONMENT']='Development';env['MSBuildEnableWorkloadResolver']='false'
    dll=ROOT/'src/backend/Ebt.Platform.Api/bin/Debug/net10.0/Ebt.Platform.Api.dll'
    subprocess.run(['dotnet',str(dll),'--verify-recovery'],env=env,check=True)
    passed('Copied protected key ring decrypts restored envelopes; all document hashes match')
    with (workspace/'worker.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen(['dotnet',str(dll),'--urls','http://127.0.0.1:5188'],cwd=dll.parents[3],env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(40):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:5188/health/ready',timeout=2) as response: assert response.status==200
                    break
                except Exception: time.sleep(.5)
            else: raise RuntimeError('Restored runtime not ready')
            time.sleep(17)
            if before!=snapshot(target): raise RuntimeError('Worker restart changed restored terminal records')
            passed('Restored runtime ready; worker restart preserves unknown and terminal sends without resending')
        finally:
            process.terminate();process.wait(timeout=20)
    report['fingerprints']=before;report['passed']=True
finally:
    (ROOT/'evidencias/testes_connect_restore.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
