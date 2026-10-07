using Ebt.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Foundation.Tests;

public sealed class Pac06BoundaryTests
{
    [Fact]
    public void Record_identity_and_scope_are_tenant_aware()
    {
        using var context = new EbtDataContext(new DbContextOptionsBuilder<EbtDataContext>()
            .UseSqlServer("Server=localhost;Database=EbtQa_model;Integrated Security=true;TrustServerCertificate=true")
            .Options);
        var entity = context.Model.FindEntityType(typeof(FoundationRecordEntity))!;
        Assert.Equal(new[] { "TenantKey", "Id" }, entity.FindPrimaryKey()!.Properties.Select(p => p.Name));
        Assert.NotNull(entity.FindProperty("OwnerUserId"));
        Assert.Contains(entity.GetIndexes(), index => index.Properties.Select(p => p.Name)
            .SequenceEqual(new[] { "TenantKey", "OwnerUserId", "CreatedAtUtc" }));
        Assert.False(context.Database.HasPendingModelChanges());
    }
}
