using System.Data;
using System.Data.Common;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace Ebt.Infrastructure.Persistence;

// Stateless: never keep request/tenant state on the factory or interceptor.
public sealed class SqlTenantConnectionInterceptor : DbConnectionInterceptor
{
    public override void ConnectionOpened(DbConnection connection, ConnectionEndEventData eventData)
    {
        using var command = CreateCommand(connection, eventData);
        command.ExecuteNonQuery();
    }

    public override async Task ConnectionOpenedAsync(
        DbConnection connection, ConnectionEndEventData eventData,
        CancellationToken cancellationToken = default)
    {
        await using var command = CreateCommand(connection, eventData);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    private static DbCommand CreateCommand(DbConnection connection, ConnectionEndEventData eventData)
    {
        var command = connection.CreateCommand();
        command.CommandText = "EXEC sys.sp_set_session_context @key=N'ebt:tenant', @value=@tenant, @read_only=1;";
        var tenant = command.CreateParameter();
        tenant.ParameterName = "@tenant";
        tenant.DbType = DbType.String;
        tenant.Size = 64;
        tenant.Value = (object?)(eventData.Context as EbtDataContext)?.TenantScope ?? DBNull.Value;
        command.Parameters.Add(tenant);
        // SqlClient resets SESSION_CONTEXT when a pooled physical connection is reused.
        // Every logical open sets the trusted value again, including retry opens.
        return command;
    }
}
