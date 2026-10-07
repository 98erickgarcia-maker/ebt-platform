using Microsoft.EntityFrameworkCore;

namespace Ebt.Infrastructure.Foundation;

public sealed class QaFoundationDbContext(DbContextOptions<QaFoundationDbContext> options)
    : DbContext(options)
{
    public DbSet<QaProbeMetadataEntity> ProbeMetadata => Set<QaProbeMetadataEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var entity = modelBuilder.Entity<QaProbeMetadataEntity>();
        entity.ToTable("QaProbeMetadata");
        entity.HasKey(item => item.Id);
        entity.Property(item => item.ConsumerKey).HasMaxLength(64).IsRequired();
        entity.Property(item => item.FileName).HasMaxLength(255).IsRequired();
        entity.Property(item => item.StorageKey).HasMaxLength(80).IsRequired();
        entity.Property(item => item.Sha256).HasMaxLength(64).IsRequired();
        entity.HasIndex(item => new { item.ConsumerKey, item.CreatedAt });
    }
}

public sealed class QaProbeMetadataEntity
{
    public Guid Id { get; set; }
    public string ConsumerKey { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string StorageKey { get; set; } = string.Empty;
    public string Sha256 { get; set; } = string.Empty;
    public long Length { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
}
