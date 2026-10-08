using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class InitialConnect : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "ebt_connect");

            migrationBuilder.CreateTable(
                name: "Receipts",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    AppKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    BodyHash = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false),
                    ProtectedBody = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Diagnostic = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ReceivedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Receipts", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Tenants",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Product = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Tenants", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Users",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Email = table.Column<string>(type: "nvarchar(254)", maxLength: 254, nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PasswordHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Stamp = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false),
                    FailedLogins = table.Column<int>(type: "int", nullable: false),
                    LockedUntil = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Users", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Audit",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    Action = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ResourceId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    TraceId = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    At = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Audit", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Audit_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Connections",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Provider = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    AppKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    AccountId = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PhoneNumberId = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SecretRef = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    OperatorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Connections", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Connections_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Imports",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Content = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    ResultJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ExpiresAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Imports", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Imports_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Invitations",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Email = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Role = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    TokenHash = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false),
                    ExpiresAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    UsedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Invitations", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Invitations_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Organizations",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ExternalKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Organizations", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Organizations_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Credentials",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    TokenHash = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false),
                    ExpiresAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Credentials", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Credentials_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Credentials_Users_UserId",
                        column: x => x.UserId,
                        principalSchema: "ebt_connect",
                        principalTable: "Users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Memberships",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Role = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Active = table.Column<bool>(type: "bit", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Memberships", x => new { x.TenantId, x.Id });
                    table.UniqueConstraint("AK_Memberships_TenantId_UserId", x => new { x.TenantId, x.UserId });
                    table.ForeignKey(
                        name: "FK_Memberships_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Memberships_Users_UserId",
                        column: x => x.UserId,
                        principalSchema: "ebt_connect",
                        principalTable: "Users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "DeliveryEvents",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ConnectionId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ProviderId = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Status = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    OccurredAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    EventKey = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DeliveryEvents", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_DeliveryEvents_Connections_TenantId_ConnectionId",
                        columns: x => new { x.TenantId, x.ConnectionId },
                        principalSchema: "ebt_connect",
                        principalTable: "Connections",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_DeliveryEvents_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Contacts",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    CreationHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ExternalKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Email = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Phone = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Stage = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Portfolio = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    OwnerId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OrganizationId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Contacts", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Contacts_Memberships_TenantId_OwnerId",
                        columns: x => new { x.TenantId, x.OwnerId },
                        principalSchema: "ebt_connect",
                        principalTable: "Memberships",
                        principalColumns: new[] { "TenantId", "UserId" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Contacts_Organizations_TenantId_OrganizationId",
                        columns: x => new { x.TenantId, x.OrganizationId },
                        principalSchema: "ebt_connect",
                        principalTable: "Organizations",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Contacts_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Conversations",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ContactId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ConnectionId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Recipient = table.Column<string>(type: "nvarchar(24)", maxLength: 24, nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    LastInboundAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Conversations", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Conversations_Connections_TenantId_ConnectionId",
                        columns: x => new { x.TenantId, x.ConnectionId },
                        principalSchema: "ebt_connect",
                        principalTable: "Connections",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Conversations_Contacts_TenantId_ContactId",
                        columns: x => new { x.TenantId, x.ContactId },
                        principalSchema: "ebt_connect",
                        principalTable: "Contacts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Conversations_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Interactions",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ContactId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Kind = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Content = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    OccurredAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    RecordedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Interactions", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Interactions_Contacts_TenantId_ContactId",
                        columns: x => new { x.TenantId, x.ContactId },
                        principalSchema: "ebt_connect",
                        principalTable: "Contacts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Interactions_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Tasks",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    CloseKey = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CloseHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ContactId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OwnerId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    DueAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Result = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ClosedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Tasks", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Tasks_Contacts_TenantId_ContactId",
                        columns: x => new { x.TenantId, x.ContactId },
                        principalSchema: "ebt_connect",
                        principalTable: "Contacts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Tasks_Memberships_TenantId_OwnerId",
                        columns: x => new { x.TenantId, x.OwnerId },
                        principalSchema: "ebt_connect",
                        principalTable: "Memberships",
                        principalColumns: new[] { "TenantId", "UserId" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Tasks_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Messages",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ConversationId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Direction = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Content = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Status = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ProviderId = table.Column<string>(type: "nvarchar(250)", maxLength: 250, nullable: false),
                    ReplyToMessageId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    FailureCode = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Messages", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Messages_Conversations_TenantId_ConversationId",
                        columns: x => new { x.TenantId, x.ConversationId },
                        principalSchema: "ebt_connect",
                        principalTable: "Conversations",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Messages_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Documents",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    CreationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    CreationHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ContactId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TaskId = table.Column<Guid>(type: "uniqueidentifier", nullable: true),
                    Title = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CurrentVersion = table.Column<int>(type: "int", nullable: false),
                    ReviewState = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Documents", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Documents_Contacts_TenantId_ContactId",
                        columns: x => new { x.TenantId, x.ContactId },
                        principalSchema: "ebt_connect",
                        principalTable: "Contacts",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Documents_Tasks_TenantId_TaskId",
                        columns: x => new { x.TenantId, x.TaskId },
                        principalSchema: "ebt_connect",
                        principalTable: "Tasks",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Documents_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Outbox",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    MessageId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ConversationId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    State = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Attempts = table.Column<int>(type: "int", nullable: false),
                    DueAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    LeaseUntil = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    Fence = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Outbox", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_Outbox_Messages_TenantId_MessageId",
                        columns: x => new { x.TenantId, x.MessageId },
                        principalSchema: "ebt_connect",
                        principalTable: "Messages",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Outbox_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "DocumentVersions",
                schema: "ebt_connect",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    TenantId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    OperationKey = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PayloadHash = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    DocumentId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Number = table.Column<int>(type: "int", nullable: false),
                    Content = table.Column<byte[]>(type: "varbinary(max)", nullable: false),
                    Sha256 = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    FileName = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    MediaType = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ActorId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    Version = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentVersions", x => new { x.TenantId, x.Id });
                    table.ForeignKey(
                        name: "FK_DocumentVersions_Documents_TenantId_DocumentId",
                        columns: x => new { x.TenantId, x.DocumentId },
                        principalSchema: "ebt_connect",
                        principalTable: "Documents",
                        principalColumns: new[] { "TenantId", "Id" },
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_DocumentVersions_Tenants_TenantId",
                        column: x => x.TenantId,
                        principalSchema: "ebt_connect",
                        principalTable: "Tenants",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Connections_AppKey_AccountId_PhoneNumberId",
                schema: "ebt_connect",
                table: "Connections",
                columns: new[] { "AppKey", "AccountId", "PhoneNumberId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Contacts_TenantId_ExternalKey",
                schema: "ebt_connect",
                table: "Contacts",
                columns: new[] { "TenantId", "ExternalKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Contacts_TenantId_OrganizationId",
                schema: "ebt_connect",
                table: "Contacts",
                columns: new[] { "TenantId", "OrganizationId" });

            migrationBuilder.CreateIndex(
                name: "IX_Contacts_TenantId_OwnerId",
                schema: "ebt_connect",
                table: "Contacts",
                columns: new[] { "TenantId", "OwnerId" });

            migrationBuilder.CreateIndex(
                name: "IX_Conversations_TenantId_ConnectionId_Recipient",
                schema: "ebt_connect",
                table: "Conversations",
                columns: new[] { "TenantId", "ConnectionId", "Recipient" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Conversations_TenantId_ContactId",
                schema: "ebt_connect",
                table: "Conversations",
                columns: new[] { "TenantId", "ContactId" });

            migrationBuilder.CreateIndex(
                name: "IX_Credentials_TokenHash",
                schema: "ebt_connect",
                table: "Credentials",
                column: "TokenHash",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Credentials_UserId",
                schema: "ebt_connect",
                table: "Credentials",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_DeliveryEvents_TenantId_ConnectionId_EventKey",
                schema: "ebt_connect",
                table: "DeliveryEvents",
                columns: new[] { "TenantId", "ConnectionId", "EventKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Documents_TenantId_ContactId_CreationKey",
                schema: "ebt_connect",
                table: "Documents",
                columns: new[] { "TenantId", "ContactId", "CreationKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Documents_TenantId_TaskId",
                schema: "ebt_connect",
                table: "Documents",
                columns: new[] { "TenantId", "TaskId" });

            migrationBuilder.CreateIndex(
                name: "IX_DocumentVersions_TenantId_DocumentId_Number",
                schema: "ebt_connect",
                table: "DocumentVersions",
                columns: new[] { "TenantId", "DocumentId", "Number" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_DocumentVersions_TenantId_DocumentId_OperationKey",
                schema: "ebt_connect",
                table: "DocumentVersions",
                columns: new[] { "TenantId", "DocumentId", "OperationKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Imports_TenantId_UserId_OperationKey",
                schema: "ebt_connect",
                table: "Imports",
                columns: new[] { "TenantId", "UserId", "OperationKey" },
                unique: true,
                filter: "[OperationKey] <> ''");

            migrationBuilder.CreateIndex(
                name: "IX_Interactions_TenantId_ContactId_OperationKey",
                schema: "ebt_connect",
                table: "Interactions",
                columns: new[] { "TenantId", "ContactId", "OperationKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Invitations_TokenHash",
                schema: "ebt_connect",
                table: "Invitations",
                column: "TokenHash",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Memberships_TenantId_UserId",
                schema: "ebt_connect",
                table: "Memberships",
                columns: new[] { "TenantId", "UserId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Memberships_UserId",
                schema: "ebt_connect",
                table: "Memberships",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_Messages_TenantId_ConversationId_ProviderId",
                schema: "ebt_connect",
                table: "Messages",
                columns: new[] { "TenantId", "ConversationId", "ProviderId" },
                unique: true,
                filter: "[ProviderId] <> ''");

            migrationBuilder.CreateIndex(
                name: "IX_Organizations_TenantId_ExternalKey",
                schema: "ebt_connect",
                table: "Organizations",
                columns: new[] { "TenantId", "ExternalKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Outbox_TenantId_ConversationId_OperationKey",
                schema: "ebt_connect",
                table: "Outbox",
                columns: new[] { "TenantId", "ConversationId", "OperationKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Outbox_TenantId_MessageId",
                schema: "ebt_connect",
                table: "Outbox",
                columns: new[] { "TenantId", "MessageId" });

            migrationBuilder.CreateIndex(
                name: "IX_Receipts_AppKey_BodyHash",
                schema: "ebt_connect",
                table: "Receipts",
                columns: new[] { "AppKey", "BodyHash" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Tasks_TenantId_ContactId_OperationKey",
                schema: "ebt_connect",
                table: "Tasks",
                columns: new[] { "TenantId", "ContactId", "OperationKey" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Tasks_TenantId_OwnerId",
                schema: "ebt_connect",
                table: "Tasks",
                columns: new[] { "TenantId", "OwnerId" });

            migrationBuilder.CreateIndex(
                name: "IX_Users_Email",
                schema: "ebt_connect",
                table: "Users",
                column: "Email",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Audit",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Credentials",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "DeliveryEvents",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "DocumentVersions",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Imports",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Interactions",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Invitations",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Outbox",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Receipts",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Documents",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Messages",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Tasks",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Conversations",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Connections",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Contacts",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Memberships",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Organizations",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Users",
                schema: "ebt_connect");

            migrationBuilder.DropTable(
                name: "Tenants",
                schema: "ebt_connect");
        }
    }
}
