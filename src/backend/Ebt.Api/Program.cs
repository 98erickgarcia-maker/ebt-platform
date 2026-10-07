using System.Text;
using Ebt.Application.Configuration;
using Ebt.Application.Foundation;
using Ebt.Infrastructure.Foundation;
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

var qaOptions = builder.Configuration
    .GetSection(QaInfrastructureOptions.SectionName)
    .Get<QaInfrastructureOptions>() ?? new QaInfrastructureOptions();

if (qaOptions.Enabled)
{
    QaInfrastructureGuard.Validate(qaOptions, builder.Environment.EnvironmentName);
    builder.Services.AddSingleton(qaOptions);
    builder.Services.AddSingleton<IQaProbeService, QaProbeService>();
}

var app = builder.Build();
var options = app.Services.GetRequiredService<IOptions<EbtPlatformOptions>>().Value;
PrivateConfigurationGuard.Validate(options, Environment.GetEnvironmentVariable);

if (qaOptions.Enabled)
{
    var qaProbe = app.Services.GetRequiredService<IQaProbeService>();
    await qaProbe.InitializeAsync();
}

app.Use(async (context, next) =>
{
    context.Response.Headers["X-Trace-Id"] = context.TraceIdentifier;
    await next();
});

app.MapGet("/health", async (IServiceProvider services, HttpContext context, CancellationToken cancellationToken) =>
{
    string database;
    string storage;

    if (qaOptions.Enabled)
    {
        var probe = services.GetRequiredService<IQaProbeService>();
        database = await probe.CheckDatabaseAsync(cancellationToken) ? "healthy" : "unhealthy";
        storage = await probe.CheckStorageAsync(cancellationToken) ? "healthy" : "unhealthy";
    }
    else
    {
        database = "not-configured";
        storage = "not-configured";
    }

    var status = database == "unhealthy" || storage == "unhealthy"
        ? "unhealthy"
        : "healthy";

    return Results.Json(new
    {
        status,
        product = options.ProductName,
        platform = options.PlatformName,
        environment = options.EnvironmentName,
        traceId = context.TraceIdentifier,
        dependencies = new
        {
            qaDatabase = database,
            qaStorage = storage
        }
    }, statusCode: status == "healthy" ? StatusCodes.Status200OK : StatusCodes.Status503ServiceUnavailable);
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

if (qaOptions.Enabled)
{
    app.MapPost("/api/foundation/qa/probes", async (
        QaProbeRequest request,
        IQaProbeService probe,
        HttpContext context,
        CancellationToken cancellationToken) =>
    {
        try
        {
            var result = await probe.SaveAsync(
                request.ConsumerKey,
                request.FileName,
                Encoding.UTF8.GetBytes(request.Content),
                cancellationToken);

            return Results.Created($"/api/foundation/qa/probes/{result.Id}", new
            {
                result.Id,
                result.ConsumerKey,
                result.FileName,
                result.Sha256,
                result.Length,
                result.CreatedAt,
                traceId = context.TraceIdentifier
            });
        }
        catch (ArgumentException)
        {
            return Results.Problem(
                statusCode: StatusCodes.Status400BadRequest,
                title: "Entrada QA inválida.",
                extensions: new Dictionary<string, object?>
                {
                    ["traceId"] = context.TraceIdentifier
                });
        }
    });

    app.MapGet("/api/foundation/qa/probes/{id:guid}", async (
        Guid id,
        IQaProbeService probe,
        HttpContext context,
        CancellationToken cancellationToken) =>
    {
        try
        {
            var result = await probe.ReadAsync(id, cancellationToken);
            if (result is null)
                return Results.NotFound();

            return Results.Ok(new
            {
                result.Metadata.Id,
                result.Metadata.ConsumerKey,
                result.Metadata.FileName,
                result.Metadata.Sha256,
                result.Metadata.Length,
                result.Metadata.CreatedAt,
                contentBase64 = Convert.ToBase64String(result.Content),
                traceId = context.TraceIdentifier
            });
        }
        catch (InvalidDataException)
        {
            return Results.Problem(
                statusCode: StatusCodes.Status500InternalServerError,
                title: "Persistência QA inconsistente.",
                extensions: new Dictionary<string, object?>
                {
                    ["traceId"] = context.TraceIdentifier
                });
        }
    });
}

app.Run();

public sealed record QaProbeRequest(string ConsumerKey, string FileName, string Content);

public partial class Program { }
