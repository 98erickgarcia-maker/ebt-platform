"""Synthetic localhost SQL/HTTP regression. Never calls Microsoft or sends email."""
import concurrent.futures, copy, http.cookiejar, json, os, re, subprocess, time, urllib.error, urllib.request, uuid
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
ACCESS = json.loads((ROOT/'tmp/runtime/qa-access.json').read_text(encoding='utf-8-sig'))
DB = next(x.split('=',1)[1] for x in CONFIG['ConnectionStrings']['Platform'].split(';') if x.lower().startswith('database='))
assert DB.startswith('EbtPlatformQa_') and 'Server=localhost;' in CONFIG['ConnectionStrings']['Platform']
BASE = 'http://127.0.0.1:5186'; P = '/api/connect/v1'; M = P+'/mail'; RUN = uuid.uuid4().hex[:10]; CASES=[]
class Client:
    def __init__(self):
        self.jar=http.cookiejar.CookieJar(); self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
    def req(self,path,method='GET',body=None,expected=200,headers=None,raw=False):
        headers=dict(headers or {})
        if method!='GET': headers['X-CSRF-TOKEN']=self.req('/api/security/csrf')['token']
        data=json.dumps(body).encode() if body is not None else None
        if data is not None: headers['Content-Type']='application/json'
        try: r=self.opener.open(urllib.request.Request(BASE+path,data,headers,method=method),timeout=40)
        except urllib.error.HTTPError as e: r=e
        content=r.read(); assert r.status==expected,(method,path,r.status,content[:350])
        return content if raw else json.loads(content) if content else None
    def login(self,email,tenant):
        self.req('/api/auth/login','POST',{'email':email,'password':ACCESS['password']}); self.req('/api/auth/context/'+tenant,'POST',expected=204); return self
    def clone(self):
        c=Client()
        for cookie in self.jar: c.jar.set_cookie(copy.copy(cookie))
        return c
def sql(statement):
    if os.environ.get('GITHUB_ACTIONS')=='true':
        run=os.environ.get('GITHUB_RUN_ID',''); container=os.environ.get('EBT_QA_SQL_CONTAINER',''); password=os.environ.get('EBT_SQL_PASSWORD','')
        assert run.isdigit() and DB=='EbtPlatformQa_Ci_'+run and re.fullmatch(r'[a-f0-9]{12,64}',container) and password=='EbtQa_'+run+'!X'
        args=['docker','exec','-i','-e','SQLCMDPASSWORD',container,'/opt/mssql-tools18/bin/sqlcmd','-S','localhost','-U','sa','-C','-b','-h','-1','-W','-d',DB]
        r=subprocess.run(args,input=statement,capture_output=True,text=True,env={**os.environ,'SQLCMDPASSWORD':password},timeout=40)
    else:
        assert 'Integrated Security=True' in CONFIG['ConnectionStrings']['Platform']
        r=subprocess.run(['sqlcmd','-S','localhost','-d',DB,'-E','-C','-b','-h','-1','-W','-Q',statement],capture_output=True,text=True,timeout=40)
    assert r.returncode==0,'Synthetic SQL command failed; private output omitted'; return r.stdout.strip()
def check(name,work):
    try: work(); CASES.append({'case':name,'result':'passed'}); print('PASS',name,flush=True)
    except Exception as e: CASES.append({'case':name,'result':'failed','error':str(e)}); print('FAIL',name,str(e),flush=True)
def h(row,key=None): return {'If-Match':f'"{row["version"]}"',**({'Idempotency-Key':key} if key else {})}
admin=Client().login('admin@ebt.example',ACCESS['tenantA']); operator=Client().login('operador@ebt.example',ACCESS['tenantA']); reader=Client().login('consulta@ebt.example',ACCESS['tenantA']); other=Client().login('outra@ebt.example',ACCESS['tenantA']); b=Client().login('admin@ebt.example',ACCESS['tenantB'])
contact=operator.req(P+'/contacts','POST',{'name':'Mail QA '+RUN,'email':RUN+'@client.example'},expected=201,headers={'Idempotency-Key':'mail-contact-'+RUN})
command={'contactId':contact['id'],'subject':'QA assunto '+RUN,'body':'Texto próprio\nsegunda linha'}
draft=operator.req(M+'/drafts','POST',command,headers={'Idempotency-Key':'draft-'+RUN})
def creation():
    assert operator.req(M+'/drafts','POST',command,headers={'Idempotency-Key':'draft-'+RUN})['id']==draft['id']
    operator.req(M+'/drafts','POST',{**command,'subject':'changed'},expected=409,headers={'Idempotency-Key':'draft-'+RUN})
    assert operator.req(M+'/drafts/'+draft['id'])['body']==command['body']
