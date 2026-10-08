using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Ebt.Platform.Api;

if(args.Contains("--keyring")){SqlKeyRingChecks.Run();return;}
if(args.Contains("--proxy")){await ProxyChecks.Run();return;}

var results = new List<object>();
void Check(string name, Action test) { test(); results.Add(new { name, passed = true }); Console.WriteLine("PASS " + name); }
void Reject(Action action) { try { action(); } catch (ApiFault) { return; } throw new Exception("Invalid event accepted"); }
var now = DateTimeOffset.UtcNow;
var stamp = now.ToUnixTimeSeconds().ToString();
var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new { eventId = "wzevt_test", version = "1", tenantId = "workspace-A", type = "message.received", occurredAt = now, wabaId = "account-A", phoneNumberId = "phone-A", data = new { from = "5511999988888", message = new { id = "wamid.test", type = "text", text = new { body = "synthetic hello" } } } }));
string Sign(string timestamp, byte[] bytes) => "sha256=" + Convert.ToHexString(HMACSHA256.HashData(Encoding.UTF8.GetBytes("synthetic-secret"), Encoding.UTF8.GetBytes(timestamp + ".").Concat(bytes).ToArray())).ToLowerInvariant();
Check("Signed raw envelope and matching event header", () => { if (!WazVoxProtocol.Verify(body, stamp, Sign(stamp, body), "synthetic-secret", now)) throw new Exception(); WazVoxProtocol.ValidateEnvelope(body,"wzevt_test","workspace-A"); });
Check("Body mutation rejected", () => { if (WazVoxProtocol.Verify(body.Concat(new byte[]{32}).ToArray(), stamp, Sign(stamp,body),"synthetic-secret",now)) throw new Exception(); });
Check("Expired and future delivery signatures rejected", () => { foreach(var at in new[]{now.AddMinutes(-6),now.AddMinutes(6)}) { var t=at.ToUnixTimeSeconds().ToString(); if(WazVoxProtocol.Verify(body,t,Sign(t,body),"synthetic-secret",now)) throw new Exception(); } });
Check("Malformed signatures rejected", () => { if(WazVoxProtocol.Verify(body,stamp,"sha256=zz","synthetic-secret",now) || WazVoxProtocol.Verify(body,"1e9",Sign(stamp,body),"synthetic-secret",now)) throw new Exception(); });
Check("Foreign workspace and mismatched event ID rejected", () => { Reject(()=>WazVoxProtocol.ValidateEnvelope(body,"wzevt_test","workspace-B")); Reject(()=>WazVoxProtocol.ValidateEnvelope(body,"another-event","workspace-A")); });
Check("Inbound normalized with provider IDs and occurrence time", () => { using var eventBody=JsonDocument.Parse(body); using var normalized=WazVoxProtocol.Normalize(eventBody.RootElement); var value=normalized.RootElement.GetProperty("entry")[0].GetProperty("changes")[0].GetProperty("value"); if(value.GetProperty("messages")[0].GetProperty("id").GetString()!="wamid.test" || value.GetProperty("metadata").GetProperty("phone_number_id").GetString()!="phone-A") throw new Exception(); });
Check("Unsupported event never treated as inbound", () => { using var p=JsonDocument.Parse(Encoding.UTF8.GetString(body).Replace("message.received","message.sent")); Reject(()=>WazVoxProtocol.Normalize(p.RootElement)); });
Check("Canonical status normalized using waMessageId", () => { using var p=JsonDocument.Parse(JsonSerializer.Serialize(new{occurredAt=now,type="message.status",wabaId="account-A",phoneNumberId="phone-A",data=new{waMessageId="wamid.sent",status="read",to="5511999988888"}})); using var n=WazVoxProtocol.Normalize(p.RootElement); if(n.RootElement.GetProperty("entry")[0].GetProperty("changes")[0].GetProperty("value").GetProperty("statuses")[0].GetProperty("id").GetString()!="wamid.sent") throw new Exception(); });
Check("Observed provider status shape keeps WhatsApp id and recipient", () => {
 foreach(var state in new[]{"sent","delivered","read","failed"}) {
  using var p=JsonDocument.Parse(JsonSerializer.Serialize(new{occurredAt=now,type="message.status",wabaId="account-A",phoneNumberId="phone-A",data=new{id="wamid.synthetic-status",status=state,timestamp=stamp,recipient_id="5511999988888"}}));
  using var n=WazVoxProtocol.Normalize(p.RootElement);var status=n.RootElement.GetProperty("entry")[0].GetProperty("changes")[0].GetProperty("value").GetProperty("statuses")[0];
  if(status.GetProperty("id").GetString()!="wamid.synthetic-status"||status.GetProperty("recipient_id").GetString()!="5511999988888"||status.GetProperty("status").GetString()!=state)throw new Exception("Observed status shape lost its identity or recipient");
 }
});
Check("Internal UUID cannot replace missing WhatsApp status reference",()=>{using var p=JsonDocument.Parse(JsonSerializer.Serialize(new{occurredAt=now,type="message.status",wabaId="account-A",phoneNumberId="phone-A",data=new{id=Guid.NewGuid().ToString(),status="read",recipient_id="5511999988888"}}));Reject(()=>WazVoxProtocol.Normalize(p.RootElement));});
Check("Conflicting WhatsApp status aliases rejected",()=>{using var p=JsonDocument.Parse(JsonSerializer.Serialize(new{occurredAt=now,type="message.status",wabaId="account-A",phoneNumberId="phone-A",data=new{id="wamid.other",waMessageId="wamid.canonical",status="read",recipient_id="5511999988888"}}));Reject(()=>WazVoxProtocol.Normalize(p.RootElement));});
var handler=new CaptureHandler(); using var client=new HttpClient(handler){BaseAddress=new Uri("https://app.wazvox.com/api/v1/")};
var operation=Guid.NewGuid(); var reply=WazVoxProtocol.Send(client,"synthetic-api-key","phone-A","5511999988888","synthetic reply",operation,CancellationToken.None).GetAwaiter().GetResult();
Check("Outbound uses Bearer and stable operation idempotency",()=>{ if(handler.Key!="ebt-connect-"+operation.ToString("N") || handler.Auth!="Bearer synthetic-api-key" || handler.Url!="https://app.wazvox.com/api/v1/messages") throw new Exception(); using var p=JsonDocument.Parse(handler.Body); if(p.RootElement.GetProperty("phoneNumberId").GetString()!="phone-A" || p.RootElement.GetProperty("text").GetString()!="synthetic reply" || reply.Reference!="wamid.accepted" || reply.State!="accepted") throw new Exception(); });
handler.Response="{\"id\":\"uuid-only\",\"waMessageId\":null,\"status\":\"accepted\"}";
var uncertain=WazVoxProtocol.Send(client,"synthetic-api-key","phone-A","5511999988888","synthetic reply",operation,CancellationToken.None).GetAwaiter().GetResult();
Check("Missing WhatsApp reference remains unknown",()=>{if(uncertain.State!="unknown")throw new Exception();});
handler.Status=HttpStatusCode.BadGateway;
var failed=WazVoxProtocol.Send(client,"synthetic-api-key","phone-A","5511999988888","synthetic reply",operation,CancellationToken.None).GetAwaiter().GetResult();
Check("Provider failure never causes automatic retry",()=>{if(failed.State!="unknown" || handler.Count!=3)throw new Exception();});
using var accountClient=new HttpClient(new AccountHandler()){BaseAddress=new Uri("https://app.wazvox.com/api/v1/")};
Check("Provisioning verifies registered number in its workspace",()=>WazVoxProtocol.VerifyAccount(accountClient,"synthetic-api-key","workspace-A","account-A","phone-A",CancellationToken.None).GetAwaiter().GetResult());
void RejectAccount(string workspace,string account,string phone){try{WazVoxProtocol.VerifyAccount(accountClient,"synthetic-api-key",workspace,account,phone,CancellationToken.None).GetAwaiter().GetResult();}catch(InvalidOperationException){return;}throw new Exception("Foreign account accepted");}
Check("Provisioning rejects foreign workspace",()=>RejectAccount("workspace-B","account-A","phone-A"));
Check("Provisioning rejects foreign WABA and number",()=>{RejectAccount("workspace-A","account-B","phone-A");RejectAccount("workspace-A","account-A","phone-B");});
var report=new{generatedUtc=DateTimeOffset.UtcNow,version="0.1.5",environment="synthetic protocol; no provider send",passed=true,cases=results.Count,results};
Directory.CreateDirectory("evidencias"); File.WriteAllText("evidencias/testes_wazvox_protocol.json",JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true}));

