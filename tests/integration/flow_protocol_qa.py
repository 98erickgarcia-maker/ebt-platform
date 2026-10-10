"""Flow gate against a fresh localhost SQL database and synthetic identities only."""
import concurrent.futures, hashlib, json, os, secrets, subprocess, time, uuid, socket
from datetime import datetime, timezone
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[2]
RUN=uuid.uuid4().hex[:10]
DB="EbtPlatformQa_Flow_"+RUN
RUNTIME=ROOT/"tmp"/("flow-qa-"+RUN)
RUNTIME.mkdir(parents=True)
with socket.socket() as probe:
 probe.bind(("127.0.0.1",0)); PORT=probe.getsockname()[1]
BASE=f"http://127.0.0.1:{PORT}"
DLL=ROOT/"src/backend/Ebt.Platform.Api/bin/Release/net10.0/Ebt.Platform.Api.dll"
CONFIG=RUNTIME/"config.json"
CONFIG.write_text(json.dumps({"ConnectionStrings":{"Platform":f"Server=localhost;Database={DB};Integrated Security=True;Encrypt=True;TrustServerCertificate=True"},"Platform":{"KeyPath":str(RUNTIME/"keys"),"RunWorkers":False},"Qa":{"Password":"Qa9!"+secrets.token_hex(18),"AccessFile":str(RUNTIME/"access.json"),"ReviewedCommercialScript":str(ROOT/"sql/connect-commercial-20261009.sql"),"CatalogScript":str(ROOT/"sql/platform-catalog.sql")}}),encoding="utf-8")
ENV={**os.environ,"ASPNETCORE_ENVIRONMENT":"Development","EBT_RUNTIME_CONFIG":str(CONFIG)}
CASES=[]
def check(name,condition):
 if not condition: raise AssertionError(name)
 CASES.append({"name":name,"passed":True});print("PASS "+name,flush=True)
def sql(query,system=True):
 assert DB.startswith("EbtPlatformQa_Flow_")
 prefix="SET NOCOUNT ON; "
 if system:prefix+="EXEC sys.sp_set_session_context @key=N'ebt_system',@value=1; "
 r=subprocess.run(["sqlcmd","-S","localhost","-E","-C","-b","-d",DB,"-h","-1","-W","-Q",prefix+query],capture_output=True,text=True,timeout=45)
 if r.returncode:raise RuntimeError(r.stderr+ r.stdout)
 return r.stdout.strip()
def request(s,path,method="GET",body=None,headers=None,status=200):
 h=dict(headers or {})
 if method!="GET":h["X-CSRF-TOKEN"]=s.get(BASE+"/api/security/csrf",timeout=15).json()["token"]
 r=s.request(method,BASE+path,json=body,headers=h,timeout=40)
 assert r.status_code==status, f"{method} {path}: expected {status}, got {r.status_code}: {r.text[:200]}"
 return r.json() if r.content else None
def login(email,tenant=None):
 s=requests.Session();request(s,"/api/auth/login","POST",{"email":email,"password":access["password"]})
 if tenant:request(s,"/api/auth/context/"+tenant,"POST",status=204)
 return s