check('Draft persisted, replay stable, changed payload rejected',creation)
def isolation():
    for c in [other,b]:
        for suffix in ['', '/history', '/eml']: c.req(M+'/drafts/'+draft['id']+suffix,expected=404)
        assert not any(x['id']==draft['id'] for x in c.req(M+'/drafts')['items'])
    reader.req(M+'/drafts','POST',command,expected=403,headers={'Idempotency-Key':'reader-'+RUN})
    operator.req(M+'/drafts','POST',{**command,'tenantId':ACCESS['tenantB']},expected=400,headers={'Idempotency-Key':'inject-'+RUN})
check('A/B, portfolio, reader and tenant injection negative tests',isolation)
def workflow():
    operator.req(M+'/drafts/'+draft['id']+'/action','POST',{'action':'approve'},expected=403,headers=h(draft,'operator-approve-'+RUN))
    approved=admin.req(M+'/drafts/'+draft['id']+'/action','POST',{'action':'approve'},headers=h(draft,'approve-'+RUN))
    assert approved['state']=='approved'
    assert admin.req(M+'/drafts/'+draft['id']+'/action','POST',{'action':'approve'},headers=h(draft,'approve-'+RUN))['version']==approved['version']
    operator.req(M+'/drafts/'+draft['id']+'/action','POST',{'action':'queue'},expected=409,headers=h(approved,'queue-'+RUN))
    operator.req(M+'/drafts/'+draft['id'],'PUT',command,expected=409,headers=h(draft))
    edited=operator.req(M+'/drafts/'+draft['id'],'PUT',{**command,'body':'Revisto'},headers=h(approved))
    assert edited['state']=='draft' and edited['approvedAt'] is None
    operator.req(M+'/drafts/'+draft['id']+'/action','POST',{'action':'simulate'},expected=400,headers=h(edited,'forbidden-simulation-'+RUN))
    assert operator.req(M+'/drafts/'+draft['id'])['state']=='draft'
check('Approval requires admin; replay; edit invalidates; simulation removed; real connection gate',workflow)
def concurrent_edit():
    row=operator.req(M+'/drafts/'+draft['id'])
    def attempt(n):
        c=operator.clone()
        try: c.req(M+'/drafts/'+row['id'],'PUT',{**command,'body':'concorrente '+str(n)},headers=h(row)); return 200
        except AssertionError as e:
            assert e.args[0][2]==409; return 409
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: assert sorted(pool.map(attempt,[1,2]))==[200,409]
check('Concurrent edits preserve first commit',concurrent_edit)
template_command={'name':'Modelo QA '+RUN,'subject':'Olá {nome}','body':'Empresa {empresa}; e-mail {email}'}
template=operator.req(M+'/templates','POST',template_command,headers={'Idempotency-Key':'template-'+RUN})
def templates_batch():
    assert operator.req(M+'/templates','POST',template_command,headers={'Idempotency-Key':'template-'+RUN})['id']==template['id']
    for c in [b,other]: c.req(M+'/templates/'+template['id'],'PUT',template_command,expected=404,headers=h(template))
    operator.req(M+'/templates','POST',{**template_command,'body':'{token}'},expected=400,headers={'Idempotency-Key':'invalid-template-'+RUN})
    batch={'templateId':template['id'],'contactIds':[contact['id']]}
    rows=operator.req(M+'/batch','POST',batch,headers={'Idempotency-Key':'batch-'+RUN}); saved=rows[0]['body']; assert contact['email'] in saved and '{email}' not in saved
    operator.req(M+'/templates/'+template['id'],'PUT',{**template_command,'body':'Novo texto'},headers=h(template))
    again=operator.req(M+'/batch','POST',batch,headers={'Idempotency-Key':'batch-'+RUN}); assert again[0]['id']==rows[0]['id'] and again[0]['body']==saved
    duplicate=operator.req(P+'/contacts','POST',{'name':'Duplicado QA '+RUN,'email':contact['email']},expected=201,headers={'Idempotency-Key':'dup-mail-'+RUN})
    total=operator.req(M+'/drafts')['total']
    operator.req(M+'/batch','POST',{'templateId':template['id'],'contactIds':[contact['id'],duplicate['id']]},expected=400,headers={'Idempotency-Key':'bad-batch-'+RUN})
    assert operator.req(M+'/drafts')['total']==total
