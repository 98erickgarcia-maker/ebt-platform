using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable
namespace Ebt.Platform.Api.Migrations;
public partial class TenantStorageBarrier : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("""
EXEC(N'CREATE FUNCTION [ebt_connect].[tenant_guard](@TenantId uniqueidentifier)
RETURNS TABLE WITH SCHEMABINDING AS
RETURN SELECT 1 AS allowed
WHERE @TenantId = TRY_CONVERT(uniqueidentifier, SESSION_CONTEXT(N''ebt_tenant''))
   OR TRY_CONVERT(int, SESSION_CONTEXT(N''ebt_system'')) = 1;');
""");
        migrationBuilder.Sql("""
EXEC(N'CREATE SECURITY POLICY [ebt_connect].[tenant_barrier]
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] BEFORE DELETE,
ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit],
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] AFTER INSERT,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] AFTER UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] BEFORE UPDATE,
ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] BEFORE DELETE
WITH (STATE=ON);');
""");
    }
    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("DROP SECURITY POLICY [ebt_connect].[tenant_barrier];");
        migrationBuilder.Sql("DROP FUNCTION [ebt_connect].[tenant_guard];");
    }
}
