using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace Ebt.Platform.Api;

public sealed class DesignFactory : IDesignTimeDbContextFactory<PlatformDb>
{
    public PlatformDb CreateDbContext(string[] args) => new(new DbContextOptionsBuilder<PlatformDb>()
        .UseSqlServer("Server=localhost;Database=EbtPlatformQa_Design;Integrated Security=True;Encrypt=True;TrustServerCertificate=True",
            sql => sql.MigrationsHistoryTable("__EFMigrationsHistory", "ebt_connect")).Options, new AccessScope());
}
