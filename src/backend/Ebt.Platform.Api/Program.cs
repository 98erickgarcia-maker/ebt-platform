using Ebt.Platform.Api;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;
using System.Threading.RateLimiting;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
var runtimeFile = Environment.GetEnvironmentVariable("EBT_RUNTIME_CONFIG");
if (!string.IsNullOrWhiteSpace(runtimeFile)) builder.Configuration.AddJsonFile(runtimeFile, optional: false, reloadOnChange: false).AddEnvironmentVariables();
var connection = builder.Configuration.GetConnectionString("Platform") ?? throw new InvalidOperationException("Configure ConnectionStrings__Platform para um ambiente EBT autorizado.");
KeyProtection.Configure(builder.Services, builder.Configuration, builder.Environment.IsDevelopment());
builder.Services.AddScoped<AccessScope>();
builder.Services.ConfigureHttpJsonOptions(o => o.SerializerOptions.UnmappedMemberHandling = System.Text.Json.Serialization.JsonUnmappedMemberHandling.Disallow);
builder.Services.AddScoped<TenantSqlContext>();
builder.Services.AddDbContext<PlatformDb>((services, o) => o.UseSqlServer(connection, sql => sql.MigrationsHistoryTable("__EFMigrationsHistory", "ebt_connect")).AddInterceptors(services.GetRequiredService<TenantSqlContext>()));
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(o =>
{
    o.Cookie.Name = builder.Environment.IsDevelopment() ? "ebt.session" : "__Host-ebt.session";
    o.Cookie.HttpOnly = true; o.Cookie.SameSite = SameSiteMode.Strict;
    o.Cookie.SecurePolicy = builder.Environment.IsDevelopment() ? CookieSecurePolicy.SameAsRequest : CookieSecurePolicy.Always;
    o.ExpireTimeSpan = TimeSpan.FromHours(8); o.SlidingExpiration = false;
    o.Events.OnRedirectToLogin = c => { c.Response.StatusCode = 401; return Task.CompletedTask; };
    o.Events.OnRedirectToAccessDenied = c => { c.Response.StatusCode = 403; return Task.CompletedTask; };
});
builder.Services.AddAntiforgery(o => { o.HeaderName = "X-CSRF-TOKEN"; o.Cookie.Name = "ebt.csrf"; o.Cookie.SameSite = SameSiteMode.Strict; o.Cookie.SecurePolicy = builder.Environment.IsDevelopment() ? CookieSecurePolicy.SameAsRequest : CookieSecurePolicy.Always; });
builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = 429;
    o.AddPolicy("auth", c => RateLimitPartition.GetFixedWindowLimiter(c.Connection.RemoteIpAddress?.ToString() ?? "unknown", _ => new FixedWindowRateLimiterOptions { PermitLimit = 15, Window = TimeSpan.FromMinutes(1), QueueLimit = 0 }));
});
builder.WebHost.ConfigureKestrel(o => o.Limits.MaxRequestBodySize = 3 * 1024 * 1024);
builder.Services.AddHttpClient("meta", c => { c.BaseAddress = new Uri("https://graph.facebook.com/"); c.Timeout = TimeSpan.FromSeconds(20); });
builder.Services.AddHttpClient("wazvox", c => { c.BaseAddress = new Uri("https://app.wazvox.com/api/v1/"); c.Timeout = TimeSpan.FromSeconds(20); }).ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler { AllowAutoRedirect = false });
builder.Services.AddSingleton<WorkPulse>();
builder.Services.AddHostedService<ConnectWorker>();
var app = builder.Build();
app.Use((http, next) => ProxyConfiguration.Audit(http, builder.Configuration, next));
app.UseForwardedHeaders(ProxyConfiguration.Options(builder.Configuration));
if (args.Contains("--verify-recovery"))
{
    if (!app.Environment.IsDevelopment()) throw new InvalidOperationException("Ensaio somente em Development.");
    using var service = app.Services.CreateScope();
    await RecoveryChecks.Run(service.ServiceProvider.GetRequiredService<PlatformDb>(), service.ServiceProvider.GetRequiredService<AccessScope>(), service.ServiceProvider.GetRequiredService<IDataProtectionProvider>(), builder.Configuration);
    return;
}
if (args.Contains("--bootstrap") || args.Contains("--configure-meta") || args.Contains("--configure-wazvox"))
{
    using var service = app.Services.CreateScope();
    var db = service.ServiceProvider.GetRequiredService<PlatformDb>();
    var scope = service.ServiceProvider.GetRequiredService<AccessScope>();
    if (args.Contains("--bootstrap")) await Provisioning.Bootstrap(db, scope, builder.Configuration);
    else if (args.Contains("--configure-wazvox")) await Provisioning.ConfigureWazVox(db, scope, builder.Configuration, service.ServiceProvider.GetRequiredService<IHttpClientFactory>().CreateClient("wazvox"));
    else await Provisioning.ConfigureMeta(db, scope, builder.Configuration);
    return;
}
if (args.Contains("--verify-sql-qa"))
{
    if (!app.Environment.IsDevelopment()) throw new InvalidOperationException("Verificação sintética apenas em Development.");
    await QaSqlChecks.Run(connection, builder.Configuration["Qa:SqlReport"] ?? throw new InvalidOperationException("Configure destino do relatório QA.")); return;
}
if (args.Contains("--inspect-azure"))
{
    await SqlInspection.Run(connection, builder.Configuration["Platform:InspectionOutput"] ?? throw new InvalidOperationException("Informe destino dos metadados sanitizados.")); return;
}
if (args.Contains("--platform-database"))
{
    await PlatformDatabaseAdmin.Run(connection, builder.Configuration); return;
}
if (args.Contains("--apply-reviewed-schema"))
{
    await SqlDeployment.Run(connection, builder.Configuration); return;
}
if (args.Contains("--schema"))
{
    using var scoped = app.Services.CreateScope(); var db = scoped.ServiceProvider.GetRequiredService<PlatformDb>();
    Console.Write(db.Database.GenerateCreateScript()); return;
}
if (args.Contains("--init-qa"))
{
    if (!app.Environment.IsDevelopment()) throw new InvalidOperationException("Massa QA permitida somente em Development.");
    var sql = new Microsoft.Data.SqlClient.SqlConnectionStringBuilder(connection);
    if (!sql.InitialCatalog.StartsWith("EbtPlatformQa_", StringComparison.Ordinal) || sql.DataSource is not ("localhost" or "." or "127.0.0.1")) throw new InvalidOperationException("Inicialização QA exige banco local exclusivo EbtPlatformQa_.");
    using var scoped = app.Services.CreateScope(); var db = scoped.ServiceProvider.GetRequiredService<PlatformDb>();
    scoped.ServiceProvider.GetRequiredService<AccessScope>().System = true;
    await db.Database.MigrateAsync();
    await QaSeed.Run(db, builder.Configuration); return;
}
app.Use(async (http, next) =>
{
    http.Response.Headers.CacheControl = "no-cache, no-store";
    http.Response.Headers.Pragma = "no-cache";
    http.Response.Headers["X-Content-Type-Options"] = "nosniff";
    http.Response.Headers["Referrer-Policy"] = "same-origin";
    http.Response.Headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'";
    http.Response.Headers["X-Request-ID"] = http.TraceIdentifier;
    try { await next(http); }
    catch (Exception ex)
    {
        if (http.Response.HasStarted) throw;
        var fault = ex as ApiFault;
        var status = fault?.Status ?? (ex is DbUpdateConcurrencyException ? 409 : ex is BadHttpRequestException or JsonException ? 400 : 503);
        var code = fault?.Code ?? (status == 409 ? "stale_version" : status == 400 ? "invalid_input" : "service_unavailable");
        // No SQL details, provider text, tokens, envelopes or personal content in logs/responses.
        if (fault == null && status == 503) app.Logger.LogError("Request {TraceId} failed: {Type}", http.TraceIdentifier, ex.GetType().Name);
        http.Response.StatusCode = status; http.Response.ContentType = "application/problem+json";
        await http.Response.WriteAsJsonAsync(new { type = "https://ebtenterprise.com.br/problems/" + code, title = fault?.Message ?? "A operação não pôde ser concluída. Tente novamente ou informe o código de atendimento.", status, code, traceId = http.TraceIdentifier }, options: (JsonSerializerOptions?)null, contentType: "application/problem+json", cancellationToken: http.RequestAborted);
    }
});
if (!app.Environment.IsDevelopment())
{
    app.UseHsts();
    app.UseWhen(http => ProxyConfiguration.RequiresHttpsRedirect(http.Request.Path), branch => branch.UseHttpsRedirection());
}
app.UseDefaultFiles(); app.UseStaticFiles(); app.UseRouting(); app.UseRateLimiter(); app.UseAuthentication();
app.Use(Security.ValidateContext);
app.MapGet("/health/live", () => Results.Ok(new { status = "alive", service = "EBT Platform", application = "Connect", version = "0.2.0" }));
app.MapGet("/health/ready", async (PlatformDb db) =>
{
    try { await db.Tenants.AsNoTracking().OrderBy(x => x.Id).Select(x => x.Id).Take(1).ToListAsync(); var catalog = await PlatformCatalog.Read(db); if (!catalog.Any(x => x.Code == "connect")) return Results.StatusCode(503); return Results.Ok(new { status = "ready", schema = "ebt_connect", platformSchema = "ebt_platform", version = "0.2.0" }); }
    catch { return Results.StatusCode(503); }
});
PlatformCatalog.Map(app); Security.Map(app); CrmEndpoints.Map(app); MessagingEndpoints.Map(app); DocumentEndpoints.Map(app);
WazVoxEndpoints.Map(app);
await app.RunAsync();

public partial class Program;
