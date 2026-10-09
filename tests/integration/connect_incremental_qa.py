"""Focused regression of R02-R05; isolated synthetic localhost only, no provider send."""
import concurrent.futures
import copy
import hashlib
import hmac
import http.cookiejar
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 'http://127.0.0.1:5186'
P = '/api/connect/v1'
ACCESS = json.loads((ROOT/'tmp/runtime/qa-access.json').read_text(encoding='utf-8-sig'))
CONFIG = json.loads((ROOT/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
CONNECTION = CONFIG['ConnectionStrings']['Platform']
match = re.fullmatch(r'Server=localhost;Database=(EbtPlatformQa_[A-Za-z0-9_]+);Integrated Security=True;Encrypt=True;TrustServerCertificate=True', CONNECTION)
if not match: raise RuntimeError('Only isolated synthetic localhost SQL is permitted')
DB = match[1]
RUN = uuid.uuid4().hex[:10]
CASES = []

def sql(query):
    return subprocess.run(['sqlcmd','-S','localhost','-E','-C','-b','-d',DB,'-h','-1','-Q',
        "SET NOCOUNT ON; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=1; "+query],
        check=True, capture_output=True, text=True).stdout.strip()

class Client:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.open = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
    def req(self, path, method='GET', body=None, expected=200, headers=None, csrf=True):
        headers = dict(headers or {})
        if method != 'GET' and csrf: headers['X-CSRF-TOKEN'] = self.req('/api/security/csrf')['token']
        if body is not None: headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(BASE+path, json.dumps(body).encode() if body is not None else None, headers, method=method)
        try: response = self.open.open(request, timeout=40)
        except urllib.error.HTTPError as error: response = error
        raw = response.read()
        assert response.status == expected, f'{method} {path}: expected {expected}, got {response.status}'
        return json.loads(raw) if raw else None
    def login(self, email, tenant=None):
        self.req('/api/auth/login','POST',{'email':email,'password':ACCESS['password']})
        if tenant: self.req('/api/auth/context/'+tenant,'POST',expected=204)
        return self
    def clone(self):
        client = Client()
        for cookie in self.jar: client.jar.set_cookie(copy.copy(cookie))
        return client

def check(name, action):
    try:
        action(); CASES.append({'case':name,'result':'passed'}); print('PASS',name,flush=True)
    except Exception as error:
        CASES.append({'case':name,'result':'failed','error':str(error)}); print('FAIL',name,str(error),flush=True)

for _ in range(60):
    try:
        Client().req('/health/ready'); break
    except (urllib.error.URLError, AssertionError): time.sleep(.5)
else: raise RuntimeError('Isolated QA server did not become ready')

admin = Client().login('admin@ebt.example', ACCESS['tenantA'])
b = Client().login('admin@ebt.example', ACCESS['tenantB'])
operator = Client().login('operador@ebt.example', ACCESS['tenantA'])
reader = Client().login('consulta@ebt.example', ACCESS['tenantA'])
other = Client().login('outra@ebt.example', ACCESS['tenantA'])

def transfer_guard():
    row = next(x for x in admin.req(P+'/contacts?search=Contato%20Exemplo%20A')['items'] if x['name']=='Contato Exemplo A')
    cmd = {key:row[key] for key in ('name','email','phone','externalKey','organizationId','ownerId','portfolio','stage')}
    denied = admin.req(P+'/contacts/'+row['id'],'PUT',{**cmd,'portfolio':'outra','ownerId':ACCESS['users']['admin@ebt.example'],'organizationId':None},expected=409,headers={'If-Match':f'"{row["version"]}"'})
    assert denied['code']=='contact_channel_transfer_required'
    unchanged = admin.req(P+'/contacts/'+row['id'])
    assert unchanged['portfolio']==row['portfolio'] and unchanged['version']==row['version']
    # Keep the immutable channel recipient while the mutable contact phone changes.
    changed = admin.req(P+'/contacts/'+row['id'],'PUT',{**cmd,'phone':'5511999990088'},headers={'If-Match':f'"{row["version"]}"'})
    try:
        conv = next(x for x in operator.req(P+'/conversations') if x['contactId']==row['id'])
        assert conv['contactName']==row['name'] and conv['recipient']=='5511999990001'
        assert conv['recipient']!=changed['phone']
        body = json.dumps({'object':'whatsapp_business_account','entry':[{'id':'qa-account','changes':[{'field':'messages','value':{'metadata':{'phone_number_id':'qa-phone-a'},'messages':[{'id':'wamid.guard.'+RUN,'from':conv['recipient'],'type':'text','text':{'body':'Guard synthetic '+RUN},'timestamp':str(int(time.time()))}]}}]}]},separators=(',',':')).encode()
        sig = hmac.new(CONFIG['Qa']['AppSecret'].encode(),body,hashlib.sha256).hexdigest()
        request = urllib.request.Request(BASE+'/webhooks/connect/meta/qa-app',body,{'Content-Type':'application/json','X-Hub-Signature-256':'sha256='+sig},method='POST')
        with urllib.request.urlopen(request,timeout=30) as response: assert response.status==200
        for _ in range(30):
            rows = operator.req(P+f'/conversations/{conv["id"]}/messages')['items']
            if any(x['providerId']=='wamid.guard.'+RUN for x in rows): break
            time.sleep(.3)
        assert any(x['providerId']=='wamid.guard.'+RUN for x in rows)
        other.req(P+'/conversations?contactId='+row['id'],expected=404)
        b.req(P+'/conversations?contactId='+row['id'],expected=404)
    finally:
        latest = admin.req(P+'/contacts/'+row['id'])
        admin.req(P+'/contacts/'+row['id'],'PUT',cmd,headers={'If-Match':f'"{latest["version"]}"'})
check('R03 blocks linked transfer without changing version; inbound stays available; R02 immutable recipient and A/B/portfolio',transfer_guard)

def unlinked_transfer():
    row = admin.req(P+'/contacts','POST',{'name':'Unlinked '+RUN},expected=201,headers={'Idempotency-Key':'unlinked-'+RUN})
    moved = admin.req(P+'/contacts/'+row['id'],'PUT',{'name':row['name'],'portfolio':'outra','ownerId':ACCESS['users']['admin@ebt.example']},headers={'If-Match':f'"{row["version"]}"'})
    assert moved['portfolio']=='outra'
    assert other.req(P+'/contacts/'+row['id'])['id']==row['id']
    operator.req(P+'/contacts/'+row['id'],expected=404)
    b.req(P+'/contacts/'+row['id'],expected=404)
check('R03 permits unlinked transfer and enforces the destination portfolio',unlinked_transfer)

def concurrent_transfer():
    row = next(x for x in admin.req(P+'/contacts?search=Contato%20Exemplo%20A')['items'] if x['name']=='Contato Exemplo A')
    cmd = {'name':row['name'],'portfolio':'outra','ownerId':ACCESS['users']['admin@ebt.example']}
    def attempt(client): return client.req(P+'/contacts/'+row['id'],'PUT',cmd,expected=409,headers={'If-Match':f'"{row["version"]}"'})['code']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        codes = list(pool.map(attempt,[admin.clone() for _ in range(3)]))
    assert codes==['contact_channel_transfer_required']*3
    assert admin.req(P+'/contacts/'+row['id'])['version']==row['version']
check('R03 concurrent linked transfers are denied consistently',concurrent_transfer)

def key_lifecycle():
    key = admin.req('/api/admin/api-keys','POST')
    headers = {'Authorization':'Bearer '+key['token']}
    anonymous = Client()
    try:
        anonymous.req(P+'/summary',headers=headers)
        rows = admin.req('/api/admin/api-keys')
        metadata = next(x for x in rows if x['id']==key['id'])
        assert not ({'token','tokenHash','password','passwordHash'} & metadata.keys())
        assert all(x['id']!=key['id'] for x in b.req('/api/admin/api-keys'))
        reader.req('/api/admin/api-keys',expected=403)
        b.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=404)
        sql(f"UPDATE ebt_connect.Credentials SET ExpiresAt=DATEADD(day,-1,SYSUTCDATETIME()) WHERE Id='{uuid.UUID(key['id'])}';")
        anonymous.req(P+'/summary',headers=headers,expected=401)
        assert next(x for x in admin.req('/api/admin/api-keys') if x['id']==key['id'])['state']=='expired'
        admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
        admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
        assert next(x for x in admin.req('/api/admin/api-keys') if x['id']==key['id'])['state']=='revoked'
    finally: admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
check('R04 metadata only, tenant/profile denial, expiry and idempotent revocation',key_lifecycle)

def owner_loses_access():
    key = admin.req('/api/admin/api-keys','POST')
    user = uuid.UUID(ACCESS['users']['admin@ebt.example']); tenant = uuid.UUID(ACCESS['tenantA'])
    headers = {'Authorization':'Bearer '+key['token']}
    try:
        sql(f"UPDATE ebt_connect.Memberships SET Active=0 WHERE TenantId='{tenant}' AND UserId='{user}';")
        Client().req(P+'/summary',headers=headers,expected=401)
    finally:
        sql(f"UPDATE ebt_connect.Memberships SET Active=1 WHERE TenantId='{tenant}' AND UserId='{user}';")
        admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
check('R04 issued key stops working when its owner loses membership',owner_loses_access)

def expired_invite():
    invite = b.req('/api/admin/invitations','POST',{'email':'consulta@ebt.example','role':'reader','portfolio':'principal'})
    sql(f"UPDATE ebt_connect.Invitations SET ExpiresAt=DATEADD(day,-1,SYSUTCDATETIME()) WHERE Id='{uuid.UUID(invite['id'])}';")
    reader.req('/api/auth/invitations/accept-existing','POST',{'token':invite['activationToken']},expected=400)
    assert not any(x['id']==ACCESS['tenantB'] for x in reader.req('/api/auth/me')['tenants'])
    Client().req('/api/auth/invitations/accept-existing','POST',{'token':invite['activationToken']},expected=401)
check('R05 expiry and authentication required; no membership created',expired_invite)

def concurrent_invites():
    invites = [b.req('/api/admin/invitations','POST',{'email':'outra@ebt.example','role':'reader','portfolio':'principal'}) for _ in range(2)]
    wrong = reader.req('/api/auth/invitations/accept-existing','POST',{'token':invites[0]['activationToken']},expected=403)
    assert wrong['code']=='invitation_owner_mismatch'
    def attempt(item):
        client, invite = item
        csrf = client.req('/api/security/csrf')['token']
        request = urllib.request.Request(BASE+'/api/auth/invitations/accept-existing',json.dumps({'token':invite['activationToken']}).encode(),{'Content-Type':'application/json','X-CSRF-TOKEN':csrf},method='POST')
        try: response = client.open.open(request,timeout=40)
        except urllib.error.HTTPError as error: response = error
        response.read(); return response.status
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(pool.map(attempt,[(other.clone(),invite) for invite in invites]))
    assert sorted(codes)==[200,409], codes
    count = sql(f"SELECT COUNT(*) FROM ebt_connect.Memberships WHERE TenantId='{uuid.UUID(ACCESS['tenantB'])}' AND UserId='{uuid.UUID(ACCESS['users']['outra@ebt.example'])}';")
    assert count=='1'
    for invite in invites:
        status = 400 if sql(f"SELECT CASE WHEN UsedAt IS NULL THEN 0 ELSE 1 END FROM ebt_connect.Invitations WHERE Id='{uuid.UUID(invite['id'])}';")=='1' else 409
        other.req('/api/auth/invitations/accept-existing','POST',{'token':invite['activationToken']},expected=status)
    # Accepting links the tenant; it does not silently switch the signed session or reset a password.
    assert other.req('/api/auth/me')['tenantId']==ACCESS['tenantA']
    relogged = Client().login('outra@ebt.example', ACCESS['tenantB'])
    assert relogged.req('/api/auth/me')['role']=='reader'
check('R05 wrong account, concurrent distinct tokens, one membership, replay and original password',concurrent_invites)

report = {'generated_utc':datetime.now(timezone.utc).isoformat(),'environment':DB,'synthetic_only':True,'passed':all(x['result']=='passed' for x in CASES),'cases':CASES,'limits':['No Azure, no real provider send, no user acceptance']}
(ROOT/'evidencias/testes_connect_incremental_20261008.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{sum(x["result"]=="passed" for x in CASES)}/{len(CASES)} passed',flush=True)
raise SystemExit(0 if report['passed'] else 1)
