using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class ConnectMail : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "MailDrafts",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ContactId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Recipient = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Body = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Origin = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ApprovedBy = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    ApprovedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    DocumentId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    DocumentNumber = table.Column<int>(type: "int", nullable: true),
                    CreationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    CreationHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Diagnostic = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    AttemptedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MailDrafts", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_MailDrafts_Contacts_TenantId_ContactId",
                        columns: x => new { x.TenantId, x.ContactId },
                        principalSchema: "ebt_connect",
                        principalTable: "Contacts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_MailDrafts_Documents_TenantId_DocumentId",
                        columns: x => new { x.TenantId, x.DocumentId },
                        principalSchema: "ebt_connect",
                        principalTable: "Documents",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_MailDrafts_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "MailQuotas",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Day = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    Used = table.Column<int>(type: "int", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MailQuotas", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_MailQuotas_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "MailSettings",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    IntervalSeconds = table.Column<int>(type: "int", nullable: false),
                    DailyCap = table.Column<int>(type: "int", nullable: false),
                    Paused = table.Column<bool>(type: "bit", nullable: false),
                    NextSendAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MailSettings", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_MailSettings_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "MailSuppressions",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Value = table.Column<string>(type: "nvarchar(254)", maxLength: 254, nullable: false),
                    Reason = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MailSuppressions", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_MailSuppressions_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "MailTemplates",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Body = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    CreationHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MailTemplates", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_MailTemplates_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "MailRevisions",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    DraftId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Body = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Recipient = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Reason = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    At = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MailRevisions", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_MailRevisions_MailDrafts_TenantId_DraftId",
                        columns: x => new { x.TenantId, x.DraftId },
                        principalSchema: "ebt_connect",
                        principalTable: "MailDrafts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_MailRevisions_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_MailDrafts_TenantId_ContactId",
                schema: "ebt_connect",
                table: "MailDrafts",
                columns: new[] { "TenantId", "ContactId" });

            migrationBuilder.CreateIndex(
                name: "IX_MailDrafts_TenantId_CreationKey",
                schema: "ebt_connect",
                table: "MailDrafts",
                columns: new[] { "TenantId", "CreationKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MailDrafts_TenantId_DocumentId",
                schema: "ebt_connect",
                table: "MailDrafts",
                columns: new[] { "TenantId", "DocumentId" });

            migrationBuilder.CreateIndex(
                name: "IX_MailQuotas_TenantId_Day",
                schema: "ebt_connect",
                table: "MailQuotas",
                columns: new[] { "TenantId", "Day" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MailRevisions_TenantId_DraftId_OperationKey",
                schema: "ebt_connect",
                table: "MailRevisions",
                columns: new[] { "TenantId", "DraftId", "OperationKey" },
                unique: true,
                filter: "[OperationKey] <> ''");

            migrationBuilder.CreateIndex(
                name: "IX_MailSettings_TenantId",
                schema: "ebt_connect",
                table: "MailSettings",
                column: "TenantId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MailSuppressions_TenantId_Value",
                schema: "ebt_connect",
                table: "MailSuppressions",
                columns: new[] { "TenantId", "Value" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MailTemplates_TenantId_CreationKey",
                schema: "ebt_connect",
                table: "MailTemplates",
                columns: new[] { "TenantId", "CreationKey" },
                unique: true);
            migrationBuilder.Sql("""
EXEC(N'ALTER SECURITY POLICY [ebt_connect].[tenant_barrier]
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] BEFORE DELETE;');
""");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
ALTER SECURITY POLICY [ebt_connect].[tenant_barrier]
DROP FILTER PREDICATE ON [ebt_connect].[MailDrafts],
DROP BLOCK PREDICATE ON [ebt_connect].[MailDrafts] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[MailDrafts] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailDrafts] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailDrafts] BEFORE DELETE,
DROP FILTER PREDICATE ON [ebt_connect].[MailQuotas],
DROP BLOCK PREDICATE ON [ebt_connect].[MailQuotas] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[MailQuotas] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailQuotas] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailQuotas] BEFORE DELETE,
DROP FILTER PREDICATE ON [ebt_connect].[MailRevisions],
DROP BLOCK PREDICATE ON [ebt_connect].[MailRevisions] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[MailRevisions] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailRevisions] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailRevisions] BEFORE DELETE,
DROP FILTER PREDICATE ON [ebt_connect].[MailSettings],
DROP BLOCK PREDICATE ON [ebt_connect].[MailSettings] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[MailSettings] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailSettings] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailSettings] BEFORE DELETE,
DROP FILTER PREDICATE ON [ebt_connect].[MailSuppressions],
DROP BLOCK PREDICATE ON [ebt_connect].[MailSuppressions] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[MailSuppressions] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailSuppressions] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailSuppressions] BEFORE DELETE,
DROP FILTER PREDICATE ON [ebt_connect].[MailTemplates],
DROP BLOCK PREDICATE ON [ebt_connect].[MailTemplates] AFTER INSERT,
DROP BLOCK PREDICATE ON [ebt_connect].[MailTemplates] AFTER UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailTemplates] BEFORE UPDATE,
DROP BLOCK PREDICATE ON [ebt_connect].[MailTemplates] BEFORE DELETE;
""");
            migrationBuilder.DropTable(
                name: "MailQuotas",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "MailRevisions",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "MailSettings",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "MailSuppressions",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "MailTemplates",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "MailDrafts",
                schema: "ebt_connect");
        }
    }
}
