using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class ProviderConnectionIdentity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Messages_TenantId_ConversationId_ProviderId",
                schema: "ebt_connect",
                table: "Messages");

            migrationBuilder.AlterColumn<string>(
                name: "ProviderId",
                schema: "ebt_connect",
                table: "Messages",
                type: "nvarchar(250)",
                maxLength: 250,
                nullable: false,
                collation: "Latin1_General_100_BIN2",
                oldClrType: typeof(string),
                oldType: "nvarchar(250)",
                oldMaxLength: 250);

            migrationBuilder.AddColumn<Guid>(
                name: "ConnectionId",
                schema: "ebt_connect",
                table: "Messages",
                type: "uniqueidentifier",
                nullable: false,
                defaultValue: new Guid("00000000-0000-0000-0000-000000000000"));

            migrationBuilder.AlterColumn<string>(
                name: "ProviderId",
                schema: "ebt_connect",
                table: "DeliveryEvents",
                type: "nvarchar(250)",
                maxLength: 250,
                nullable: false,
                collation: "Latin1_General_100_BIN2",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.Sql("EXEC sys.sp_set_session_context @key=N'ebt_system', @value=1; EXEC(N'UPDATE m SET ConnectionId=c.ConnectionId FROM ebt_connect.Messages m JOIN ebt_connect.Conversations c ON c.TenantId=m.TenantId AND c.Id=m.ConversationId;'); EXEC sys.sp_set_session_context @key=N'ebt_system', @value=NULL;");

            migrationBuilder.CreateIndex(
                name: "IX_Messages_TenantId_ConnectionId_ProviderId",
                schema: "ebt_connect",
                table: "Messages",
                columns: new[] { "TenantId", "ConnectionId", "ProviderId" },
                unique: true,
                filter: "[ProviderId] <> ''");

            migrationBuilder.CreateIndex(
                name: "IX_Messages_TenantId_ConversationId",
                schema: "ebt_connect",
                table: "Messages",
                columns: new[] { "TenantId", "ConversationId" });

            migrationBuilder.AddForeignKey(
                name: "FK_Messages_Connections_TenantId_ConnectionId",
                schema: "ebt_connect",
                table: "Messages",
                columns: new[] { "TenantId", "ConnectionId" },
                principalSchema: "ebt_connect",
                principalTable: "Connections",
                principalColumns: new[] { "TenantId", "Id" },
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Messages_Connections_TenantId_ConnectionId",
                schema: "ebt_connect",
                table: "Messages");

            migrationBuilder.DropIndex(
                name: "IX_Messages_TenantId_ConnectionId_ProviderId",
                schema: "ebt_connect",
                table: "Messages");

            migrationBuilder.DropIndex(
                name: "IX_Messages_TenantId_ConversationId",
                schema: "ebt_connect",
                table: "Messages");

            migrationBuilder.DropColumn(
                name: "ConnectionId",
                schema: "ebt_connect",
                table: "Messages");

            migrationBuilder.AlterColumn<string>(
                name: "ProviderId",
                schema: "ebt_connect",
                table: "Messages",
                type: "nvarchar(250)",
                maxLength: 250,
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(250)",
                oldMaxLength: 250,
                oldCollation: "Latin1_General_100_BIN2");

            migrationBuilder.AlterColumn<string>(
                name: "ProviderId",
                schema: "ebt_connect",
                table: "DeliveryEvents",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(250)",
                oldMaxLength: 250,
                oldCollation: "Latin1_General_100_BIN2");

            migrationBuilder.CreateIndex(
                name: "IX_Messages_TenantId_ConversationId_ProviderId",
                schema: "ebt_connect",
                table: "Messages",
                columns: new[] { "TenantId", "ConversationId", "ProviderId" },
                unique: true,
                filter: "[ProviderId] <> ''");
        }
    }
}
