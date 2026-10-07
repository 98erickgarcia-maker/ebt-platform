using Ebt.Domain.Foundation;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Infrastructure.Persistence;

public sealed class EbtDataContext(DbContextOptions<EbtDataContext> options) : DbContext(options)
{
    public DbSet<FoundationRecordEntity> FoundationRecords => Set<FoundationRecordEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var record = modelBuilder.Entity<FoundationRecordEntity>();

        record.ToTable("FoundationRecords");
        record.HasKey(item => item.Id);
        record.Property(item => item.TenantKey).HasMaxLength(64).IsRequired();
        record.Property(item => item.Title).HasMaxLength(200).IsRequired();
        record.Property(item => item.CreatedAtUtc).IsRequired();
        record.Property(item => item.BlobName).HasMaxLength(260);
        record.Property(item => item.FileName).HasMaxLength(120);
        record.Property(item => item.ContentType).HasMaxLength(120);
        record.HasIndex(item => new { item.TenantKey, item.CreatedAtUtc });
    }
}

public sealed class FoundationRecordEntity
{
    public Guid Id { get; set; }
    public string TenantKey { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public DateTimeOffset CreatedAtUtc { get; set; }
    public string? BlobName { get; set; }
    public string? FileName { get; set; }
    public string? ContentType { get; set; }
    public long? AttachmentLength { get; set; }

    public FoundationStoredRecord ToDomain()
    {
        FoundationAttachmentMetadata? attachment = null;

        if (!string.IsNullOrWhiteSpace(BlobName)
            && !string.IsNullOrWhiteSpace(FileName)
            && !string.IsNullOrWhiteSpace(ContentType)
            && AttachmentLength.HasValue)
        {
            attachment = new FoundationAttachmentMetadata(
                BlobName,
                FileName,
                ContentType,
                AttachmentLength.Value);
        }

        return new FoundationStoredRecord(
            Id,
            TenantKey,
            Title,
            attachment,
            CreatedAtUtc);
    }

    public static FoundationRecordEntity FromDomain(FoundationStoredRecord record) =>
        new()
        {
            Id = record.Id,
            TenantKey = record.TenantKey,
            Title = record.Title,
            CreatedAtUtc = record.CreatedAtUtc,
            BlobName = record.Attachment?.BlobName,
            FileName = record.Attachment?.FileName,
            ContentType = record.Attachment?.ContentType,
            AttachmentLength = record.Attachment?.Length
        };
}
