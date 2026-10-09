using Ebt.Platform.Api;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using System.Net;
using System.Text.Json;

public static class ProxyChecks
{
    public static async Task Run()
    {
        var configuration=new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?>{{"Platform:TrustedProxies","10.10.0.4"}}).Build();
        var options=ProxyConfiguration.Options(configuration);
        async Task<HttpContext> Request(string sender,string forwardedFor="198.51.100.2")
        {
            var context=new DefaultHttpContext();context.Request.Scheme="http";context.Request.Host=new HostString("connect.example");context.Connection.RemoteIpAddress=IPAddress.Parse(sender);
            context.Request.Headers["X-Forwarded-Proto"]="https";context.Request.Headers["X-Forwarded-For"]=forwardedFor;context.Request.Headers["X-Forwarded-Host"]="evil.example";
            var middleware=new ForwardedHeadersMiddleware(_=>Task.CompletedTask,NullLoggerFactory.Instance,Options.Create(options));await middleware.Invoke(context);return context;
        }
        var trusted=await Request("10.10.0.4");if(trusted.Request.Scheme!="https"||trusted.Connection.RemoteIpAddress?.ToString()!="198.51.100.2")throw new Exception("Trusted proxy failed");
        var publicSender=await Request("203.0.113.3");if(publicSender.Request.Scheme!="http"||publicSender.Connection.RemoteIpAddress?.ToString()!="203.0.113.3")throw new Exception("Untrusted spoof accepted");
        var chain=await Request("10.10.0.4","203.0.113.99, 198.51.100.2");if(chain.Connection.RemoteIpAddress?.ToString()!="198.51.100.2"||chain.Request.Host.Host!="connect.example")throw new Exception("Spoofed IP/host accepted");
        try{ProxyConfiguration.Options(new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?>{{"Platform:TrustedProxies","*"}}).Build());throw new Exception("Wildcard proxy accepted");}catch(InvalidOperationException){}
        async Task<(HttpContext,bool)> Audit(string? configured,string? presented)
        {
            var config=new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?>{{"Platform:ProxyAuditKey",configured}}).Build();
            var context=new DefaultHttpContext();context.Request.Path="/ops/proxy";context.Request.Scheme="http";context.Connection.RemoteIpAddress=IPAddress.Parse("10.10.0.4");context.Response.Body=new MemoryStream();
            if(presented!=null)context.Request.Headers["X-EBT-Proxy-Audit"]=presented;
            var nextCalled=false;await ProxyConfiguration.Audit(context,config,_=>{nextCalled=true;return Task.CompletedTask;});return(context,nextCalled);
        }
        var secret=new string('a',64);
        var acceptedAudit=await Audit(secret,secret);if(acceptedAudit.Item2||acceptedAudit.Item1.Response.StatusCode!=200)throw new Exception("Private audit failed");
        acceptedAudit.Item1.Response.Body.Position=0;var auditBody=await new StreamReader(acceptedAudit.Item1.Response.Body).ReadToEndAsync();if(!auditBody.Contains("10.10.0.4")||auditBody.Contains(secret))throw new Exception("Audit scope failed");
        foreach(var pair in new[]{(secret,(string?)null),(secret,"wrong"),((string?)null,secret)}){var denied=await Audit(pair.Item1,pair.Item2);if(denied.Item2||denied.Item1.Response.StatusCode!=404)throw new Exception("Anonymous audit accepted");}
        foreach(var path in new[]{"/health/live","/health/ready"})if(ProxyConfiguration.RequiresHttpsRedirect(new PathString(path)))throw new Exception("Internal health redirected");
        foreach(var path in new[]{"/api/auth/login","/","/health/ready/extra"})if(!ProxyConfiguration.RequiresHttpsRedirect(new PathString(path)))throw new Exception("Application HTTPS bypassed");
        File.WriteAllText("evidencias/testes_connect_proxy.json",JsonSerializer.Serialize(new{generatedUtc=DateTimeOffset.UtcNow,passed=true,cases=10,checks=new[]{"Explicit proxy restores HTTPS and rightmost client IP","Untrusted sender cannot spoof HTTPS or client IP","Forward limit and ignored host reject spoofed values","Wildcard proxy fails configuration","Private observation exposes only ingress metadata","Observation rejects missing key","Observation rejects wrong key","Observation disabled without configuration","Exact health endpoints serve internal probes","Other application paths still require HTTPS"}},new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine("PASS 10 proxy checks; Azure proxy IP still requires observed confirmation.");
    }
}
