using System.Diagnostics;
using System.Net;
using System.Text.Json;
using Ebt.Platform.Api;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging.Abstractions;

static class MailSqlChecks
{
    public static async Task Run()
    {
        var root = Directory.GetCurrentDirectory(); var config = new ConfigurationBuilder().AddJsonFile(Path.Combine(root,"tmp/runtime/local-config.json")).Build();
        var connection = config.GetConnectionString("Platform")!; var sql = new SqlConnectionStringBuilder(connection);
        if(sql.DataSource!="localhost" || !sql.InitialCatalog.StartsWith("EbtPlatformQa_",StringComparison.Ordinal)) throw new Exception("Exclusive synthetic localhost SQL required");
        using var accessFile=JsonDocument.Parse(await File.ReadAllTextAsync(Path.Combine(root,"tmp/runtime/qa-access.json"))); var user=accessFile.RootElement.GetProperty("users").GetProperty("admin@ebt.example").GetGuid();
        var handler=new SyntheticHandler(); var configuration=new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?> { ["Mail:Enabled"]="true",["Mail:MicrosoftTenantId"]=Guid.NewGuid().ToString(),["Mail:ClientId"]=Guid.NewGuid().ToString(),["Mail:ClientSecret"]="synthetic-mail-sql-secret",["Mail:Sender"]="sender@ebt.example" }).Build();
        var collection=new ServiceCollection(); collection.AddScoped<AccessScope>(); collection.AddScoped<TenantSqlContext>();
        collection.AddDbContext<PlatformDb>((s,o)=>o.UseSqlServer(connection).AddInterceptors(s.GetRequiredService<TenantSqlContext>())); collection.AddSingleton<IHttpClientFactory>(new Factory(handler));
        using var services=collection.BuildServiceProvider(); var worker=new MailWorker(services.GetRequiredService<IServiceScopeFactory>(),configuration,new SyntheticEnvironment(),NullLogger<MailWorker>.Instance);
        var cases=new List<object>(); void Check(bool ok,string name){if(!ok)throw new Exception(name);cases.Add(new{name,result="passed"});Console.WriteLine("PASS "+name);}
        async Task<(Guid Tenant,Guid[] Drafts)> Seed(int cap,int interval,int messages)
        {
            using var scope=services.CreateScope(); var access=scope.ServiceProvider.GetRequiredService<AccessScope>(); access.System=true;
            var db=scope.ServiceProvider.GetRequiredService<PlatformDb>(); var tenant=new Tenant{Name="Synthetic Mail Worker "+Guid.NewGuid().ToString("N")}; db.Tenants.Add(tenant);
            db.Memberships.Add(new Membership{TenantId=tenant.Id,UserId=user,Role="admin"});
            var contact=new Contact{TenantId=tenant.Id,Name="Synthetic worker recipient",Email="worker@client.example",OwnerId=user,ExternalKey="synthetic-worker"};db.Contacts.Add(contact);
            db.MailSettings.Add(new MailSettings{TenantId=tenant.Id,Paused=false,DailyCap=cap,IntervalSeconds=interval});var ids=new List<Guid>();
            for(var i=0;i<messages;i++){var row=new MailDraft{TenantId=tenant.Id,ContactId=contact.Id,ActorId=user,ApprovedBy=user,ApprovedAt=DateTimeOffset.UtcNow,State="queued",Recipient=contact.Email,Subject="Synthetic worker "+i,Body="Synthetic reviewed body",CreationKey="synthetic-"+Guid.NewGuid().ToString("N")};db.MailDrafts.Add(row);ids.Add(row.Id);}
            await db.SaveChangesAsync();configuration["Mail:PlatformTenantId"]=tenant.Id.ToString();handler.Starts.Clear();handler.Status=HttpStatusCode.Accepted; return(tenant.Id,ids.ToArray());
        }
        async Task<(MailDraft[] Rows,MailSettings Settings,int Used)> Read(Guid tenant)
        {
            using var service=services.CreateScope();service.ServiceProvider.GetRequiredService<AccessScope>().TenantId=tenant;var db=service.ServiceProvider.GetRequiredService<PlatformDb>();return(await db.MailDrafts.AsNoTracking().ToArrayAsync(),await db.MailSettings.AsNoTracking().SingleAsync(),await db.MailQuotas.Select(x=>x.Used).SingleAsync());
        }
        var cap=await Seed(1,1,2);await Task.WhenAll(worker.Process(cap.Tenant,CancellationToken.None),worker.Process(cap.Tenant,CancellationToken.None));var read=await Read(cap.Tenant);
        Check(handler.Starts.Count==1 && read.Rows.Count(x=>x.State=="accepted")==1 && read.Used==1,"Concurrent workers claim one job and reserve one quota slot");
        using (var historyScope = services.CreateScope())
        {
            historyScope.ServiceProvider.GetRequiredService<AccessScope>().TenantId = cap.Tenant;
            var historyDb = historyScope.ServiceProvider.GetRequiredService<PlatformDb>();
            Check(await historyDb.Interactions.CountAsync(x => x.Kind == "email" && x.Content.Contains("accepted")) == 1,
                "Graph acceptance automatically records one CRM interaction without manual confirmation");
        }
        await Task.Delay(1150);await worker.Process(cap.Tenant,CancellationToken.None);read=await Read(cap.Tenant);
        Check(handler.Starts.Count==1 && read.Settings.Paused && read.Rows.Count(x=>x.State=="queued")==1,"Daily cap persists and pauses without an extra send");
        var pace=await Seed(5,1,2);await worker.Process(pace.Tenant,CancellationToken.None);await worker.Process(pace.Tenant,CancellationToken.None);
        Check(handler.Starts.Count==1,"Per-send interval blocks an immediate second call");await Task.Delay(1150);await worker.Process(pace.Tenant,CancellationToken.None);
        Check(handler.Starts.Count==2 && Stopwatch.GetElapsedTime(handler.Starts[0],handler.Starts[1]).TotalSeconds>=1,"Observed call timestamps respect interval across SQL reservations");
        var throttle=await Seed(5,1,1);handler.Status=HttpStatusCode.TooManyRequests;await worker.Process(throttle.Tenant,CancellationToken.None);read=await Read(throttle.Tenant);
        Check(read.Settings.Paused && read.Rows.Single().Diagnostic=="graph_throttled" && handler.Starts.Count==1,"429 pauses persisted queue without automatic retry");
        var uncertain=await Seed(5,1,1);handler.Status=HttpStatusCode.BadGateway;await worker.Process(uncertain.Tenant,CancellationToken.None);await worker.Process(uncertain.Tenant,CancellationToken.None);read=await Read(uncertain.Tenant);
        Check(read.Settings.Paused && read.Rows.Single().State=="unknown" && read.Used==1 && handler.Starts.Count==1,"Uncertain provider result retains reservation and never resends");
        var suppressed=await Seed(5,1,1);
        using(var scope=services.CreateScope()){scope.ServiceProvider.GetRequiredService<AccessScope>().TenantId=suppressed.Tenant;var db=scope.ServiceProvider.GetRequiredService<PlatformDb>();db.MailSuppressions.Add(new MailSuppression{TenantId=suppressed.Tenant,Value="client.example",Reason="Synthetic opt-out",ActorId=user});await db.SaveChangesAsync();}
        await worker.Process(suppressed.Tenant,CancellationToken.None);read=await Read(suppressed.Tenant);
        Check(handler.Starts.Count==0 && read.Rows.Single().State=="failed","Domain suppression is rechecked at dispatch, before HTTP");
        await File.WriteAllTextAsync(Path.Combine(root,"evidencias/mail_worker_sql_20261009.json"),JsonSerializer.Serialize(new{environment=sql.InitialCatalog,syntheticOnly=true,realEmailSent=false,passed=true,cases},new JsonSerializerOptions{WriteIndented=true}));
    }
    sealed class Factory(SyntheticHandler handler):IHttpClientFactory{public HttpClient CreateClient(string name)=>new(handler,false);}
    sealed class SyntheticHandler:HttpMessageHandler
    {
        public List<long> Starts=new();public HttpStatusCode Status=HttpStatusCode.Accepted;
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct)
        {
            if(request.RequestUri!.Host=="login.microsoftonline.com")return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK){Content=new StringContent("{\"access_token\":\"synthetic-token\"}")});
            if(request.RequestUri.Host!="graph.microsoft.com")throw new Exception("Unexpected mock endpoint");Starts.Add(Stopwatch.GetTimestamp());return Task.FromResult(new HttpResponseMessage(Status){Content=new StringContent("{}")});
        }
    }
    sealed class SyntheticEnvironment:IHostEnvironment
    {
        public string EnvironmentName{get;set;}="Production";public string ApplicationName{get;set;}="SyntheticMailWorker";public string ContentRootPath{get;set;}="";public IFileProvider ContentRootFileProvider{get;set;}=new NullFileProvider();
    }
}