check('Local personalization, version snapshot, batch replay and atomic duplicate rejection',templates_batch)
def suppression_settings():
    admin.req(M+'/suppression','POST',{'value':contact['email'],'reason':'QA opt-out'})
    row=operator.req(M+'/drafts/'+draft['id'])
    admin.req(M+'/drafts/'+draft['id']+'/action','POST',{'action':'approve'},expected=409,headers=h(row,'blocked-'+RUN))
    operator.req(M+'/suppression',expected=403)
    reader.req(M+'/settings','PUT',{'intervalSeconds':3,'dailyCap':100,'paused':True},expected=403,headers={'If-Match':'"0"'})
    status=admin.req(M+'/status')
    admin.req(M+'/settings','PUT',{'intervalSeconds':0,'dailyCap':100,'paused':True},expected=400,headers={'If-Match':f'"{status["version"]}"'})
    admin.req(M+'/settings','PUT',{'intervalSeconds':3,'dailyCap':100,'paused':False},expected=409,headers={'If-Match':f'"{status["version"]}"'})
    admin.req(M+'/settings','PUT',{'intervalSeconds':5,'dailyCap':77,'paused':True},headers={'If-Match':f'"{status["version"]}"'})
    assert admin.req(M+'/status')['dailyCap']==77
check('Opt-out checked on approval; admin-only controls; persisted limits; unconfigured real queue blocked',suppression_settings)
def recovery():
    id=str(uuid.UUID(draft['id']))
    sql(f"EXEC sys.sp_set_session_context @key=N'ebt_system',@value=1; UPDATE ebt_connect.MailDrafts SET State='processing',AttemptedAt=DATEADD(minute,-3,SYSDATETIMEOFFSET()),Version=Version+1 WHERE Id='{id}';")
    for _ in range(30):
        row=admin.req(M+'/drafts/'+id)
        if row['state']=='unknown': break
        time.sleep(.3)
    assert row['state']=='unknown' and row['diagnostic']=='worker_restart_uncertain'
    admin.req(M+'/drafts/'+id+'/action','POST',{'action':'queue'},expected=409,headers=h(row,'retry-unknown-'+RUN))
    admin.req(M+'/drafts/'+id+'/action','POST',{'action':'reconcile'},expected=400,headers=h(row,'empty-reconcile-'+RUN))
    done=admin.req(M+'/drafts/'+id+'/action','POST',{'action':'reconcile','reason':'QA synthetic mailbox checked'},headers=h(row,'reconcile-'+RUN)); assert done['state']=='reconciled'
    history=admin.req(M+'/drafts/'+id+'/history'); assert history['total']>=5
check('Crash recovery uncertain, no automatic resend, evidence required and immutable history',recovery)
def raw_rls():
    sql("IF USER_ID('EbtConnectQaRuntime') IS NULL CREATE USER EbtConnectQaRuntime WITHOUT LOGIN; GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::ebt_connect TO EbtConnectQaRuntime;")
    sql("EXECUTE AS USER='EbtConnectQaRuntime'; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value=NULL; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; IF EXISTS(SELECT 1 FROM ebt_connect.MailDrafts) OR EXISTS(SELECT 1 FROM ebt_connect.MailRevisions) THROW 51031,'Contextless mail leak',1; REVERT;")
    assert sql("SELECT COUNT(*) FROM sys.security_predicates WHERE object_id=OBJECT_ID('ebt_connect.tenant_barrier') AND target_object_id IN (OBJECT_ID('ebt_connect.MailDrafts'),OBJECT_ID('ebt_connect.MailRevisions'),OBJECT_ID('ebt_connect.MailSettings'),OBJECT_ID('ebt_connect.MailQuotas'),OBJECT_ID('ebt_connect.MailSuppressions'),OBJECT_ID('ebt_connect.MailTemplates')); ").splitlines()[0]=='30'
    a=str(uuid.UUID(ACCESS['tenantA'])); tenantb=str(uuid.UUID(ACCESS['tenantB']))
    sql(f"DECLARE @a uniqueidentifier='{a}', @blocked bit=0; EXECUTE AS USER='EbtConnectQaRuntime'; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value=@a; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; IF EXISTS(SELECT 1 FROM ebt_connect.MailDrafts WHERE TenantId='{tenantb}') THROW 51032,'B leak',1; BEGIN TRY INSERT ebt_connect.MailQuotas(Id,TenantId,Version,Day,Used) VALUES(NEWID(),'{tenantb}',1,'2099-01-01',1); END TRY BEGIN CATCH IF ERROR_NUMBER()=33504 SET @blocked=1; ELSE THROW; END CATCH; REVERT; IF @blocked=0 THROW 51033,'Cross write allowed',1;")