P="/api/flow/v1/protocols"
log=(RUNTIME/"server.log").open("w",encoding="utf-8")
server=None
try:
 init=subprocess.run(["dotnet",str(DLL),"--init-qa"],env=ENV,stdout=log,stderr=log,timeout=120)
 check("Fresh isolated QA database initialized",init.returncode==0)
 script=(ROOT/"sql/flow-protocol-mvp-20261009.sql").read_text(encoding="utf-8-sig")
 for repeat in range(2):check("Flow migration commit and repeat "+str(repeat+1),sql(script+" SELECT @@TRANCOUNT;")=="0")
 access=json.loads((RUNTIME/"access.json").read_text())
 server=subprocess.Popen(["dotnet",str(DLL),"--urls",BASE],env=ENV,stdout=log,stderr=log,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
 for _ in range(50):
  if server.poll() is not None:raise RuntimeError("Own QA server exited; inspect private server log")
  try:
   if requests.get(BASE+"/health/ready",timeout=1).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.4)
 else:raise RuntimeError("QA server not ready")
 check("Anonymous Flow rejected",requests.get(BASE+P,timeout=10).status_code==401)
 a=login("admin@ebt.example",access["tenantA"]);b=login("admin@ebt.example",access["tenantB"])
 op=login("operador@ebt.example");other=login("outra@ebt.example");reader=login("consulta@ebt.example")
 key="flow-"+RUN
 create=lambda s,subject,key=key:request(s,P,"POST",{"subject":subject},{"Idempotency-Key":key})
 row=create(op,"Synthetic protocol")
 check("Idempotent replay preserves ID",create(op,"Synthetic protocol")["id"]==row["id"])
 request(op,P,"POST",{"subject":"Changed"},{"Idempotency-Key":key},409);check("Mismatched replay rejected",True)
 request(other,P,"POST",{"subject":"Synthetic protocol"},{"Idempotency-Key":key},404);check("Other portfolio cannot replay private protocol",True)
 check("Tenant B list hides A",row["id"] not in {x["id"] for x in request(b,P)["items"]})
 check("Other portfolio list hides A",row["id"] not in {x["id"] for x in request(other,P)["items"]})
 request(reader,P,"POST",{"subject":"Reader"},{"Idempotency-Key":uuid.uuid4().hex},403);check("Reader mutation denied",True)
 request(op,P,"POST",{"subject":" "},{"Idempotency-Key":uuid.uuid4().hex},400);check("Invalid subject denied",True)
 request(op,P,"POST",{"subject":"No key"},status=400);check("Missing idempotency key denied",True)
 transition=lambda s,action,ver,result=None,status=200:request(s,P+"/"+row["id"]+"/transition","POST",{"action":action,"result":result},{"If-Match":f'"{ver}"'},status)
 transition(b,"start",1,status=404);transition(other,"start",1,status=404);check("Cross tenant and portfolio direct transition denied",True)
 request(b,P+"/"+row["id"]+"/history",status=404);request(other,P+"/"+row["id"]+"/history",status=404);check("History direct ID scoped",True)
 transition(op,"complete",1,"done",409);transition(op,"start",9,status=409);check("Invalid transition and stale version rejected",True)
 transition(op,"start",1);transition(op,"complete",2,"",400);transition(op,"complete",2,"Synthetic result")
 history=request(op,P+"/"+row["id"]+"/history")["items"]
 check("Three persisted movements and completion result",[x["action"] for x in history]==["created","start","complete"] and history[-1]["result"]=="Synthetic result")
 transition(op,"complete",3,"Again",409);check("Completed protocol cannot complete twice",True)
 def concurrent_create(i):
  s=requests.Session();s.cookies.update(op.cookies)
  return create(s,"Concurrent "+str(i),"parallel-"+RUN+"-"+str(i))
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(concurrent_create,range(16)))
 numbers=sorted(x["number"] for x in rows)
 check("16 concurrent creations have unique contiguous sequence",len(set(numbers))==16 and numbers==list(range(numbers[0],numbers[0]+16)))
 def race_transition(i):
  s=requests.Session();s.cookies.update(op.cookies)
  csrf=s.get(BASE+"/api/security/csrf",timeout=15).json()["token"]
  return s.post(BASE+P+"/"+rows[0]["id"]+"/transition",json={"action":"start","result":None},headers={"X-CSRF-TOKEN":csrf,"If-Match":'"1"'},timeout=30).status_code
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:statuses=list(pool.map(race_transition,range(2)))
 check("Concurrent same-version transition commits once",sorted(statuses)==[200,409] and len(request(op,P+"/"+rows[0]["id"]+"/history")["items"])==2)

 def replay(i):
  s=requests.Session();s.cookies.update(op.cookies)
  return create(s,"Concurrent replay","same-"+RUN)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:replays=list(pool.map(replay,range(8)))
 check("8 simultaneous replays create exactly one protocol",len({x["id"] for x in replays})==1)
 foreign=create(b,"Tenant B independent sequence","tenant-b-"+RUN)
 check("Sequence scoped independently to tenant",foreign["number"]==1)
 count=sql("SELECT COUNT(*) FROM ebt_flow.Protocols WHERE TenantId='"+access["tenantA"]+"';")
 visible=sql("EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value='"+access["tenantA"]+"'; SELECT COUNT(*) FROM ebt_flow.Protocols;")
 check("RLS SQL read exposes only selected tenant",visible==count)
 check("RLS SQL without context exposes nothing",sql("SELECT COUNT(*) FROM ebt_flow.Protocols;",False)=="0")
 principal="flow_qa_"+RUN
 sql("CREATE USER ["+principal+"] WITHOUT LOGIN; GRANT SELECT,INSERT,UPDATE ON OBJECT::ebt_flow.Protocols TO ["+principal+"]; GRANT SELECT,INSERT ON OBJECT::ebt_flow.Movements TO ["+principal+"];")
 permission=sql("EXECUTE AS USER='"+principal+"'; SELECT CASE WHEN HAS_PERMS_BY_NAME('ebt_flow.Protocols','OBJECT','SELECT')=1 AND HAS_PERMS_BY_NAME('ebt_flow.Protocols','OBJECT','UPDATE')=1 AND HAS_PERMS_BY_NAME('ebt_flow.Movements','OBJECT','UPDATE')=0 AND HAS_PERMS_BY_NAME('ebt_flow','SCHEMA','ALTER')=0 AND HAS_PERMS_BY_NAME('dbo','SCHEMA','SELECT')=0 THEN 1 ELSE 0 END; REVERT;")
 check("Object-only runtime grants deny history modification and DDL",permission=="1")
 blocked=sql("EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value='"+access["tenantA"]+"'; EXECUTE AS USER='"+principal+"'; BEGIN TRY INSERT INTO ebt_flow.Protocols (TenantId,Id,Number,[Year],Subject,Portfolio,CreatedAt,CreatedBy,OperationKey,PayloadHash) VALUES ('"+access["tenantB"]+"',NEWID(),987654,2026,N'RLS negative',N'principal',SYSUTCDATETIME(),NEWID(),N'rls-negative',REPLICATE('a',64)); SELECT 0; END TRY BEGIN CATCH SELECT CASE WHEN ERROR_NUMBER()=33504 THEN 1 ELSE 0 END; END CATCH; REVERT;")
 check("Runtime SQL cross-tenant insertion blocked by RLS",blocked=="1")
 sql("DROP USER ["+principal+"];")
 sql("EXEC(N'CREATE TRIGGER ebt_flow.qa_fail_movement ON ebt_flow.Movements AFTER INSERT AS THROW 51002,''Synthetic rollback probe'',1;');")
 request(op,P,"POST",{"subject":"Rollback probe"},{"Idempotency-Key":"rollback-"+RUN},503)
 sql("DROP TRIGGER ebt_flow.qa_fail_movement;")
 check("Movement failure rolls back protocol and sequence",sql("SELECT COUNT(*) FROM ebt_flow.Protocols WHERE OperationKey='rollback-"+RUN+"';")=="0")
 # Fresh connections read committed records after the HTTP server is stopped and restarted.
 server.terminate();server.wait(timeout=20)
 server=subprocess.Popen(["dotnet",str(DLL),"--urls",BASE],env=ENV,stdout=log,stderr=log,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
 for _ in range(50):
  if server.poll() is not None:raise RuntimeError("Own QA server exited; inspect private server log")
  try:
   if requests.get(BASE+"/health/ready",timeout=1).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.4)
 check("Restart preserves session and persisted history",request(op,P+"/"+row["id"]+"/history")["items"][-1]["result"]=="Synthetic result")
 # Restore a full synthetic backup into another fresh local QA database; never overwrite source.
 restored=DB+"_Restore"
 backup_sql="""
DECLARE @backup nvarchar(4000)=CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultBackupPath'))+N'\\"""+DB+""".bak';
DECLARE @data nvarchar(4000)=CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultDataPath'))+N'\\"""+restored+""".mdf';
DECLARE @log nvarchar(4000)=CONVERT(nvarchar(4000),SERVERPROPERTY('InstanceDefaultLogPath'))+N'\\"""+restored+""".ldf';
DECLARE @logicalData nvarchar(128)=(SELECT TOP(1)name FROM sys.database_files WHERE type=0);
DECLARE @logicalLog nvarchar(128)=(SELECT TOP(1)name FROM sys.database_files WHERE type=1);
BACKUP DATABASE ["""+DB+"""] TO DISK=@backup WITH COPY_ONLY,INIT,CHECKSUM;
RESTORE DATABASE ["""+restored+"""] FROM DISK=@backup WITH MOVE @logicalData TO @data,MOVE @logicalLog TO @log,CHECKSUM;
"""
 sql(backup_sql)
 digest="SELECT CONVERT(varchar(64),HASHBYTES('SHA2_256',(SELECT * FROM ebt_flow.Protocols ORDER BY TenantId,Id FOR JSON PATH)),2); SELECT CONVERT(varchar(64),HASHBYTES('SHA2_256',(SELECT * FROM ebt_flow.Movements ORDER BY TenantId,Id FOR JSON PATH)),2);"
 original=sql(digest)
 recovered=sql(digest.replace("FROM ebt_flow.","FROM ["+restored+"].ebt_flow."))
 check("SQL backup restore preserves protocol and movement hashes",original==recovered)
 report={"generatedUtc":datetime.now(timezone.utc).isoformat(),"environment":"exclusive localhost SQL QA","database":DB,"passed":True,"scriptSha256":hashlib.sha256((ROOT/"sql/flow-protocol-mvp-20261009.sql").read_bytes()).hexdigest(),"sourceHashes":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ["src/backend/Ebt.Platform.Api/FlowProtocol.cs","tests/integration/flow_protocol_qa.py"]},"cases":CASES,"limits":["No Azure migration or deploy","No user homologation","No attachments or linked tasks in this first protocol slice"]}
 (ROOT/"evidencias/flow_protocol_sql_qa_20261009.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
finally:
 if server and server.poll() is None:server.terminate();server.wait(timeout=20)
 log.close()
