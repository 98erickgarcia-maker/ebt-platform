using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Ebt.Platform.Api.Migrations
{
    /// <inheritdoc />
    public partial class CommercialProspection : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Channel",
                schema: "ebt_connect",
                table: "MailTemplates",
                type: "nvarchar(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "email");

            migrationBuilder.AddColumn<string>(
                name: "Purpose",
                schema: "ebt_connect",
                table: "MailTemplates",
                type: "nvarchar(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "prospection");

            migrationBuilder.AddColumn<DateTimeOffset>(
                name: "ActiveSince",
                schema: "ebt_connect",
                table: "Contacts",
                type: "datetimeoffset",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "BestTime",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(160)",
                maxLength: 160,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "ContactRole",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "DecisionMaker",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "unknown");

            migrationBuilder.AddColumn<string>(
                name: "Need",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(2000)",
                maxLength: 2000,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "PreferredChannel",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "Segment",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "Source",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(160)",
                maxLength: 160,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "SourceUrl",
                schema: "ebt_connect",
                table: "Contacts",
                type: "nvarchar(500)",
                maxLength: 500,
                nullable: false,
                defaultValue: "");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Channel",
                schema: "ebt_connect",
                table: "MailTemplates");

            migrationBuilder.DropColumn(
                name: "Purpose",
                schema: "ebt_connect",
                table: "MailTemplates");

            migrationBuilder.DropColumn(
                name: "ActiveSince",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "BestTime",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "ContactRole",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "DecisionMaker",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "Need",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "PreferredChannel",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "Segment",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "Source",
                schema: "ebt_connect",
                table: "Contacts");

            migrationBuilder.DropColumn(
                name: "SourceUrl",
                schema: "ebt_connect",
                table: "Contacts");
        }
    }
}