check('SQL RLS 30 predicates, contextless read and cross-tenant write rejection',raw_rls)
def search_export():
    q=urllib.parse.quote('Mail QA '+RUN); assert any(x['contactId']==contact['id'] for x in operator.req(P+'/search?search='+q)); assert not other.req(P+'/search?search='+q)
    assert len(operator.req(P+'/contacts/duplicates?email='+urllib.parse.quote(contact['email'])))==2
    eml=operator.req(M+'/drafts/'+draft['id']+'/eml',raw=True); assert b'X-Unsent: 1' in eml and b'Content-Transfer-Encoding: base64' in eml
    assert operator.req(M+'/drafts?limit=1')['total']>=2
check('Scoped search, duplicate hints, EML draft export and pagination totals',search_export)
def complete_lists():
    a=str(uuid.UUID(ACCESS['tenantA'])); cid=str(uuid.UUID(contact['id'])); owner=str(uuid.UUID(ACCESS['users']['operador@ebt.example']))
    sql(f"EXEC sys.sp_set_session_context @key=N'ebt_system',@value=1; DECLARE @i int=0; WHILE @i<106 BEGIN INSERT ebt_connect.Tasks(Id,TenantId,Version,ContactId,OwnerId,Title,DueAt,State,Result,CloseKey,CloseHash,OperationKey,PayloadHash) VALUES(NEWID(),'{a}',1,'{cid}','{owner}','Synthetic page '+CONVERT(varchar,@i),DATEADD(day,@i,SYSDATETIMEOFFSET()),'open','','','', 'qa-page-{RUN}-'+CONVERT(varchar,@i),''); INSERT ebt_connect.Interactions(Id,TenantId,Version,ContactId,ActorId,Kind,Content,OccurredAt,RecordedAt,OperationKey,PayloadHash) VALUES(NEWID(),'{a}',1,'{cid}','{owner}','note','Synthetic page '+CONVERT(varchar,@i),SYSDATETIMEOFFSET(),SYSDATETIMEOFFSET(),'qa-page-{RUN}-'+CONVERT(varchar,@i),''); INSERT ebt_connect.Organizations(Id,TenantId,Version,Name,ExternalKey,Portfolio) VALUES(NEWID(),'{a}',1,'zz page {RUN} '+CONVERT(varchar,@i),'qa-page-{RUN}-'+CONVERT(varchar,@i),'principal'); SET @i=@i+1; END;")
    for suffix in ['/tasks?contactId='+cid+'&', '/contacts/'+cid+'/history?']:
        ids=[]; index=1
        while True:
            result=operator.req(P+suffix+'paged=true&limit=25&page='+str(index));ids.extend(x['id'] for x in result['items'])
            if len(ids)>=result['total']:break
            index+=1
        assert len(ids)==result['total'] and len(ids)==len(set(ids)) and len(ids)>=106
        b.req(P+suffix+'paged=true',expected=404)
    org=operator.req(P+'/organizations?paged=true&search='+urllib.parse.quote('zz page '+RUN)+'&page=5&limit=25'); assert org['total']==106 and len(org['items'])==6
    last=org['items'][-1]; row=operator.req(P+'/contacts/'+cid)
    updated=operator.req(P+'/contacts/'+cid,'PUT',{'name':row['name'],'email':row['email'],'organizationId':last['id']},headers=h(row)); assert updated['organizationName']==last['name']
    task=operator.req(P+'/tasks?contactId='+cid+'&paged=true&limit=1')['items'][0]
    ics=operator.req(P+'/tasks/'+task['id']+'/calendar.ics',raw=True);assert b'BEGIN:VCALENDAR' in ics and b'DTSTART:' in ics
    b.req(P+'/tasks/'+task['id']+'/calendar.ics',expected=404)
    without=operator.req(P+'/contacts?withoutNextAction=true');summary=operator.req(P+'/summary');assert without['total']==summary['withoutNextAction']