sealed class CaptureHandler:HttpMessageHandler
{
 public string Key="",Auth="",Body="",Url="";
 public int Count;
 public string Response="{\"id\":\"uuid\",\"waMessageId\":\"wamid.accepted\",\"status\":\"accepted\"}";
 public HttpStatusCode Status=HttpStatusCode.Created;
 protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct){Count++;Key=request.Headers.GetValues("Idempotency-Key").Single();Auth=request.Headers.Authorization!.ToString();Url=request.RequestUri!.ToString();Body=await request.Content!.ReadAsStringAsync(ct);return new HttpResponseMessage(Status){Content=new StringContent(Response,Encoding.UTF8,"application/json")};}
}
sealed class AccountHandler:HttpMessageHandler
{
 protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct)
 {
  if(request.Headers.Authorization?.ToString()!="Bearer synthetic-api-key")throw new Exception("Missing server credential");
  var json=request.RequestUri!.AbsolutePath.EndsWith("/me",StringComparison.Ordinal)?"{\"data\":{\"tenantId\":\"workspace-A\"}}":"{\"data\":[{\"wabaId\":\"account-A\",\"phoneNumberId\":\"phone-A\",\"registered\":true,\"connectionStatus\":\"connected\"}]}";
  return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK){Content=new StringContent(json)});
 }
}
