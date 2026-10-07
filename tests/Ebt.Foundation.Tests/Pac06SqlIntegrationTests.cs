using Ebt.Application.Configuration;
using Ebt.Infrastructure.Persistence;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Ebt.Foundation.Tests;

public sealed class Pac06SqlIntegrationTests
{
    [QaFact]
    [Trait("Category", "QaPersistence")]
    public async Task Empty_database_migrates_and_RLS_filters_blocks_and_resets_pool()
    {
        await using var services = BuildServices("rls");
        await services.GetRequiredService<QaPersistenceInitializer>().InitializeAsync();
        var factory = services.GetRequiredService<IDbContextFactory<EbtDataContext>>();
        var id = Guid.NewGuid();
        await using (var orbe = await factory.CreateDbContextAsync())
        {
            orbe.BindTenant("orbe");
            orbe.FoundationRecords.Add(new() { Id = id, TenantKey = "orbe", Title = "A", CreatedAtUtc = DateTimeOffset.UtcNow });
            await orbe.SaveChangesAsync();
            Assert.Single(await orbe.FoundationRecords.AsNoTracking().ToListAsync()); // no LINQ tenant predicate
            orbe.FoundationRecords.Add(new() { Id = Guid.NewGuid(), TenantKey = "nexo", Title = "Forbidden", CreatedAtUtc = DateTimeOffset.UtcNow });
            var denied = await Assert.ThrowsAsync<DbUpdateException>(() => orbe.SaveChangesAsync());
            Assert.Equal(33504, Assert.IsType<SqlException>(denied.InnerException).Number);
            orbe.ChangeTracker.Clear();
            var updateDenied = await Assert.ThrowsAsync<SqlException>(() => orbe.Database.ExecuteSqlRawAsync(
                "UPDATE dbo.FoundationRecords SET TenantKey=N'nexo' WHERE TenantKey=N'orbe';"));
            Assert.Equal(33504, updateDenied.Number);
            await orbe.Database.OpenConnectionAsync();
            var relabelDenied = await Assert.ThrowsAsync<SqlException>(() => orbe.Database.ExecuteSqlRawAsync(
                "EXEC sys.sp_set_session_context @key=N'ebt:tenant', @value=N'nexo';"));
            Assert.Equal(15664, relabelDenied.Number);
        }
        await using (var nexo = await factory.CreateDbContextAsync())
        {
            nexo.BindTenant("nexo");
            Assert.Empty(await nexo.FoundationRecords.AsNoTracking().ToListAsync());
            nexo.FoundationRecords.Add(new() { Id = id, TenantKey = "nexo", Title = "B", CreatedAtUtc = DateTimeOffset.UtcNow });
            await nexo.SaveChangesAsync(); // same ID in different tenant succeeds
        }
        // Force the same physical pooled session for A/B/null, independently of EF.
        var settings = services.GetRequiredService<QaConnectionSettingsProvider>().Get();
        var pool = new SqlConnectionStringBuilder(settings.SqlConnectionString) { MaxPoolSize = 1, ApplicationName = "EBT PAC06 pool proof" };
        int? spid = null;
        foreach (var tenant in new string?[] { "orbe", "nexo", null, "orbe" })
        {
            var options = new DbContextOptionsBuilder<EbtDataContext>().UseSqlServer(pool.ConnectionString)
                .AddInterceptors(new SqlTenantConnectionInterceptor()).Options;
            await using var context = new EbtDataContext(options);
            if (tenant is not null) context.BindTenant(tenant);
            await context.Database.OpenConnectionAsync();
            await using var command = context.Database.GetDbConnection().CreateCommand();
            command.CommandText = "SELECT @@SPID";
            var currentSpid = Convert.ToInt32(await command.ExecuteScalarAsync());
            if (spid is not null) Assert.Equal(spid, currentSpid);
            spid = currentSpid;
            var rows = await context.FoundationRecords.AsNoTracking().ToListAsync();
            if (tenant is null) Assert.Empty(rows);
            else Assert.Equal(tenant, Assert.Single(rows).TenantKey);
        }
        await using (var duplicate = await factory.CreateDbContextAsync())
        {
            duplicate.BindTenant("orbe");
            duplicate.FoundationRecords.Add(new() { Id = id, TenantKey = "orbe", Title = "Duplicate", CreatedAtUtc = DateTimeOffset.UtcNow });
            var denied = await Assert.ThrowsAsync<DbUpdateException>(() => duplicate.SaveChangesAsync());
            Assert.Contains(Assert.IsType<SqlException>(denied.InnerException).Number, new[] { 2627, 2601 });
        }
        await using var unscoped = await factory.CreateDbContextAsync();
        Assert.Empty(await unscoped.FoundationRecords.AsNoTracking().ToListAsync());
        Assert.Equal(3, (await unscoped.Database.GetAppliedMigrationsAsync()).Count());
        await unscoped.Database.MigrateAsync();
        Assert.Equal(3, (await unscoped.Database.GetAppliedMigrationsAsync()).Count());
    }

