using System.Text;
using Ebt.Application.Foundation;
using Ebt.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Ebt.Foundation.Tests;

public sealed class QaPersistenceIntegrationTests
{
    [Fact]
    [Trait("Category", "QaPersistence")]
    public async Task Qa_persists_metadata_and_binary_in_separate_stores_and_scopes_tenant_reads()
    {
        if (!string.Equals(
            Environment.GetEnvironmentVariable("EBT_QA_E2E"),
            "1",
            StringComparison.Ordinal))
            return;

        var configuration = new ConfigurationBuilder()
            .AddEnvironmentVariables()
            .Build();

        await using var services = new ServiceCollection()
            .AddLogging()
            .AddQaPersistence(configuration)
            .BuildServiceProvider();

        await services
            .GetRequiredService<QaPersistenceInitializer>()
            .InitializeAsync();

        var service = services.GetRequiredService<FoundationRecordService>();
        var content = Encoding.UTF8.GetBytes("EBT QA persistence proof");

        var saved = await service.SaveAsync(new FoundationRecordDraft(
            "orbe",
            "Registro sintético G1",
            "prova.txt",
            "text/plain",
            content));

        var reloaded = await service.GetAsync(saved.Id, "orbe");
        Assert.NotNull(reloaded);
        Assert.Equal("orbe", reloaded.TenantKey);
        Assert.Equal("Registro sintético G1", reloaded.Title);
        Assert.NotNull(reloaded.Attachment);
        Assert.Equal(content.LongLength, reloaded.Attachment.Length);

        Assert.Null(await service.GetAsync(saved.Id, "nexo"));
        Assert.Empty(await service.ListAsync("nexo"));
        Assert.Single(await service.ListAsync("orbe"));

        var download = await service.DownloadAsync(saved.Id, "orbe");
        Assert.NotNull(download);
        Assert.Equal("prova.txt", download.FileName);
        Assert.Equal("text/plain", download.ContentType);
        Assert.Equal(content, download.Content);
        Assert.Null(await service.DownloadAsync(saved.Id, "nexo"));

        var contextFactory = services.GetRequiredService<IDbContextFactory<EbtDataContext>>();
        await using var context = await contextFactory.CreateDbContextAsync();

        var entity = await context.FoundationRecords
            .AsNoTracking()
            .SingleAsync(item => item.Id == saved.Id);

        Assert.Equal(reloaded.Attachment.BlobName, entity.BlobName);
        Assert.Equal(reloaded.Attachment.Length, entity.AttachmentLength);
        Assert.DoesNotContain(
            context.Model
                .FindEntityType(typeof(FoundationRecordEntity))!
                .GetProperties(),
            property => property.ClrType == typeof(byte[]));

        var readiness = await services
            .GetRequiredService<QaReadinessProbe>()
            .CheckAsync();

        Assert.True(readiness.IsHealthy);
        Assert.True(readiness.SqlHealthy);
        Assert.True(readiness.BlobHealthy);
    }
}
