using Ebt.Api;
using Ebt.Api.Security;
using Ebt.Application.Configuration;
using Ebt.Application.Foundation;
using Ebt.Application.Security;
using Ebt.Infrastructure.Foundation;
using Ebt.Infrastructure.Persistence;
using Ebt.Infrastructure.Security;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddOptions<EbtPlatformOptions>()
    .Bind(builder.Configuration.GetSection(EbtPlatformOptions.SectionName))
    .Validate(options =>
        !string.IsNullOrWhiteSpace(options.ProductName)
        && !string.IsNullOrWhiteSpace(options.PlatformName)
        && !string.IsNullOrWhiteSpace(options.EnvironmentName)
        && !string.IsNullOrWhiteSpace(options.DefaultConsumerKey),
        "A configuração base da EBT Platform está incompleta.")
    .ValidateOnStart();

builder.Services.AddSingleton<IEbtConsumerCatalog, SyntheticConsumerCatalog>();
builder.Services.AddSingleton<IEbtIdentityCatalog, SyntheticIdentityCatalog>();
builder.Services.AddEbtAuthentication();
builder.Services.AddQaPersistence(builder.Configuration);

var app = builder.Build();
var options = app.Services.GetRequiredService<IOptions<EbtPlatformOptions>>().Value;
var qaOptions = app.Services.GetRequiredService<IOptions<QaPersistenceOptions>>().Value;

PrivateConfigurationGuard.Validate(options, Environment.GetEnvironmentVariable);
QaTargetGuard.ValidatePrivateConfiguration(qaOptions, Environment.GetEnvironmentVariable);

if (qaOptions.Enabled)
    await app.Services.GetRequiredService<QaPersistenceInitializer>().InitializeAsync();

app.Use(async (context, next) =>
{
    var traceId = SafeDiagnostics.CreateTraceId();
    context.Items[SafeDiagnostics.TraceItemKey] = traceId;
    context.Response.Headers["X-Trace-Id"] = traceId;

    try
    {
        await next();
    }
    catch (Exception error)
    {
        if (context.Response.HasStarted)
            throw;

        var logger = context.RequestServices
            .GetRequiredService<ILoggerFactory>()
            .CreateLogger("Ebt.SafeDiagnostics");

        logger.LogError(
            "Falha não tratada do tipo {ExceptionType}. TraceId {TraceId}.",
            error.GetType().Name,
            traceId);

        context.Response.Clear();
        context.Response.StatusCode = StatusCodes.Status500InternalServerError;
        context.Response.ContentType = "application/problem+json";

        await context.Response.WriteAsJsonAsync(new
        {
            type = "https://ebt.invalid/problems/internal-error",
            title = "Erro interno.",
            status = StatusCodes.Status500InternalServerError,
            traceId
        });
    }
});

app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health", (HttpContext context) => Results.Ok(new
{
    status = "healthy",
    product = options.ProductName,
    platform = options.PlatformName,
    environment = options.EnvironmentName,
    traceId = SafeDiagnostics.GetTraceId(context)
}));

app.MapGet("/health/live", (HttpContext context) => Results.Ok(new
{
    status = "healthy",
    traceId = SafeDiagnostics.GetTraceId(context)
}));

app.MapGet("/health/ready", async (
    QaReadinessProbe probe,
    HttpContext context,
    CancellationToken cancellationToken) =>
{
    var readiness = await probe.CheckAsync(cancellationToken);
    var payload = new
    {
        status = readiness.IsHealthy ? "healthy" : "unhealthy",
        dependencies = new
        {
            sql = readiness.SqlHealthy ? "healthy" : "unhealthy",
            blob = readiness.BlobHealthy ? "healthy" : "unhealthy"
        },
        traceId = SafeDiagnostics.GetTraceId(context)
    };

    return readiness.IsHealthy
        ? Results.Ok(payload)
        : Results.Json(payload, statusCode: StatusCodes.Status503ServiceUnavailable);
});

app.MapGet("/api/foundation/consumers", (IEbtConsumerCatalog catalog) =>
{
    if (!options.SyntheticDataEnabled)
        return Results.NotFound();

    return Results.Ok(catalog.GetAll());
});

app.MapGet("/api/foundation/consumers/{key}", (string key, IEbtConsumerCatalog catalog) =>
{
    if (!options.SyntheticDataEnabled)
        return Results.NotFound();

    var consumer = catalog.Find(key);
    if (consumer is null)
        return Results.NotFound();

    return Results.Ok(consumer);
});

app.MapEbtAuthEndpoints();
app.MapFoundationRecordEndpoints();

app.Run();

public partial class Program { }
