using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class ContactCreationLedger : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "ContactCreations",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ContactId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ContactCreations", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_ContactCreations_Contacts_TenantId_ContactId",
                        columns: x => new { x.TenantId, x.ContactId },
                        principalSchema: "ebt_connect",
                        principalTable: "Contacts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_ContactCreations_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_ContactCreations_TenantId_ContactId",
                schema: "ebt_connect",
                table: "ContactCreations",
                columns: new[] { "TenantId", "ContactId" });

            migrationBuilder.CreateIndex(
                name: "IX_ContactCreations_TenantId_OperationKey",
                schema: "ebt_connect",
                table: "ContactCreations",
                columns: new[] { "TenantId", "OperationKey" },
                unique: true);
            migrationBuilder.Sql("""
EXEC(N'ALTER SECURITY POLICY [ebt_connect].[tenant_barrier]
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] BEFORE DELETE;');
""");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
EXEC(N'ALTER SECURITY POLICY [ebt_connect].[tenant_barrier]
DROP FILTER PREDICATE ON [ebt_connect].[ContactCreations],
DROP BLOCK PREDICATE ON [ebt_connect].[ContactCreations] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[ContactCreations] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[ContactCreations] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[ContactCreations] BEFORE DELETE;');
""");
            migrationBuilder.DropTable(
                name: "ContactCreations",
                schema: "ebt_connect");
        }
    }
}
