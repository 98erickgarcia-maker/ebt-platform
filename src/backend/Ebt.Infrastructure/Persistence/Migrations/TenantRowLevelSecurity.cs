using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;

namespace Ebt.Infrastructure.Persistence.Migrations;

[DbContext(typeof(EbtDataContext))]
[Migration("202610070003_TenantRowLevelSecurity")]
public sealed class TenantRowLevelSecurity : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("IF SCHEMA_ID(N'ebt_security') IS NULL EXEC(N'CREATE SCHEMA ebt_security');");
        migrationBuilder.Sql("""
            CREATE FUNCTION ebt_security.TenantPredicate(@TenantKey nvarchar(64))
            RETURNS TABLE WITH SCHEMABINDING AS
            RETURN SELECT 1 AS allowed
            WHERE @TenantKey = CONVERT(nvarchar(64), SESSION_CONTEXT(N'ebt:tenant'));
            """);
        migrationBuilder.Sql("""
            CREATE SECURITY POLICY ebt_security.FoundationTenantPolicy
            ADD FILTER PREDICATE ebt_security.TenantPredicate(TenantKey) ON dbo.FoundationRecords,
            ADD BLOCK PREDICATE ebt_security.TenantPredicate(TenantKey) ON dbo.FoundationRecords AFTER INSERT,
            ADD BLOCK PREDICATE ebt_security.TenantPredicate(TenantKey) ON dbo.FoundationRecords AFTER UPDATE
            WITH (STATE = ON, SCHEMABINDING = ON);
            """);
    }

    protected override void Down(MigrationBuilder migrationBuilder) =>
        throw new NotSupportedException("Remoção da proteção SQL bloqueada. Use restore de QA validado.");
}
