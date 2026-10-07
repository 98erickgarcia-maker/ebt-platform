using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;

namespace Ebt.Infrastructure.Persistence.Migrations;

[DbContext(typeof(EbtDataContext))]
[Migration("202610070002_TenantResourceScope")]
public sealed class TenantResourceScope : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<Guid>("OwnerUserId", "FoundationRecords", type: "uniqueidentifier", nullable: true);
        migrationBuilder.DropPrimaryKey("PK_FoundationRecords", "FoundationRecords");
        migrationBuilder.AddPrimaryKey("PK_FoundationRecords", "FoundationRecords", new[] { "TenantKey", "Id" });
        migrationBuilder.CreateIndex("IX_FoundationRecords_TenantKey_OwnerUserId_CreatedAtUtc",
            "FoundationRecords", new[] { "TenantKey", "OwnerUserId", "CreatedAtUtc" });
    }

    protected override void Down(MigrationBuilder migrationBuilder) =>
        throw new NotSupportedException("Rollback do isolamento bloqueado. Use restore de QA validado.");
}