    [QaFact]
    [Trait("Category", "QaPersistence")]
    public async Task Previous_EnsureCreated_snapshot_is_adopted_without_losing_record_or_attachment_metadata()
    {
        await using var services = BuildServices("legacy");
        var factory = services.GetRequiredService<IDbContextFactory<EbtDataContext>>();
        await CreateLegacyDatabase(services);
        await using (var legacy = await factory.CreateDbContextAsync())
            await legacy.Database.MigrateAsync();
        await using var migrated = await factory.CreateDbContextAsync();
        migrated.BindTenant("orbe");
        var record = Assert.Single(await migrated.FoundationRecords.AsNoTracking().ToListAsync());
        Assert.Equal("Anterior", record.Title);
        Assert.Equal("orbe/previous/prova.txt", record.BlobName);
        Assert.Equal(9, record.AttachmentLength);
        Assert.Null(record.OwnerUserId); // no invented owner for old records
        Assert.Equal(3, (await migrated.Database.GetAppliedMigrationsAsync()).Count());
    }

    [QaFact]
    [Trait("Category", "QaPersistence")]
    public async Task Legacy_schema_with_missing_index_is_rejected_without_erasing_record()
    {
        await using var services = BuildServices("drift");
        await CreateLegacyDatabase(services);
        var factory = services.GetRequiredService<IDbContextFactory<EbtDataContext>>();
        await using var context = await factory.CreateDbContextAsync();
        await context.Database.ExecuteSqlRawAsync("DROP INDEX IX_FoundationRecords_TenantKey_CreatedAtUtc ON dbo.FoundationRecords;");
        var denied = await Assert.ThrowsAsync<SqlException>(() => context.Database.MigrateAsync());
        Assert.Equal(51000, denied.Number);
        Assert.Equal("Anterior", Assert.Single(await context.FoundationRecords.FromSqlRaw(
            "SELECT *, CAST(NULL AS uniqueidentifier) AS OwnerUserId FROM dbo.FoundationRecords").AsNoTracking().ToListAsync()).Title);
        Assert.Empty(await context.Database.GetAppliedMigrationsAsync());
    }

    private static async Task CreateLegacyDatabase(ServiceProvider services)
    {
        var factory = services.GetRequiredService<IDbContextFactory<EbtDataContext>>();
        var settings = services.GetRequiredService<QaConnectionSettingsProvider>().Get();
        var connection = new SqlConnectionStringBuilder(settings.SqlConnectionString);
        var database = connection.InitialCatalog;
        connection.InitialCatalog = "master";
        await using (var master = new SqlConnection(connection.ConnectionString))
        {
            await master.OpenAsync();
            await using var command = master.CreateCommand();
            // DatabaseName passed QaTargetGuard: letters/digits/underscore only, QA prefix.
            command.CommandText = $"CREATE DATABASE [{database}]";
            await command.ExecuteNonQueryAsync();
        }
        await using (var legacy = await factory.CreateDbContextAsync())
        {
            await legacy.Database.ExecuteSqlRawAsync("""
                CREATE TABLE dbo.FoundationRecords (
                    Id uniqueidentifier NOT NULL CONSTRAINT PK_FoundationRecords PRIMARY KEY,
                    TenantKey nvarchar(64) NOT NULL, Title nvarchar(200) NOT NULL,
                    CreatedAtUtc datetimeoffset NOT NULL, BlobName nvarchar(260) NULL,
                    FileName nvarchar(120) NULL, ContentType nvarchar(120) NULL, AttachmentLength bigint NULL);
                CREATE INDEX IX_FoundationRecords_TenantKey_CreatedAtUtc ON dbo.FoundationRecords(TenantKey, CreatedAtUtc);
                INSERT dbo.FoundationRecords VALUES ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',N'orbe',N'Anterior',SYSDATETIMEOFFSET(),N'orbe/previous/prova.txt',N'prova.txt',N'text/plain',9);
                """);
        }
    }

    internal static ServiceProvider BuildServices(string suffix) => new ServiceCollection().AddLogging()
        .AddQaPersistence(Configuration(suffix)).BuildServiceProvider();

    internal static IConfiguration Configuration(string suffix)
    {
        suffix += "_" + Guid.NewGuid().ToString("N")[..8];
        var configuration = new ConfigurationBuilder().AddEnvironmentVariables().Build();
        return new ConfigurationBuilder().AddConfiguration(configuration).AddInMemoryCollection(new Dictionary<string, string?>
        {
            ["QaPersistence:DatabaseName"] = configuration["QaPersistence:DatabaseName"] + "_pac06_" + suffix,
            ["QaPersistence:BlobContainerName"] = configuration["QaPersistence:BlobContainerName"] + "-p6-" + suffix.Replace('_', '-')
        }).Build();
    }
}
