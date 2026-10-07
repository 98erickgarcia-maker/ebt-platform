using Ebt.Application.Foundation;
using Ebt.Domain.Foundation;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Infrastructure.Persistence;

public sealed class SqlFoundationRecordRepository(
    IDbContextFactory<EbtDataContext> contextFactory) : IFoundationRecordRepository
{
    public async Task AddAsync(
        FoundationStoredRecord record,
        CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        context.BindTenant(record.TenantKey);
        context.FoundationRecords.Add(FoundationRecordEntity.FromDomain(record));
        await context.SaveChangesAsync(cancellationToken);
    }

    public async Task<FoundationStoredRecord?> FindAsync(
        Guid id,
        string tenantKey,
        CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        context.BindTenant(tenantKey);
        var entity = await context.FoundationRecords
            .AsNoTracking()
            .SingleOrDefaultAsync(
                item => item.Id == id && item.TenantKey == tenantKey,
                cancellationToken);

        return entity?.ToDomain();
    }

    public async Task<IReadOnlyList<FoundationStoredRecord>> ListAsync(
        string tenantKey,
        CancellationToken cancellationToken = default,
        Guid? ownerUserId = null)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        context.BindTenant(tenantKey);
        var entities = await context.FoundationRecords
            .AsNoTracking()
            .Where(item => item.TenantKey == tenantKey && (!ownerUserId.HasValue || item.OwnerUserId == ownerUserId))
            .OrderByDescending(item => item.CreatedAtUtc)
            .ThenBy(item => item.Id)
            .Take(100)
            .ToListAsync(cancellationToken);

        return entities.Select(item => item.ToDomain()).ToArray();
    }

    public async Task<bool> CanConnectAsync(CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        return await context.Database.CanConnectAsync(cancellationToken);
    }

    public async Task EnsureCreatedAsync(CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        await context.Database.MigrateAsync(cancellationToken);
    }
}
