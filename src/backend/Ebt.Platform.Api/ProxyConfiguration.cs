using Microsoft.AspNetCore.HttpOverrides;
using System.Net;

namespace Ebt.Platform.Api;

public static class ProxyConfiguration
{
    // Exact, metadata-only health routes support internal Azure probes without a TLS proxy.
    public static bool RequiresHttpsRedirect(PathString path) => path != "/health/live" && path != "/health/ready";

    // Temporary operator observation before HTTPS redirection. Disabled by default.
    public static async Task Audit(HttpContext context, IConfiguration configuration, RequestDelegate next)
    {
        if (context.Request.Path != "/ops/proxy") { await next(context); return; }
        var expected = configuration["Platform:ProxyAuditKey"];
        var provided = context.Request.Headers["X-EBT-Proxy-Audit"].ToString();
        context.Response.Headers.CacheControl = "no-store";
        if (expected is null || expected.Length < 32 || provided.Length != expected.Length ||
            !System.Security.Cryptography.CryptographicOperations.FixedTimeEquals(System.Text.Encoding.UTF8.GetBytes(expected), System.Text.Encoding.UTF8.GetBytes(provided)))
        { context.Response.StatusCode = 404; return; }
        await context.Response.WriteAsJsonAsync(new { peer = context.Connection.RemoteIpAddress?.ToString(), scheme = context.Request.Scheme, forwardedProto = context.Request.Headers["X-Forwarded-Proto"].ToString() });
    }

    public static ForwardedHeadersOptions Options(IConfiguration configuration)
    {
        var options = new ForwardedHeadersOptions
        {
            ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto,
            ForwardLimit = 1
        };
        // Preserve framework loopback defaults; never trust every public sender.
        foreach (var item in (configuration["Platform:TrustedProxies"] ?? "").Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            if (!IPAddress.TryParse(item, out var address)) throw new InvalidOperationException("TrustedProxies exige endereços IP explícitos.");
            options.KnownProxies.Add(address);
        }
        return options;
    }
}
