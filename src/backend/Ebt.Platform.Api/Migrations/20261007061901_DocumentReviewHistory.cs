using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class DocumentReviewHistory : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "ReviewReason",
                schema: "ebt_connect",
                table: "DocumentVersions",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "ReviewState",
                schema: "ebt_connect",
                table: "DocumentVersions",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<DateTimeOffset>(
                name: "ReviewedAt",
                schema: "ebt_connect",
                table: "DocumentVersions",
                type: "datetimeoffset",
                nullable: true);

            migrationBuilder.AddColumn<Guid>(
                name: "ReviewedBy",
                schema: "ebt_connect",
                table: "DocumentVersions",
                type: "uniqueidentifier",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ScanState",
                schema: "ebt_connect",
                table: "DocumentVersions",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ReviewReason",
                schema: "ebt_connect",
                table: "DocumentVersions");

            migrationBuilder.DropColumn(
                name: "ReviewState",
                schema: "ebt_connect",
                table: "DocumentVersions");

            migrationBuilder.DropColumn(
                name: "ReviewedAt",
                schema: "ebt_connect",
                table: "DocumentVersions");

            migrationBuilder.DropColumn(
                name: "ReviewedBy",
                schema: "ebt_connect",
                table: "DocumentVersions");

            migrationBuilder.DropColumn(
                name: "ScanState",
                schema: "ebt_connect",
                table: "DocumentVersions");
        }
    }
}
