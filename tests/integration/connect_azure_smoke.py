"""Live deployment checks against isolated synthetic tenants; never sends messages."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,requests,uuid,hmac,hashlib
root=Path.cwd();url='https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io';results=[]
qa=json.loads((root/'tmp/private-integrations/connect-live-qa.json').read_text());cfg=json.loads((root/'tmp/private-integrations/connect-production.json').read_text(encoding='utf-8-sig'))
s=requests.Session();csrf=''
def check(name,condition):
 results.append({'name':name,'passed':bool(condition)});print(('PASS ' if condition else 'FAIL ')+name)
 if not condition:raise RuntimeError(name)
def req(method,path,**kw):
 h=kw.pop('headers',{});h['X-CSRF-TOKEN']=csrf
 return s.request(method,url+path,headers=h,timeout=35,allow_redirects=False,**kw)
def token():
 global csrf
 r=s.get(url+'/api/security/csrf',timeout=35);r.raise_for_status();csrf=r.json()['token']
try:
 for p in ['/health/live','/health/ready','/']:
  r=requests.get(url+p,timeout=35,allow_redirects=False);check('Public '+p,r.status_code==200 and bool(r.headers.get('Strict-Transport-Security')))
 check('HTTP upgrades to HTTPS',requests.get(url.replace('https:','http:')+'/',timeout=20,allow_redirects=False).status_code in (301,302,307,308))
 check('Anonymous CRM denied',requests.get(url+'/api/connect/v1/contacts',timeout=35).status_code==401)
 check('Temporary proxy observation disabled',requests.get(url+'/ops/proxy',headers={'X-EBT-Proxy-Audit':cfg['Platform'].get('ProxyAuditKey','disabled-'+('a'*64))},timeout=25).status_code==404)
 token();r=req('POST','/api/auth/login',json={'email':qa['email'],'password':qa['password']});check('Login and protected session cookie',r.status_code==200 and '__Host-ebt.session=' in r.headers.get('Set-Cookie','') and 'httponly' in r.headers.get('Set-Cookie','').lower() and 'secure' in r.headers.get('Set-Cookie','').lower());token()
 me=req('GET','/api/auth/me');check('Authenticated identity',me.status_code==200 and me.json()['userId']==qa['userId']);current=me.json()['tenantId']
 if current!=qa['tenantA']:
  check('Select synthetic tenant A',req('POST','/api/auth/context/'+qa['tenantA']).status_code==204);token()
 fixture='live-'+uuid.uuid4().hex
 body={'name':'VALIDACAO TECNICA - sem cliente real','externalKey':fixture,'portfolio':'QA','stage':'novo'}
 r=req('POST','/api/connect/v1/contacts',json=body,headers={'Idempotency-Key':fixture});check('Contact persisted through live API',r.status_code==201);contact=r.json();cid=contact['id']
 r=req('POST','/api/connect/v1/contacts',json=body,headers={'Idempotency-Key':fixture});check('Contact creation replay keeps one ID',r.status_code==200 and r.json()['id']==cid)
 missing=s.post(url+'/api/connect/v1/contacts',json=body,headers={'Idempotency-Key':fixture+'csrf'},timeout=30);check('Missing CSRF rejected',missing.status_code==400)
 check('Direct contact read',req('GET','/api/connect/v1/contacts/'+cid).status_code==200)
 r=req('POST','/api/connect/v1/contacts/'+cid+'/history',json={'content':'Teste de persistência da primeira entrega ao vivo.'},headers={'Idempotency-Key':fixture+'note'});check('History note saved',r.status_code==200)
 due=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat();r=req('POST','/api/connect/v1/contacts/'+cid+'/tasks',json={'title':'Validação técnica de próxima ação','dueAt':due},headers={'Idempotency-Key':fixture+'task'});check('Task saved',r.status_code==200);task=r.json()
 r=req('GET','/api/connect/v1/contacts/'+cid);check('Next action derived from persistent task',r.status_code==200 and r.json()['nextAction']['id']==task['id'])
 check('Switch to tenant B',req('POST','/api/auth/context/'+qa['tenantB']).status_code==204);token()
 check('Tenant B cannot read A by direct ID',req('GET','/api/connect/v1/contacts/'+cid).status_code==404)
 r=req('GET','/api/connect/v1/contacts');check('Tenant B listing excludes A',r.status_code==200 and not any(x['id']==cid for x in r.json()['items']))
 check('Switch back to tenant A',req('POST','/api/auth/context/'+qa['tenantA']).status_code==204);token()
 check('Revisit keeps original contact ID',req('GET','/api/connect/v1/contacts/'+cid).json()['id']==cid)
 event='deployment-qa-'+uuid.uuid4().hex;stamp=str(int(datetime.now(timezone.utc).timestamp()));envelope={'eventId':event,'version':'1','type':'message.received','occurredAt':datetime.now(timezone.utc).isoformat(),'tenantId':'01a11528-b74e-723c-82bc-a9a728af7d71','wabaId':'deployment-qa-unmapped','phoneNumberId':'deployment-qa-unmapped','data':{'from':'5511999988888','message':{'id':'wamid.deployment-qa-'+fixture,'type':'text','text':{'body':'synthetic deployment signature check; no real message'}}}}
 def callback(data,signature=True):
  raw=json.dumps(data,separators=(',',':')).encode();secret=cfg['WazVox']['Apps']['wz-ebt']['SigningSecret'].encode();sig='sha256='+hmac.new(secret,stamp.encode()+b'.'+raw,hashlib.sha256).hexdigest()
  return requests.post(url+'/webhooks/connect/wazvox/wz-ebt',data=raw,headers={'Content-Type':'application/json','X-BSP-Timestamp':stamp,'X-BSP-Event-Id':event,'X-BSP-Signature':sig if signature else 'sha256='+'0'*64},timeout=35)
 check('Unsigned callback rejected',callback(envelope,False).status_code==401)
 check('Signed synthetic callback durably acknowledged',callback(envelope).status_code==200)
 check('Identical callback replay acknowledged',callback(envelope).status_code==200)
 envelope['data']['message']['text']['body']='changed synthetic content';check('Changed duplicate callback rejected',callback(envelope).status_code==409)
 oldcookies=s.cookies.copy();check('Logout revokes live session',req('POST','/api/auth/logout').status_code==204);s.cookies=oldcookies;check('Revoked cookie cannot reopen CRM',req('GET','/api/connect/v1/contacts').status_code==401)
 report={'generatedUtc':datetime.now(timezone.utc).isoformat(),'version':'0.1.3','url':url,'environment':'Azure live / isolated synthetic fixtures','passed':True,'cases':len(results),'results':results,'fixture':{'tenantA':qa['tenantA'],'tenantB':qa['tenantB'],'contactId':cid,'taskId':task['id'],'callbackEventId':event},'realMessagesSent':0,'limits':['Callback signature was generated by the deployment check, not observed from provider delivery','Real inbound, human reply, delivery/read status, scanner, Azure restore and business acceptance remain pending']}
except Exception:
 report={'generatedUtc':datetime.now(timezone.utc).isoformat(),'url':url,'passed':False,'cases':len(results),'results':results};raise
finally:
 (root/'evidencias/connect_primeira_entrega_online.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
