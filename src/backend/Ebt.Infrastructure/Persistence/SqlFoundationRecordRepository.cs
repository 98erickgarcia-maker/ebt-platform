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
        context.FoundationRecords.Add(FoundationRecordEntity.FromDomain(record));
        await context.SaveChangesAsync(cancellationToken);
    }

    public async Task<FoundationStoredRecord?> FindAsync(
        Guid id,
        CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        var entity = await context.FoundationRecords
            .AsNoTracking()
            .SingleOrDefaultAsync(item => item.Id == id, cancellationToken);

        return entity?.ToDomain();
    }

    public async Task<bool> CanConnectAsync(CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        return await context.Database.CanConnectAsync(cancellationToken);
    }

    public async Task EnsureCreatedAsync(CancellationToken cancellationToken = default)
    {
        await using var context = await contextFactory.CreateDbContextAsync(cancellationToken);
        await context.Database.EnsureCreatedAsync(cancellationToken);
    }
}
