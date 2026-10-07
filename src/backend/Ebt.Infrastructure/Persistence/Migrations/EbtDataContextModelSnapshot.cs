using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;

namespace Ebt.Infrastructure.Persistence.Migrations;

[DbContext(typeof(EbtDataContext))]
public sealed class EbtDataContextModelSnapshot : ModelSnapshot
{
    protected override void BuildModel(ModelBuilder modelBuilder)
    {
        modelBuilder.HasAnnotation("ProductVersion", "10.0.12")
            .HasAnnotation("Relational:MaxIdentifierLength", 128);
        modelBuilder.UseIdentityColumns();
        modelBuilder.Entity("Ebt.Infrastructure.Persistence.FoundationRecordEntity", record =>
        {
            record.Property<Guid>("Id").HasColumnType("uniqueidentifier");
            record.Property<string>("TenantKey").IsRequired().HasMaxLength(64).HasColumnType("nvarchar(64)");
            record.Property<Guid?>("OwnerUserId").HasColumnType("uniqueidentifier");
            record.Property<string>("Title").IsRequired().HasMaxLength(200).HasColumnType("nvarchar(200)");
            record.Property<DateTimeOffset>("CreatedAtUtc").HasColumnType("datetimeoffset");
            record.Property<string>("BlobName").HasMaxLength(260).HasColumnType("nvarchar(260)");
            record.Property<string>("FileName").HasMaxLength(120).HasColumnType("nvarchar(120)");
            record.Property<string>("ContentType").HasMaxLength(120).HasColumnType("nvarchar(120)");
            record.Property<long?>("AttachmentLength").HasColumnType("bigint");
            record.HasKey("TenantKey", "Id");
            record.HasIndex("TenantKey", "CreatedAtUtc");
            record.HasIndex("TenantKey", "OwnerUserId", "CreatedAtUtc");
            record.ToTable("FoundationRecords");
        });
    }
}
