"""Restore synthetic GitHub SQL service into a new database; never accepts a cloud source."""
import hashlib
import http.cookiejar
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if os.environ.get('GITHUB_ACTIONS') != 'true': raise RuntimeError('Dedicated GitHub CI only')
run = os.environ.get('GITHUB_RUN_ID', '')
container = os.environ.get('EBT_QA_SQL_CONTAINER', '')
password = os.environ.get('EBT_SQL_PASSWORD', '')
if not run.isdigit() or not re.fullmatch(r'[a-f0-9]{12,64}', container): raise RuntimeError('Isolated SQL service required')
if password != 'EbtQa_'+run+'!X': raise RuntimeError('Synthetic CI credential required')
CONFIG = json.loads((ROOT/'tmp/runtime/local-config.json').read_text(encoding='utf-8'))
source = 'EbtPlatformQa_Ci_'+run
connection = CONFIG['ConnectionStrings']['Platform']
expected = f'Server=localhost;Database={source};User Id=sa;Password={password};Encrypt=True;TrustServerCertificate=True'
if connection != expected: raise RuntimeError('Exclusive localhost synthetic source required')
image = subprocess.run(['docker', 'inspect', '--format', '{{.Config.Image}}', container], check=True, capture_output=True, text=True).stdout.strip()
if image != 'mcr.microsoft.com/mssql/server@sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090':
    raise RuntimeError('SQL service image differs from reviewed fixture')
target = 'EbtPlatformQa_Restore_'+uuid.uuid4().hex[:10]
workspace = ROOT/'tmp/recovery'/target
workspace.mkdir(parents=True)
report = {'generatedUtc': datetime.now(timezone.utc).isoformat(), 'source': source, 'target': target,
          'passed': False, 'cases': [], 'limits': ['Synthetic isolated CI only', 'Not Azure PITR or production restore', 'No existing database overwritten']}

def quote(value): return "N'"+str(value).replace("'", "''")+"'"
def sql(database, text):
    # Synthetic password stays in process environment, never in SQL, argv or reports.
    args = ['docker', 'exec', '-i', '-e', 'SQLCMDPASSWORD', container, '/opt/mssql-tools18/bin/sqlcmd',
            '-S', 'localhost', '-U', 'sa', '-C', '-b', '-d', database, '-y', '0', '-w', '65535']
    result = subprocess.run(args, input='SET NOCOUNT ON;\n'+text, capture_output=True, text=True,
                            env={**os.environ, 'SQLCMDPASSWORD': password}, timeout=120)
    if result.returncode: raise RuntimeError('Synthetic SQL recovery command failed; private SQL output omitted')
    return ''.join(line.strip() for line in result.stdout.splitlines()).lstrip('\ufeff')
def passed(name):
    report['cases'].append({'name': name, 'result': 'passed'})
    print('PASS', name, flush=True)
def snapshot(database):
    tables = json.loads(sql(database, "SELECT t.name FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id WHERE s.name='ebt_connect' ORDER BY t.name FOR JSON PATH"))
    result = {}
    for row in tables:
        table = row['name']
        if not re.fullmatch(r'[A-Za-z_]+', table): raise RuntimeError('Unexpected fixture table')
        key = 'MigrationId' if table == '__EFMigrationsHistory' else 'Id'
        data = sql(database, f"EXEC sys.sp_set_session_context @key=N'ebt_system',@value=1; SELECT (SELECT * FROM ebt_connect.[{table}] ORDER BY [{key}] FOR JSON PATH,INCLUDE_NULL_VALUES);")
        result[table] = hashlib.sha256(data.encode()).hexdigest()
    result['other_schema'] = hashlib.sha256(sql(database, 'SELECT * FROM qa_other.Sentinel ORDER BY Id FOR JSON PATH').encode()).hexdigest()
    return result

class Client:
    def __init__(self): self.open = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def req(self, path, method='GET', data=None, expected=200, raw=False):
        headers = {}
        if method != 'GET': headers['X-CSRF-TOKEN'] = self.req('/api/security/csrf')['token']
        body = None if data is None else json.dumps(data).encode()
        if body is not None: headers['Content-Type'] = 'application/json'
        try: response = self.open.open(urllib.request.Request('http://127.0.0.1:5188'+path, data=body, method=method, headers=headers), timeout=10)
        except urllib.error.HTTPError as exc: response = exc
        payload = response.read()
        if response.status != expected: raise RuntimeError(f'Restored HTTP status {response.status}, expected {expected}')
        return payload if raw else json.loads(payload) if payload else None
    def login(self, email, access): self.req('/api/auth/login', 'POST', {'email': email, 'password': access['password']})

