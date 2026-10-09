"""Synthetic localhost catalog and authorization checks; no real data or sends."""
import json, subprocess, uuid, requests
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
BASE="http://127.0.0.1:5186"
qa=json.loads((ROOT/"tmp/runtime/qa-access.json").read_text(encoding="utf-8-sig"))
config=json.loads((ROOT/"tmp/runtime/local-config.json").read_text(encoding="utf-8-sig"))
connection=config["ConnectionStrings"]["Platform"]
if "Database=EbtPlatformQa_Review20261008" not in connection or "Server=localhost" not in connection:raise RuntimeError("Wrong local QA fixture")
results=[]
def check(name,condition):
 if not condition:raise AssertionError(name)
 results.append({"name":name,"passed":True});print("PASS "+name)
def csrf(s):return s.get(BASE+"/api/security/csrf",timeout=15).json()["token"]
def post(s,path,body=None):return s.post(BASE+path,json=body,headers={"X-CSRF-TOKEN":csrf(s)},timeout=20)
def login(email):
 s=requests.Session();r=post(s,"/api/auth/login",{"email":email,"password":qa["password"]});r.raise_for_status();return s
check("Anonymous platform catalog denied",requests.get(BASE+"/api/platform/v1/applications",timeout=15).status_code==401)
s=login("admin@ebt.example")
for tenant in [qa["tenantA"],qa["tenantB"]]:
 post(s,"/api/auth/context/"+tenant).raise_for_status()
 r=s.get(BASE+"/api/platform/v1/applications",timeout=15);r.raise_for_status();d=r.json()
 check("Catalog scoped to authorized tenant "+("A" if tenant==qa["tenantA"] else "B"),d["tenantId"]==tenant and len(d["applications"])==9 and sum(x["available"] for x in d["applications"])==1 and next(x for x in d["applications"] if x["available"])["code"]=="connect" and "dataSchema" not in d["applications"][0])
check("Catalog preserves Portuguese Unicode",next(x for x in d["applications"] if x["code"]=="educacao")["name"]=="EBT Educa\u00e7\u00e3o" and next(x for x in d["applications"] if x["code"]=="saude")["name"]=="EBT Sa\u00fade")
check("Unimplemented platform mutation unavailable",post(s,"/api/platform/v1/applications",{"code":"flow","state":"available"}).status_code in (404,405))
post(s,"/api/auth/context/"+qa["tenantA"]).raise_for_status()
r=post(s,"/api/admin/api-keys");r.raise_for_status();key=r.json()
check("Connect API key cannot access platform catalog",requests.get(BASE+"/api/platform/v1/applications",headers={"Authorization":"Bearer "+key["token"]},timeout=15).status_code==401)
s.delete(BASE+"/api/admin/api-keys/"+key["id"],headers={"X-CSRF-TOKEN":csrf(s)},timeout=20).raise_for_status()
reader=login("consulta@ebt.example")
check("Reader can use catalog without admin privileges",reader.get(BASE+"/api/platform/v1/applications",timeout=15).status_code==200)
# Direct SQL permissions only on a temporary synthetic local principal; always clean up.
principal="platform_catalog_qa_"+uuid.uuid4().hex[:10]
sql=f"CREATE USER [{principal}] WITHOUT LOGIN; GRANT SELECT ON OBJECT::ebt_platform.Applications TO [{principal}]; EXECUTE AS USER='{principal}'; SELECT CASE WHEN HAS_PERMS_BY_NAME('ebt_platform.Applications','OBJECT','SELECT')=1 AND HAS_PERMS_BY_NAME('ebt_platform.Applications','OBJECT','INSERT')=0 AND HAS_PERMS_BY_NAME('ebt_platform','SCHEMA','ALTER')=0 THEN 1 ELSE 0 END; REVERT; DROP USER [{principal}];"
r=subprocess.run(["sqlcmd","-S","localhost","-E","-C","-d","EbtPlatformQa_Review20261008","-b","-h","-1","-W","-Q",sql],capture_output=True,text=True,timeout=30)
check("Catalog runtime read permission does not imply writes or schema DDL",r.returncode==0 and "1" in r.stdout.split())
d={"generatedUtc":datetime.now(timezone.utc).isoformat(),"environment":"synthetic localhost SQL QA","passed":True,"cases":results,"realMessagesSent":0,"limits":["Azure permissions and published runtime require separate proof"]}
(ROOT/"evidencias/platform_catalog_qa_20261009.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