check('106 tasks/history/orgs fully reachable; linked name outside first page; scoped ICS; count reconciled',complete_lists)
def qualification():
    row=operator.req(P+'/contacts/'+contact['id'])
    info={'source':'Indicação sintética','sourceUrl':'https://example.com/source','segment':'Serviços','contactRole':'Compras','need':'Organizar retornos comerciais','preferredChannel':'email','bestTime':'Tarde','decisionMaker':'yes'}
    payload={'name':row['name'],'email':row['email'],'stage':'proposta','organizationId':row['organizationId'],'prospection':info}
    changed=operator.req(P+'/contacts/'+row['id'],'PUT',payload,headers=h(row)); assert changed['prospection']==info and changed['activeSince'] is None
    credential_url=''.join(['https://', 'fixture-user:fixture-secret', '@example.com'])
    operator.req(P+'/contacts/'+row['id'],'PUT',{**payload,'prospection':{**info,'sourceUrl':credential_url}},headers=h(changed),expected=400)
    active=operator.req(P+'/contacts/'+row['id'],'PUT',{**payload,'stage':'ganho'},headers=h(changed)); assert active['id']==row['id'] and active['activeSince'] and active['prospection']==info
    legacy=operator.req(P+'/contacts/'+row['id'],'PUT',{'name':row['name'],'email':row['email'],'stage':'ganho','organizationId':row['organizationId']},headers=h(active)); assert legacy['prospection']==info and legacy['activeSince']==active['activeSince']
    b.req(P+'/contacts/'+row['id'],expected=404); reader.req(P+'/contacts/'+row['id'],'PUT',payload,headers=h(legacy),expected=403)
check('Qualification persistence, URL rejection, same-ID sale conversion and legacy PUT preservation',qualification)
def templates_context():
    command={'name':'Context '+RUN,'subject':'Retorno {nome}','body':'Olá {nome}. Cargo: {cargo}. Necessidade: {necessidade}.','channel':'email','purpose':'followup'}
    t=operator.req(M+'/templates','POST',command,headers={'Idempotency-Key':'context-template-'+RUN})
    preview=operator.req(M+'/templates/'+t['id']+'/preview?contactId='+contact['id']); assert 'Compras' in preview['body'] and 'Organizar retornos comerciais' in preview['body'] and '{nome}' not in preview['body']
    b.req(M+'/templates/'+t['id']+'/preview?contactId='+contact['id'],expected=404); other.req(M+'/templates/'+t['id']+'/preview?contactId='+contact['id'],expected=404)
    d=operator.req(M+'/drafts','POST',{'contactId':contact['id'],'subject':preview['subject'],'body':preview['body'],'templateId':t['id'],'templateVersion':t['version']},headers={'Idempotency-Key':'context-draft-'+RUN}); assert d['origin'].endswith(':v1')
    changed=operator.req(M+'/templates/'+t['id'],'PUT',{**command,'body':'Modelo alterado'},headers=h(t))
    assert operator.req(M+'/drafts/'+d['id'])['body']==preview['body']
    operator.req(M+'/drafts','POST',{'contactId':contact['id'],'subject':preview['subject'],'body':preview['body'],'templateId':t['id'],'templateVersion':t['version']},headers={'Idempotency-Key':'context-stale-'+RUN},expected=409)
    whats=operator.req(M+'/templates','POST',{**command,'channel':'whatsapp','purpose':'relationship'},headers={'Idempotency-Key':'whats-template-'+RUN})
    assert operator.req(M+'/templates/'+whats['id']+'/preview?contactId='+contact['id'])['channel']=='whatsapp'
    operator.req(M+'/batch','POST',{'templateId':whats['id'],'contactIds':[contact['id']]},headers={'Idempotency-Key':'whats-mail-block-'+RUN},expected=409)
check('Shared channel templates, personalized preview, snapshot preserved and stale model/tenant rejected',templates_context)
report={'generated_utc':datetime.now(timezone.utc).isoformat(),'environment':DB,'synthetic_only':True,'real_email_sent':False,'passed':all(c['result']=='passed' for c in CASES),'cases':CASES}
(ROOT/'evidencias/mail_connect_qa_20261009.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raise SystemExit(0 if report['passed'] else 1)
