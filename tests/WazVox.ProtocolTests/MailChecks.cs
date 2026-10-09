using System.Net;
using System.Text;
using System.Text.Json;
using Ebt.Platform.Api;
using Microsoft.Extensions.Configuration;

static class MailChecks
{
    public static async Task Run()
    {
        var tenant = Guid.NewGuid(); var config = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?> { ["Mail:Enabled"]="true", ["Mail:PlatformTenantId"]=tenant.ToString(), ["Mail:MicrosoftTenantId"]=Guid.NewGuid().ToString(), ["Mail:ClientId"]=Guid.NewGuid().ToString(), ["Mail:ClientSecret"]="synthetic-mail-secret", ["Mail:Sender"]="sender@ebt.example" }).Build();
        var row = new MailDraft { TenantId=tenant, Recipient="recipient@ebt.example", Subject="Synthetic subject", Body="Own text\nsecond line" }; int count=0;
        void Check(bool passed, string name) { if(!passed) throw new Exception(name); count++; Console.WriteLine("PASS " + name); }
        var handler = new MailHandler(); using var client = new HttpClient(handler);
        var result = await GraphMail.Send(client,config,row,null,CancellationToken.None);
        Check(result.State=="accepted" && result.Code=="graph_accepted_not_delivery" && handler.Posts==1,"Graph 202 is acceptance, never delivery/read");
        using(var payload=JsonDocument.Parse(handler.Body))
        {
            var message=payload.RootElement.GetProperty("message");
            Check(message.GetProperty("body").GetProperty("contentType").GetString()=="Text" && message.GetProperty("body").GetProperty("content").GetString()==row.Body && payload.RootElement.GetProperty("saveToSentItems").GetBoolean(),"Plain text and Sent Items copy preserve reviewed content");
            Check(message.GetProperty("internetMessageHeaders")[0].GetProperty("value").GetString()==row.Id.ToString(),"Stable operation reference for manual reconciliation");
        }
        handler.Status=HttpStatusCode.TooManyRequests; result=await GraphMail.Send(client,config,row,null,CancellationToken.None);
        Check(result.Code=="graph_throttled" && handler.Posts==2,"429 classified without automatic HTTP retry");
        handler.Status=HttpStatusCode.BadGateway; result=await GraphMail.Send(client,config,row,null,CancellationToken.None);
        Check(result.State=="unknown" && handler.Posts==3,"5xx remains uncertain; no resend");
        handler.BreakConnection=true; result=await GraphMail.Send(client,config,row,null,CancellationToken.None);
        Check(result.State=="unknown" && handler.Posts==4,"Interrupted send remains uncertain");
        handler.BreakConnection=false; handler.TokenDenied=true; result=await GraphMail.Send(client,config,row,null,CancellationToken.None);
        Check(result.State=="failed" && result.Code=="graph_authentication_failed" && handler.Posts==4,"Token failure does not attempt send or expose provider text");
        row.TenantId=Guid.NewGuid(); result=await GraphMail.Send(client,config,row,null,CancellationToken.None);
        Check(result.Code=="mail_unconfigured" && handler.Posts==4,"Other EBT tenant cannot use bound Microsoft mailbox");
        row.TenantId=tenant; handler.TokenDenied=false; handler.Status=HttpStatusCode.Accepted;
        var attachment=new DocumentVersion { FileName="synthetic.txt",MediaType="text/plain",Content=Encoding.UTF8.GetBytes("synthetic file") };
        await GraphMail.Send(client,config,row,attachment,CancellationToken.None);
        using(var payload=JsonDocument.Parse(handler.Body)) Check(payload.RootElement.GetProperty("message").GetProperty("attachments")[0].GetProperty("contentBytes").GetString()==Convert.ToBase64String(attachment.Content),"Approved attachment payload encodes exact bytes");
        var (today,tomorrow)=ConnectImprovements.Today(new DateTimeOffset(2026,10,9,2,0,0,TimeSpan.Zero));
        Check(today.Day==8 && today.Hour==0 && tomorrow.Day==9 && today.Offset==TimeSpan.FromHours(-3),"Agenda day and mail quota use Sao Paulo boundary");
        Check(ConnectImprovements.CalendarText("a\r\nX:b,c;d\\e")=="a\\nX:b\\,c\\;d\\\\e","Calendar export escapes line and delimiter injection");
        Check(MailEndpoints.Personalize("{nome}|{empresa}|{email}",new Contact{Name="Ana",Email="ana@ebt.example"},"EBT")=="Ana|EBT|ana@ebt.example","Local template works without AI or credits");
        Console.WriteLine($"{count} mail protocol checks passed; mocked HTTP only, no real emails.");
    }
    sealed class MailHandler : HttpMessageHandler
    {
        public int Posts; public string Body=""; public HttpStatusCode Status=HttpStatusCode.Accepted; public bool BreakConnection,TokenDenied;
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct)
        {
            if(request.RequestUri!.Host=="login.microsoftonline.com") return new HttpResponseMessage(TokenDenied?HttpStatusCode.Unauthorized:HttpStatusCode.OK){Content=new StringContent("{\"access_token\":\"synthetic-token\"}")};
            if(request.RequestUri.Host!="graph.microsoft.com" || request.Method!=HttpMethod.Post) throw new Exception("Unexpected endpoint");
            Posts++; Body=await request.Content!.ReadAsStringAsync(ct); if(BreakConnection) throw new HttpRequestException("Synthetic transport loss");
            return new HttpResponseMessage(Status){Content=new StringContent("{\"private\":\"provider detail not returned\"}")};
        }
    }
}
