using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class WazVoxEventIdentity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "ProviderEventId",
                schema: "ebt_connect",
                table: "Receipts",
                type: "nvarchar(200)",
                maxLength: 200,
                nullable: false,
                defaultValue: "",
                collation: "Latin1_General_100_BIN2");

            migrationBuilder.CreateIndex(
                name: "IX_Receipts_AppKey_ProviderEventId",
                schema: "ebt_connect",
                table: "Receipts",
                columns: new[] { "AppKey", "ProviderEventId" },
                unique: true,
                filter: "[ProviderEventId] <> ''");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Receipts_AppKey_ProviderEventId",
                schema: "ebt_connect",
                table: "Receipts");

            migrationBuilder.DropColumn(
                name: "ProviderEventId",
                schema: "ebt_connect",
                table: "Receipts");
        }
    }
}