try:
    if sql('master', f'SELECT COUNT(*) FROM sys.databases WHERE name={quote(target)}') != '0': raise RuntimeError('Restore target exists')
    before = snapshot(source)
    backup_folder = sql('master', "SELECT CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultBackupPath'))")
    data_folder = sql('master', "SELECT CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultDataPath'))")
    log_folder = sql('master', "SELECT CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultLogPath'))")
    backup = str(Path(backup_folder)/(target+'.bak'))
    sql('master', f'BACKUP DATABASE [{source}] TO DISK={quote(backup)} WITH COPY_ONLY,CHECKSUM;')
    sql('master', f'RESTORE VERIFYONLY FROM DISK={quote(backup)} WITH CHECKSUM;')
    passed('COPY_ONLY backup checksum verified')
    logical = json.loads(sql(source, 'SELECT name,type FROM sys.database_files ORDER BY type FOR JSON PATH'))
    if len(logical) != 2: raise RuntimeError('Unexpected QA file layout')
    moves = ','.join('MOVE '+quote(row['name'])+' TO '+quote(Path(data_folder if row['type'] == 0 else log_folder)/(target+('.mdf' if row['type'] == 0 else '.ldf'))) for row in logical)
    sql('master', f'RESTORE DATABASE [{target}] FROM DISK={quote(backup)} WITH CHECKSUM,{moves};')
    if before != snapshot(target): raise RuntimeError('Restored fingerprints differ')
    passed('Restored table fingerprints and other-schema sentinel match')
    migration = (ROOT/'sql/connect-migrations.sql').read_text(encoding='utf-8-sig')
    sql(target, migration); sql(target, migration)
    if before != snapshot(target): raise RuntimeError('Idempotent migration changed records')
    passed('Reviewed migration reapplied twice preserves data and other schema')
    shutil.copytree(Path(CONFIG['Platform']['KeyPath']), workspace/'keys')
    cfg = json.loads(json.dumps(CONFIG))
    cfg['ConnectionStrings']['Platform'] = connection.replace('Database='+source+';', 'Database='+target+';')
    cfg['Platform']['KeyPath'] = str(workspace/'keys')
    cfg['Qa']['RecoveryReport'] = str(ROOT/'evidencias/testes_restore_ci_integridade.json')
    config_path = workspace/'restore-config.json'
    config_path.write_text(json.dumps(cfg), encoding='utf-8')
    env = {**os.environ, 'EBT_RUNTIME_CONFIG': str(config_path), 'ASPNETCORE_ENVIRONMENT': 'Development'}
    dll = ROOT/'src/backend/Ebt.Platform.Api/bin/Release/net10.0/Ebt.Platform.Api.dll'
    subprocess.run(['dotnet', str(dll), '--verify-recovery'], env=env, check=True, timeout=60)
    passed('Copied key ring decrypts restored envelopes; every document hash matches')
    with (workspace/'worker.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(['dotnet', str(dll), '--urls', 'http://127.0.0.1:5188'], cwd=ROOT/'src/backend/Ebt.Platform.Api', env=env, stdout=log, stderr=log)
        try:
            for _ in range(40):
                try: Client().req('/health/ready'); break
                except (OSError, RuntimeError): time.sleep(.5)
            else: raise RuntimeError('Restored runtime unavailable')
            time.sleep(17)
            if before != snapshot(target): raise RuntimeError('Worker restart changed restored terminal records')
            passed('Restored runtime ready; worker preserves unknown/terminal sends without resending')
            access = json.loads((ROOT/'tmp/runtime/qa-access.json').read_text(encoding='utf-8'))
            operator = Client(); operator.login('operador@ebt.example', access)
            contacts = operator.req('/api/connect/v1/contacts')['items']
            if not contacts: raise RuntimeError('Restored CRM empty')
            passed('Restored account login and contact query work')
            docs = operator.req('/api/connect/v1/documents')
            selected = None
            for doc in docs:
                versions = operator.req('/api/connect/v1/documents/'+doc['id']+'/versions')
                selected = next(((doc, version) for version in versions if version['reviewState'] == 'approved' and version['scanState'] == 'clean'), None)
                if selected: break
            if not selected: raise RuntimeError('Restored clean approved document required')
            doc, version = selected
            path = f'/api/connect/v1/documents/{doc["id"]}/download/{version["number"]}'
            reader = Client(); reader.login('consulta@ebt.example', access)
            if hashlib.sha256(reader.req(path, raw=True)).hexdigest() != version['sha256']: raise RuntimeError('Restored download hash mismatch')
            passed('Authorized restored download bytes match stored SHA256')
            other = Client(); other.login('admin@ebt.example', access)
            other.req('/api/auth/context/'+access['tenantB'], 'POST', expected=204)
            other.req(path, expected=404)
            passed('Tenant B cannot download restored tenant A document by ID')
            incident = reader.req('/api/connect/v1/documents/'+str(uuid.uuid4())+'/download/1', expected=404)
            if not incident.get('traceId') or any(value in json.dumps(incident) for value in (access['password'], password, CONFIG['Qa']['AppSecret'])):
                raise RuntimeError('Restored incident diagnostic unsafe or missing traceId')
            passed('Restored negative request returns traceId without fixture secrets')
        finally:
            process.terminate(); process.wait(timeout=20)
    if before != snapshot(source): raise RuntimeError('Recovery changed original source')
    passed('Source database preserved by isolated restore')
    report['fingerprints'] = before
    report['passed'] = True
finally:
    (ROOT/'evidencias/testes_restore_ci.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
