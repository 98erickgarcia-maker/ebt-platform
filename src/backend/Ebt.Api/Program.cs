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

var app = builder.Build();
var options = app.Services.GetRequiredService<IOptions<EbtPlatformOptions>>().Value;
PrivateConfigurationGuard.Validate(options, Environment.GetEnvironmentVariable);

app.MapGet("/health", () => Results.Ok(new
{
    status = "healthy",
    product = options.ProductName,
    platform = options.PlatformName,
    environment = options.EnvironmentName
}));

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

app.Run();

public partial class Program { }
