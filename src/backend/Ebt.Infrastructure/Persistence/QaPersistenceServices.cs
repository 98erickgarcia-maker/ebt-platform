using Azure.Storage.Blobs;
using Ebt.Application.Configuration;
using Ebt.Application.Foundation;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace Ebt.Infrastructure.Persistence;

public static class QaPersistenceServices
{
    public static IServiceCollection AddQaPersistence(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services
            .AddOptions<QaPersistenceOptions>()
            .Bind(configuration.GetSection(QaPersistenceOptions.SectionName))
            .Validate(
                options => !options.Enabled
                    || (!string.IsNullOrWhiteSpace(options.SqlHost)
                        && options.SqlPort is > 0 and <= 65535
                        && !string.IsNullOrWhiteSpace(options.SqlUser)
                        && !string.IsNullOrWhiteSpace(options.DatabaseName)
                        && !string.IsNullOrWhiteSpace(options.BlobContainerName)),
                "A configuração pública de persistência QA está incompleta.")
            .ValidateOnStart();

        services.AddSingleton<QaConnectionSettingsProvider>();

        services.AddDbContextFactory<EbtDataContext>((provider, options) =>
        {
            var settings = provider.GetRequiredService<QaConnectionSettingsProvider>().Get();

            options.UseSqlServer(
                settings.SqlConnectionString,
                sql => sql.EnableRetryOnFailure(
                    maxRetryCount: 5,
                    maxRetryDelay: TimeSpan.FromSeconds(2),
                    errorNumbersToAdd: null));
        });

        services.AddSingleton(provider =>
        {
            var settings = provider.GetRequiredService<QaConnectionSettingsProvider>().Get();
            return new BlobServiceClient(settings.BlobConnectionString)
                .GetBlobContainerClient(settings.BlobContainerName);
        });

        services.AddSingleton<IFoundationRecordRepository, SqlFoundationRecordRepository>();
        services.AddSingleton<IFoundationBinaryStore, AzureBlobFoundationBinaryStore>();
        services.AddSingleton<FoundationRecordService>();
        services.AddSingleton<QaPersistenceInitializer>();
        services.AddSingleton<QaReadinessProbe>();

        return services;
    }
}

public sealed class QaPersistenceInitializer(
    IOptions<QaPersistenceOptions> options,
    IFoundationRecordRepository repository,
    IFoundationBinaryStore binaryStore)
{
    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
        if (!options.Value.Enabled)
            return;

        QaTargetGuard.ValidatePrivateConfiguration(
            options.Value,
            Environment.GetEnvironmentVariable);

        Exception? lastError = null;

        for (var attempt = 1; attempt <= 15; attempt++)
        {
            try
            {
                await repository.EnsureCreatedAsync(cancellationToken);
                await binaryStore.EnsureContainerAsync(cancellationToken);
                return;
            }
            catch (Exception error)
            {
                lastError = error;

                if (attempt == 15)
                    break;

                await Task.Delay(TimeSpan.FromSeconds(2), cancellationToken);
            }
        }

        throw new InvalidOperationException(
            "Persistência QA não ficou disponível no tempo esperado.",
            lastError);
    }
}

public sealed record QaReadinessResult(
    bool IsHealthy,
    bool SqlHealthy,
    bool BlobHealthy);

public sealed class QaReadinessProbe(
    IOptions<QaPersistenceOptions> options,
    IServiceProvider services)
{
    public async Task<QaReadinessResult> CheckAsync(
        CancellationToken cancellationToken = default)
    {
        if (!options.Value.Enabled)
            return new QaReadinessResult(true, true, true);

        var repository = services.GetRequiredService<IFoundationRecordRepository>();
        var binaryStore = services.GetRequiredService<IFoundationBinaryStore>();

        var sql = await repository.CanConnectAsync(cancellationToken);
        var blob = await binaryStore.CanConnectAsync(cancellationToken);
        return new QaReadinessResult(sql && blob, sql, blob);
    }
}
