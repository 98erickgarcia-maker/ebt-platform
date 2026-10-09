"""Explicit authorized synthetic live Flow smoke; no credentials or real rows exported."""
import hashlib,json,time,uuid,os
from datetime import datetime,timezone
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[2]
PRIVATE=Path(os.environ.get("EBT_FLOW_QA_ACCESS",r"C:/Users/Ivair Silva/Documents/ChatGPT/EBT PLATAFORM/tmp/private-integrations/connect-live-qa.json"))
BASE="https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io"
P="/api/flow/v1/protocols"
CHECKS=[]
def check(name,condition):
 if not condition:raise AssertionError(name)
 CHECKS.append({"name":name,"passed":True});print("PASS "+name,flush=True)
def call(s,path,method="GET",body=None,headers=None,status=200):
 h=dict(headers or {})
 if method!="GET":
  t=s.get(BASE+"/api/security/csrf",timeout=25);t.raise_for_status();h["X-CSRF-TOKEN"]=t.json()["token"]
 r=s.request(method,BASE+path,json=body,headers=h,timeout=40)
 assert r.status_code==status,f"{method} {path.split('?')[0]} status {r.status_code}, expected {status}"
 return r.json() if r.content else None
print("Waiting for verified published 0.4.0 readiness; credential file remains private.",flush=True)
for _ in range(144):
 try:
  live=requests.get(BASE+"/health/live",timeout=15);ready=requests.get(BASE+"/health/ready",timeout=15)
  if live.status_code==ready.status_code==200 and live.json().get("version")==ready.json().get("version")=="0.4.0":break
 except requests.RequestException:pass
 time.sleep(5)
else:raise RuntimeError("Published Flow 0.4.0 not ready within bounded wait")
check("HTTPS live and ready version 0.4.0",True)
qa=json.loads(PRIVATE.read_text(encoding="utf-8-sig"))
assert qa["tenantA"]!=qa["tenantB"] and all(k in qa for k in ["email","password","tenantA","tenantB","userId"])
assert qa["email"].endswith("@ebt.example")
if os.environ.get("EBT_FLOW_QA_ACCESS"):assert qa.get("syntheticOnly") is True
s=requests.Session();call(s,"/api/auth/login","POST",{"email":qa["email"],"password":qa["password"]})
check("Authenticated identity matches synthetic QA fixture",call(s,"/api/auth/me")["userId"]==qa["userId"])
call(s,"/api/auth/context/"+qa["tenantA"],"POST",status=204)
for _ in range(60):
 catalog=call(s,"/api/platform/v1/applications")
 if catalog.get("tenantId")==qa["tenantA"] and any(x["code"]=="flow" and x.get("available") for x in catalog["applications"]):break
 time.sleep(3)
else:raise RuntimeError("Flow catalog not activated for synthetic tenant")
check("Catalog Flow available in authorized QA tenant",True)
check("Anonymous protocol and history require authentication",requests.get(BASE+P,timeout=25).status_code==401)
contact_before=call(s,"/api/connect/v1/contacts")["items"]
contact_hash=lambda rows:hashlib.sha256(json.dumps(sorted(x["id"] for x in rows)).encode()).hexdigest()
before_hash=contact_hash(contact_before)
check("Connect read preserved before Flow mutation",isinstance(contact_before,list))
run=uuid.uuid4().hex[:12];key="online-flow-qa-"+run
subject="QA sintÃƒÂ©tico Flow "+run
create=lambda content:call(s,P,"POST",{"subject":content},{"Idempotency-Key":key})
row=create(subject);check("Create persisted open protocol",row["state"]=="open" and row["version"]==1 and row["number"]>0)
replay=create(subject);check("Replay has same ID and sequential number",row["id"]==replay["id"] and row["number"]==replay["number"])
call(s,P,"POST",{"subject":subject+" conflict"},{"Idempotency-Key":key},409);check("Conflicting idempotency payload denied",True)
call(s,P,"POST",{"subject":" "},{"Idempotency-Key":key+"-invalid"},400);check("Empty subject denied",True)
path=P+"/"+row["id"]+"/transition"
transition=lambda action,version,result=None,status=200:call(s,path,"POST",{"action":action,"result":result},{"If-Match":f'"{version}"'},status)
transition("start",99,status=409);check("Stale If-Match denied",True)
started=transition("start",1);check("Start persists state and version",started["state"]=="in_review" and started["version"]==2)
transition("complete",2,"",400);check("Completion needs nonempty result",True)
result="Resultado sintÃƒÂ©tico QA "+run
completed=transition("complete",2,result);check("Complete persists state and version",completed["state"]=="complete" and completed["version"]==3)
history=call(s,P+"/"+row["id"]+"/history")["items"]
check("History exposes three movements and exact QA result",[x["action"] for x in history]==["created","start","complete"] and history[-1]["result"]==result and all(x.get("actorId") for x in history))
transition("complete",3,result,409);check("Repeated completed transition denied",True)
reload=next(x for x in call(s,P)["items"] if x["id"]==row["id"])
check("Reload preserves ID number state version",all(reload[k]==completed[k] for k in ["id","state","version"]) and reload["number"]==row["number"])
call(s,"/api/auth/context/"+qa["tenantB"],"POST",status=204)
check("Tenant B list hides tenant A protocol",row["id"] not in {x["id"] for x in call(s,P)["items"]})
call(s,P+"/"+row["id"]+"/history",status=404);check("Tenant B direct history denied",True)
transition("start",3,status=404);check("Tenant B direct transition denied",True)
call(s,"/api/auth/context/"+qa["tenantA"],"POST",status=204)
check("Returning to A preserves completed history",call(s,P+"/"+row["id"]+"/history")["items"][-1]["result"]==result)
contact_after=call(s,"/api/connect/v1/contacts")["items"]
check("Existing Connect contact IDs preserved after Flow",contact_hash(contact_after)==before_hash)
report={"generatedUtc":datetime.now(timezone.utc).isoformat(),"url":BASE,"version":"0.4.0","environment":"published authorized synthetic QA tenants only","passed":True,"checks":CHECKS,"syntheticProtocolId":row["id"],"contactIdsBeforeSha256":before_hash,"contactIdsAfterSha256":contact_hash(contact_after),"credentialCopied":False,"realMessagesSent":0,"limits":["No customer or user homologation","No Azure restore performed","No changes to existing Connect contact rows","Protocol created only in authorized synthetic QA tenant"]}
(ROOT/"evidencias/flow_online_qa_20261009.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
