"""Signed WazVox ingress on an isolated localhost SQL fixture. No provider send."""
import hashlib, hmac, json, time, uuid, urllib.request, urllib.error, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
CONFIG=json.loads((ROOT/'tmp/runtime/wazvox-qa-config.json').read_text(encoding='utf-8-sig'))
ACCESS=json.loads((ROOT/'tmp/runtime/qa-access.json').read_text(encoding='utf-8-sig'))
if CONFIG['ConnectionStrings']['Platform']!='Server=localhost;Database=EbtPlatformQa_20261007Migrated;Integrated Security=True;Encrypt=True;TrustServerCertificate=True': raise RuntimeError('Only exact local synthetic QA fixture')
BASE='http://127.0.0.1:5186'; RUN=uuid.uuid4().hex; RESULTS=[]
def sql(query):
 r=subprocess.run(['sqlcmd','-S','localhost','-E','-C','-b','-d','EbtPlatformQa_20261007Migrated','-h','-1','-W','-Q',"SET NOCOUNT ON; EXEC sp_set_session_context @key=N'ebt_system',@value=1; "+query],capture_output=True,encoding='utf-8',errors='replace',check=True)
 return r.stdout.strip()
def event(event_id=None,phone='wz-qa-A',workspace='workspace-qa'):
 return {'eventId':event_id or 'wzevt_'+uuid.uuid4().hex,'version':'1','tenantId':workspace,'type':'message.received','occurredAt':datetime.now(timezone.utc).isoformat(),'wabaId':'wz-qa-account','phoneNumberId':phone,'data':{'from':'5511998877665','message':{'id':'wamid.'+RUN,'type':'text','text':{'body':'QA WazVox synthetic '+RUN}}}}
def post(e,expected=200,timestamp=None,signature=True,header_id=None):
 body=json.dumps(e,separators=(',',':')).encode(); t=timestamp or str(int(time.time())); secret=CONFIG['WazVox']['Apps']['wz-qa']['SigningSecret']
 signature_value=hmac.new(secret.encode(),t.encode()+b'.'+body,hashlib.sha256).hexdigest() if signature else '0'*64
 req=urllib.request.Request(BASE+'/webhooks/connect/wazvox/wz-qa',data=body,headers={'Content-Type':'application/json','X-BSP-Timestamp':t,'X-BSP-Event-Id':header_id or e['eventId'],'X-BSP-Signature':'sha256='+signature_value},method='POST')
 try:r=urllib.request.urlopen(req,timeout=30)
 except urllib.error.HTTPError as ex:r=ex
 result=r.read()
 if r.status!=expected:raise AssertionError(f'expected {expected}, got {r.status}: {result[:120]!r}')
def check(name,fn):
 try:fn();RESULTS.append({'name':name,'passed':True});print('PASS',name,flush=True)
 except Exception as ex:RESULTS.append({'name':name,'passed':False,'error':str(ex)});print('FAIL',name,str(ex),flush=True)
def wait(query,value='1'):
 for _ in range(40):
  if sql(query)==value:return
  time.sleep(.25)
 raise AssertionError('Expected durable worker state not observed')
e=event(); receipt_query=f"SELECT COUNT(*) FROM ebt_connect.Receipts WHERE AppKey='wz-qa' AND ProviderEventId='{e['eventId']}'"
check('Invalid signature creates no receipt',lambda:(post(e,401,signature=False),wait(receipt_query,'0')))
check('Expired signature creates no receipt',lambda:(post(e,401,timestamp=str(int(time.time())-301)),wait(receipt_query,'0')))
check('Workspace spoof rejected before durable ACK',lambda:post(event(workspace='other-workspace'),400))
check('Event header mismatch rejected',lambda:post(e,400,header_id='wrong'))
check('Durable ACK and identical event replay',lambda:(post(e),post(e),wait(receipt_query)))
changed=json.loads(json.dumps(e));changed['data']['message']['text']['body']='different signed text'
check('Same event ID with changed body rejected',lambda:post(changed,409))
check('Canonical inbound processed once',lambda:wait(f"SELECT COUNT(*) FROM ebt_connect.Messages WHERE ProviderId='wamid.{RUN}' AND ConnectionId IN (SELECT Id FROM ebt_connect.Connections WHERE AppKey='wz-qa' AND PhoneNumberId='wz-qa-A')"))
b=event(phone='wz-qa-B');b['data']['message']['id']='wamid.B.'+RUN
check('Same workspace number B routes only to tenant B',lambda:(post(b),wait(f"SELECT COUNT(*) FROM ebt_connect.Messages m JOIN ebt_connect.Connections c ON m.TenantId=c.TenantId AND m.ConnectionId=c.Id WHERE m.ProviderId='wamid.B.{RUN}' AND c.PhoneNumberId='wz-qa-B' AND m.TenantId='{uuid.UUID(ACCESS['tenantB'])}'"),wait(f"SELECT COUNT(*) FROM ebt_connect.Messages WHERE ProviderId='wamid.B.{RUN}' AND TenantId='{uuid.UUID(ACCESS['tenantA'])}'",'0')))
unknown=event(phone='not-configured');unknown['data']['message']['id']='wamid.unknown.'+RUN
check('Unknown number quarantined without contact creation',lambda:(post(unknown),wait(f"SELECT COUNT(*) FROM ebt_connect.Receipts WHERE ProviderEventId='{unknown['eventId']}' AND State='quarantined' AND Diagnostic='unknown_connection'"),wait(f"SELECT COUNT(*) FROM ebt_connect.Messages WHERE ProviderId='wamid.unknown.{RUN}'",'0')))
unsupported=event();unsupported['type']='message.sent'
check('Business App mirror cannot open incoming service window',lambda:(post(unsupported),wait(f"SELECT COUNT(*) FROM ebt_connect.Receipts WHERE ProviderEventId='{unsupported['eventId']}' AND State='quarantined' AND Diagnostic='unsupported_wazvox_event'")))
status=event();status['type']='message.status';status['data']={'waMessageId':'wamid.orphan.'+RUN,'status':'read','to':'5511998877665'}
check('Status callback persisted with WhatsApp reference',lambda:(post(status),wait(f"SELECT COUNT(*) FROM ebt_connect.DeliveryEvents WHERE ProviderId='wamid.orphan.{RUN}' AND Status='read'")))
report={'generatedUtc':datetime.now(timezone.utc).isoformat(),'environment':'localhost synthetic SQL; no external send','passed':all(x['passed'] for x in RESULTS),'cases':len(RESULTS),'results':RESULTS,'limits':['Status payload is a strict candidate mapping; real callback remains pending','No real key is loaded by the QA API']}
(ROOT/'evidencias/testes_wazvox_sql_http.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if not report['passed']:raise SystemExit(1)
