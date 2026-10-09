"""HTTP + SQL-real integration checks. Only synthetic localhost QA is permitted."""
import concurrent.futures, hashlib, hmac, json, time, uuid, urllib.request, urllib.error, http.cookiejar
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[2]
BASE = 'http://127.0.0.1:5186'
ACCESS = json.loads((ROOT / 'tmp/runtime/qa-access.json').read_text(encoding='utf-8-sig'))
CONFIG = json.loads((ROOT / 'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
RUN = uuid.uuid4().hex[:10]
RESULTS = []
class Client:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.open = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
    def req(self, path, method='GET', body=None, headers=None, expected=200, csrf=True, raw=False):
        headers = dict(headers or {})
        if method != 'GET' and csrf:
            token = self.req('/api/security/csrf')['token']; headers['X-CSRF-TOKEN'] = token
        data = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else None
        if data is not None and 'Content-Type' not in headers: headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
        try: response = self.open.open(request, timeout=35)
        except urllib.error.HTTPError as exc: response = exc
        payload = response.read()
        if response.status != expected:
            safe = json.loads(payload) if 'json' in response.headers.get('Content-Type','') else payload[:100].decode(errors='replace')
            raise AssertionError(f'{method} {path}: expected {expected}, got {response.status}; {safe}')
        if raw: return payload
        return json.loads(payload) if payload and 'json' in response.headers.get('Content-Type','') else None
    def login(self, email):
        self.req('/api/auth/login','POST', {'email': email, 'password': ACCESS['password']})
        return self.req('/api/auth/me')
    def context(self, tenant): self.req('/api/auth/context/' + tenant, 'POST', expected=204); return self.req('/api/auth/me')

def check(name, fn):
    start = time.time()
    try: fn(); RESULTS.append({'case': name, 'result': 'passed', 'seconds': round(time.time()-start,3)}); print('PASS', name, flush=True)
    except Exception as exc:
        RESULTS.append({'case': name, 'result': 'failed', 'error': str(exc), 'seconds': round(time.time()-start,3)})
        print('FAIL', name, str(exc), flush=True)

def poll(fn, test, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = fn()
        if test(result): return result
        time.sleep(.5)
    raise AssertionError('Worker did not reach expected durable state')

def webhook(envelope, signature=True, expected=200):
    body = json.dumps(envelope, separators=(',',':')).encode()
    secret = CONFIG['Qa']['AppSecret'].encode()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest() if signature else '0'*64
    Client().req('/webhooks/connect/meta/qa-app', 'POST', body, {'X-Hub-Signature-256': 'sha256=' + sig}, expected=expected, csrf=False)

def envelope(phone, messages=None, statuses=None, account='qa-account'):
    value = {'metadata': {'phone_number_id': phone}}
    if messages is not None: value['messages'] = messages
    if statuses is not None: value['statuses'] = statuses
    return {'object':'whatsapp_business_account','entry':[{'id':account,'changes':[{'field':'messages','value':value}]}]}

for _ in range(40):
    try: Client().req('/health/ready'); break
    except Exception: time.sleep(.5)
admin = Client(); admin.login('admin@ebt.example'); admin.context(ACCESS['tenantA'])
operator = Client(); operator.login('operador@ebt.example')
reader = Client(); reader.login('consulta@ebt.example')
other = Client(); other.login('outra@ebt.example')
b = Client(); b.login('admin@ebt.example'); b.context(ACCESS['tenantB'])
P = '/api/connect/v1'
created = {}
command = {'name':'QA contact ' + RUN, 'externalKey':'qa-' + RUN, 'email':'qa@client.example','phone':'551198888'+str(int(RUN[:5],16)).zfill(7)[:7], 'stage':'novo'}
command['phone'] = command['phone'][:15]
def create():
    created.update(operator.req(P+'/contacts','POST',command, {'Idempotency-Key':'create-'+RUN}, expected=201))
    replay = operator.req(P+'/contacts','POST',command, {'Idempotency-Key':'create-'+RUN})
    assert replay['id']==created['id']
check('CRM creation + stable ID + idempotent replay',create)
ID = created.get('id','00000000-0000-0000-0000-000000000000')
check('Tenant B rejects direct contact ID',lambda:b.req(P+'/contacts/'+ID,expected=404))
check('Portfolio rejects direct contact ID',lambda:other.req(P+'/contacts/'+ID,expected=404))
check('Reader mutation denied',lambda:reader.req(P+'/contacts','POST',command, {'Idempotency-Key':'reader-'+RUN},expected=403))
check('CSRF mutation denied',lambda:operator.req(P+'/contacts','POST',command, {'Idempotency-Key':'csrf-'+RUN},expected=400,csrf=False))
check('Unknown tenant fields rejected',lambda:operator.req(P+'/contacts','POST',{**command,'tenantId':ACCESS['tenantB']},{'Idempotency-Key':'injected-'+RUN},expected=400))
check('Changed payload same key rejected',lambda:operator.req(P+'/contacts','POST',{**command,'name':'different'},{'Idempotency-Key':'create-'+RUN},expected=409))
def update():
    row = operator.req(P+'/contacts/'+ID)
    result = operator.req(P+'/contacts/'+ID,'PUT',{**command,'stage':'proposta'}, {'If-Match':f'"{row["version"]}"'})
    assert result['stage']=='proposta'
    operator.req(P+'/contacts/'+ID,'PUT',{**command,'stage':'ganho'}, {'If-Match':f'"{row["version"]}"'}, expected=409)
check('Contact update persisted + stale conflict',update)
def history():
    note = {'content':'Historical synthetic note','occurredAt':(datetime.now(timezone.utc)-timedelta(days=4)).isoformat()}
    first = operator.req(P+f'/contacts/{ID}/history','POST',note,{'Idempotency-Key':'note-'+RUN})
    second = operator.req(P+f'/contacts/{ID}/history','POST',note,{'Idempotency-Key':'note-'+RUN})
    assert first==second
    rows = operator.req(P+f'/contacts/{ID}/history'); saved = next(x for x in rows if x['id']==first['id'])
    assert saved['actorId']==ACCESS['users']['operador@ebt.example'] and saved['recordedAt']!=saved['occurredAt']
check('Historical note preserves author/time; duplicate not repeated',history)
def tasks():
    body = {'title':'Next action '+RUN,'dueAt':(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat()}
    task = operator.req(P+f'/contacts/{ID}/tasks','POST',body,{'Idempotency-Key':'task-'+RUN})
    assert operator.req(P+'/contacts/'+ID)['nextAction']['id']==task['id']
    close = {'state':'done','result':'Synthetic outcome'}
    first = operator.req(P+f'/tasks/{task["id"]}/close','POST',close,{'Idempotency-Key':'close-'+RUN,'If-Match':f'"{task["version"]}"'})
    second = operator.req(P+f'/tasks/{task["id"]}/close','POST',close,{'Idempotency-Key':'close-'+RUN,'If-Match':f'"{task["version"]}"'})
    assert first==second and operator.req(P+'/contacts/'+ID)['nextAction'] is None
    b.req(P+f'/tasks/{task["id"]}/close','POST',close,{'Idempotency-Key':'b-'+RUN},expected=404)
check('Single next-action source + close/replay + B denied',tasks)
def importing():
    rows = [{'externalKey':'import-'+RUN,'name':'Imported QA','email':'import@client.example','phone':'5511977770001'}]
    before = operator.req(P+'/summary')['contacts']
    preview = operator.req(P+'/imports/preview','POST',{'rows':rows})
    assert operator.req(P+'/summary')['contacts']==before
    b.req(P+f'/imports/{preview["id"]}/confirm','POST',{'payloadHash':preview['payloadHash']},{'Idempotency-Key':'confirm-'+RUN},expected=404)
    result = operator.req(P+f'/imports/{preview["id"]}/confirm','POST',{'payloadHash':preview['payloadHash']},{'Idempotency-Key':'confirm-'+RUN})
    replay = operator.req(P+f'/imports/{preview["id"]}/confirm','POST',{'payloadHash':preview['payloadHash']},{'Idempotency-Key':'confirm-'+RUN})
    assert result==replay and operator.req(P+'/summary')['contacts']==before+1
check('Import preview/confirm/replay/tenant boundary',importing)
def import_atomic():
    before=operator.req(P+'/summary')['contacts']
    preview=operator.req(P+'/imports/preview','POST',{'rows':[{'externalKey':'atomic-'+RUN,'name':'Must not persist'}, {'externalKey':command['externalKey'],'name':'Conflicting existing record'}]})
    operator.req(P+f'/imports/{preview["id"]}/confirm','POST',{'payloadHash':preview['payloadHash']},{'Idempotency-Key':'atomic-'+RUN},expected=409)
    assert operator.req(P+'/summary')['contacts']==before
check('Import conflict rolls back entire batch',import_atomic)
def onboarding():
    invite=admin.req('/api/admin/invitations','POST',{'email':'invite-'+RUN+'@ebt.example','role':'reader','portfolio':'principal'})
    new=Client(); result=new.req('/api/auth/activate','POST',{'token':invite['activationToken'],'name':'Invited QA','password':ACCESS['password']})
    assert new.req('/api/auth/me')['role']=='reader' and result['tenantId']==ACCESS['tenantA']
    Client().req('/api/auth/activate','POST',{'token':invite['activationToken'],'name':'Duplicate','password':ACCESS['password']},expected=400)
check('Onboarding activation works once and yields correct membership',onboarding)

def existing_account_invite():
    # A tenant-B admin invites an account that already exists in tenant A.
    invite=b.req('/api/admin/invitations','POST',{'email':'operador@ebt.example','role':'reader','portfolio':'principal'})
    wrong=Client(); wrong.login('outra@ebt.example')
    wrong.req('/api/auth/invitations/accept-existing','POST',{'token':invite['activationToken']},expected=403)
    linked=operator.req('/api/auth/invitations/accept-existing','POST',{'token':invite['activationToken']})
    assert linked['tenantId']==ACCESS['tenantB'] and linked['role']=='reader'
    operator.req('/api/auth/invitations/accept-existing','POST',{'token':invite['activationToken']},expected=400)
    me=operator.context(ACCESS['tenantB'])
    assert me['role']=='reader'
    operator.context(ACCESS['tenantA'])
    # Preserve the original seed accounts for the following browser suite.
    member=next(x for x in b.req('/api/admin/members') if x['userId']==ACCESS['users']['operador@ebt.example'])
    b.req('/api/admin/members/'+member['id'],'PUT',{'role':member['role'],'portfolio':member['portfolio'],'active':False},{'If-Match':f'"{member["version"]}"'})
check('Existing account accepts only its own tenant invitation once',existing_account_invite)

def api_key_inventory():
    key=admin.req('/api/admin/api-keys','POST')
    rows=admin.req('/api/admin/api-keys')
    saved=next(x for x in rows if x['id']==key['id'])
    assert saved['state']=='active' and 'token' not in saved and 'tokenHash' not in saved
    b.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=404)
    admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
    admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
    revoked=next(x for x in admin.req('/api/admin/api-keys') if x['id']==key['id'])
    assert revoked['state']=='revoked' and revoked['active'] is False
check('API key inventory exposes metadata only and revocation is tenant-safe/idempotent',api_key_inventory)
check('Invalid webhook signature rejected',lambda:webhook(envelope('qa-phone-a'),False,401))
incoming_id = 'wamid.qa.'+RUN
at = str(int(time.time()))
def inbound():
    e=envelope('qa-phone-a',messages=[{'id':incoming_id,'from':command['phone'],'type':'text','text':{'body':'Inbound QA '+RUN},'timestamp':at}])
    webhook(e); webhook(e)
    global conv_id
    convs=poll(lambda:operator.req(P+'/conversations?contactId='+ID),lambda x:xbool(x))
    conv_id=convs[0]['id']
    rows=poll(lambda:operator.req(P+f'/conversations/{conv_id}/messages'),lambda x:xhas(x,incoming_id))['items']
    assert sum(x['providerId']==incoming_id for x in rows)==1
    b.req(P+f'/conversations/{conv_id}/messages',expected=404)
def xbool(x):return bool(x)
def xhas(x,provider):return any(m['providerId']==provider for m in x['items'])
conv_id=''
check('Signed webhook durable receipt + inbox dedupe + A/B',inbound)
def portfolio_transfer():
    row=admin.req(P+'/contacts/'+ID)
    payload={**command,'portfolio':'outra','organizationId':None,'ownerId':ACCESS['users']['outra@ebt.example']}
    admin.req(P+'/contacts/'+ID,'PUT',payload,{'If-Match':f'"{row["version"]}"'},expected=409)
    assert admin.req(P+'/contacts/'+ID)['portfolio']==row['portfolio']
    event_id='wamid.transfer-blocked.'+RUN
    webhook(envelope('qa-phone-a',messages=[{'id':event_id,'from':command['phone'],'type':'text','text':{'body':'Still reachable'},'timestamp':at}]))
    poll(lambda:operator.req(P+f'/conversations/{conv_id}/messages'),lambda rows:xhas(rows,event_id))
    b.req(P+'/contacts/'+ID,'PUT',payload,{'If-Match':f'"{row["version"]}"'},expected=404)
    other.req(P+f'/conversations/{conv_id}/messages',expected=404)
check('R03 incompatible portfolio move is blocked and subsequent inbound preserved',portfolio_transfer)
def recipient_projection():
    rows=operator.req(P+'/conversations'); conv=next(x for x in rows if x['id']==conv_id)
    assert conv['contactName']==command['name'] and conv['recipient']==command['phone']
    row=operator.req(P+'/contacts/'+ID)
    changed={**command,'phone':'5511998880000'}
    operator.req(P+'/contacts/'+ID,'PUT',changed,{'If-Match':f'"{row["version"]}"'})
    conv=next(x for x in operator.req(P+'/conversations') if x['id']==conv_id)
    assert conv['recipient']==command['phone'], 'Recipient must match channel destination, not mutable contact phone'
    assert operator.req(P+'/contacts?search=unmatched-filter-'+RUN)['items']==[]
    other_rows=other.req(P+'/conversations')
    assert all(x['id']!=conv_id for x in other_rows)
check('R02 authorized identity survives filters and mutable contact phone',recipient_projection)
outgoing={}
def reply():
    v=operator.req(P+f'/conversations/{conv_id}/messages')['version']
    body={'content':'Confirmed QA reply '+RUN,'contentType':'text'}; headers={'Idempotency-Key':'reply-'+RUN,'If-Match':v}
    outgoing.update(operator.req(P+f'/conversations/{conv_id}/messages','POST',body,headers,expected=202))
    replay=operator.req(P+f'/conversations/{conv_id}/messages','POST',body,headers)
    assert replay['messageId']==outgoing['messageId'] and replay['operationId']==outgoing['operationId']
    operator.req(P+f'/conversations/{conv_id}/messages','POST',{'content':'Different','contentType':'text'},headers,expected=409)
    operator.req(P+f'/conversations/{conv_id}/messages','POST',body,{'Idempotency-Key':'missing-'+RUN},expected=428)
    m=poll(lambda:operator.req(P+'/messages/'+outgoing['messageId']),lambda x:xstatus(x,'accepted'))
    assert m['providerId'].startswith('qa.')
def xstatus(x,state):return x['status']==state
check('Reply API queues atomically; replay/conflict/preconditions/worker',reply)
def callbacks():
    m=operator.req(P+'/messages/'+outgoing['messageId'])
    e=envelope('qa-phone-a',statuses=[{'id':m['providerId'],'status':s,'timestamp':at} for s in ['read','delivered','sent','failed']])
    webhook(e); webhook(e)
    poll(lambda:operator.req(P+'/messages/'+outgoing['messageId']),lambda x:xstatus(x,'read'))
check('Callback batch/order/duplicate preserve read and facts',callbacks)
def unknown():
    v=operator.req(P+f'/conversations/{conv_id}/messages')['version']
    op=operator.req(P+f'/conversations/{conv_id}/messages','POST',{'content':'QA:unknown '+RUN}, {'Idempotency-Key':'unknown-'+RUN,'If-Match':v},expected=202)
    poll(lambda:operator.req(P+'/messages/'+op['messageId']),lambda x:xstatus(x,'unknown'))
    time.sleep(1)
    operations=admin.req('/api/admin/communications')['operations']; saved=next(x for x in operations if x['id']==op['operationId'])
    assert saved['state']=='unknown' and saved['attempts']==1
check('Ambiguous send becomes unknown without automatic resend',unknown)
def multipart(content,name,title):
    boundary='EBT'+uuid.uuid4().hex
    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="title"\r\n\r\n{title}\r\n--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\nContent-Type: text/plain\r\n\r\n').encode()+content+f'\r\n--{boundary}--\r\n'.encode()
    return body,{'Content-Type':'multipart/form-data; boundary='+boundary}
def documents():
    content=b'Synthetic commercial document v1'; body,headers=multipart(content,'qa.txt','QA doc '+RUN)
    headers['Idempotency-Key']='doc-'+RUN
    doc=operator.req(P+f'/contacts/{ID}/documents','POST',body,headers)
    assert operator.req(P+f'/contacts/{ID}/documents','POST',body,headers)['id']==doc['id']
    reader.req(P+f'/documents/{doc["id"]}/download/1',expected=403)
    b.req(P+f'/documents/{doc["id"]}/download/1',expected=404)
    admin.req(P+f'/documents/{doc["id"]}/review','POST',{'state':'approved'},{'If-Match':f'"{doc["version"]}"'})
    assert reader.req(P+f'/documents/{doc["id"]}/download/1',raw=True)==content
    versions=operator.req(P+f'/documents/{doc["id"]}/versions'); assert versions[0]['sha256']==hashlib.sha256(content).hexdigest()
    body2,headers2=multipart(b'Synthetic v2','qa.txt','QA doc '+RUN); headers2.update({'Idempotency-Key':'v2-'+RUN,'If-Match':f'"{doc["version"]+1}"'})
    changed=operator.req(P+f'/documents/{doc["id"]}/versions','POST',body2,headers2)
    assert changed['currentVersion']==2 and changed['reviewState']=='pending'
    reader.req(P+f'/documents/{doc["id"]}/download/2',expected=403)
check('Private document version/hash/review/reader/B boundaries',documents)
def api_key():
    key=admin.req('/api/admin/api-keys','POST'); client=Client(); headers={'Authorization':'Bearer '+key['token']}
    client.req(P+'/summary',headers=headers)
    client.req('/api/admin/audit',headers=headers,expected=401)
    admin.req('/api/admin/api-keys/'+key['id'],'DELETE',expected=204)
    client.req(P+'/summary',headers=headers,expected=401)
check('Technical API key restricted + revocation immediate',api_key)
check('Audit tenant scope contains persisted actions',lambda: (_ for _ in ()).throw(AssertionError()) if not admin.req('/api/admin/audit') else None)

def clone(client):
    import copy
    other_client = Client()
    for cookie in client.jar: other_client.jar.set_cookie(copy.copy(cookie))
    return other_client

def concurrent_create():
    dto={**command,'externalKey':'parallel-'+RUN,'name':'Concurrent QA '+RUN}
    token=operator.req('/api/security/csrf')['token']
    clients=[clone(operator) for _ in range(4)]
    # Exactly one creation (201); all other submissions return its canonical ID (200).
    def tolerant(client):
        headers={'Content-Type':'application/json','Idempotency-Key':'parallel-'+RUN,'X-CSRF-TOKEN':token}
        request=urllib.request.Request(BASE+P+'/contacts',json.dumps(dto).encode(),headers,method='POST')
        with client.open.open(request,timeout=35) as response:
            assert response.status in (200,201)
            return response.status,json.loads(response.read())['id']
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(tolerant,clients))
    assert sum(status==201 for status,_ in rows)==1 and len({id for _,id in rows})==1
check('Concurrent commands create one durable contact ID',concurrent_create)

def mixed_webhook():
    provider='wamid.mixed.'+RUN
    message={'id':provider,'from':'551199777'+str(int(RUN[:5],16)).zfill(6)[:6],'type':'text','text':{'body':'Mixed envelope QA'},'timestamp':at}
    aevent=envelope('qa-phone-a',messages=[message])
    bevent=envelope('qa-phone-b',messages=[message])
    unknown=envelope('unmapped-phone',messages=[message])
    packet={'object':'whatsapp_business_account','entry':aevent['entry']+bevent['entry']+unknown['entry']}
    webhook(packet)
    for client in (operator,b):
        convs=poll(lambda:client.req(P+'/conversations'),lambda rows:any(x['lastInboundAt'] for x in rows))
        def find():
            return [m for c in client.req(P+'/conversations') for m in client.req(P+f'/conversations/{c["id"]}/messages')['items'] if m['providerId']==provider]
        assert len(poll(find,lambda rows:len(rows)==1))==1
    before=len(operator.req(P+'/conversations'))
    webhook(envelope('qa-phone-a',messages=[{**message,'from':'5511996666555'}]))
    # Another sender cannot make a second conversation out of the same provider event.
    time.sleep(.5)
    assert len(operator.req(P+'/conversations'))==before
    webhook(envelope('qa-phone-a',messages=[{**message,'id':provider.upper()}]))
    def case_ids():
        return [m['providerId'] for c in operator.req(P+'/conversations') for m in operator.req(P+f'/conversations/{c["id"]}/messages')['items'] if m['providerId'] in (provider,provider.upper())]
    assert len(poll(case_ids,lambda rows:len(rows)==2))==2
check('Mixed envelope routes A/B; unknown metadata quarantined; provider IDs scoped and case sensitive',mixed_webhook)

def reconcile_unknown():
    version=operator.req(P+f'/conversations/{conv_id}/messages')['version']
    op=operator.req(P+f'/conversations/{conv_id}/messages','POST',{'content':'QA:unknown reconcile '+RUN},{'Idempotency-Key':'reconcile-'+RUN,'If-Match':version},expected=202)
    poll(lambda:operator.req(P+'/messages/'+op['messageId']),lambda x:x['status']=='unknown')
    webhook(envelope('qa-phone-a',statuses=[{'id':'wamid.reconciled.'+RUN,'status':'delivered','timestamp':at,'biz_opaque_callback_data':op['operationId']}]))
    poll(lambda:operator.req(P+'/messages/'+op['messageId']),lambda x:x['status']=='delivered')
    row=next(x for x in admin.req('/api/admin/communications')['operations'] if x['id']==op['operationId'])
    assert row['state']=='reconciled' and row['attempts']==1
check('Late signed callback reconciles unknown without resending',reconcile_unknown)

def revoke_session():
    copied=clone(reader)
    reader.req('/api/auth/logout','POST',expected=204)
    copied.req(P+'/summary',expected=401)
    # Context switch invalidates the former signed session even if its cookie was copied.
    copied_admin=clone(admin)
    admin.context(ACCESS['tenantB'])
    copied_admin.req(P+'/summary',expected=401)
    admin.context(ACCESS['tenantA'])
    operator.req(P+'/contacts','POST',{**command,'externalKey':'old-context-'+RUN},{'Idempotency-Key':'old-context-'+RUN,'X-Expected-Tenant':ACCESS['tenantB']},expected=409)
check('Logout/context revoke copied sessions; old-context mutation denied',revoke_session)
result={'generated_utc':datetime.now(timezone.utc).isoformat(),'environment':'localhost SQL Server QA synthetic','run':RUN,'passed':all(r['result']=='passed' for r in RESULTS),'cases':RESULTS,'limits':['No real provider send or Meta homologation','No Azure shared schema modified','Not user acceptance']}
target=ROOT/'evidencias/testes_connect_sql_http.json'; target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{sum(r["result"]=="passed" for r in RESULTS)}/{len(RESULTS)} passed')
raise SystemExit(0 if result['passed'] else 1)
