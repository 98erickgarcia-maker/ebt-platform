using System.Data.Common;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace Ebt.Platform.Api;

// Separate context keys: never changes CASST's existing SESSION_CONTEXT/RLS policy.
public sealed class TenantSqlContext(AccessScope scope) : DbCommandInterceptor
{
    async Task Apply(DbCommand original, CancellationToken ct)
    {
        if (original.Connection == null) return;
        using var context = original.Connection.CreateCommand(); context.Transaction = original.Transaction;
        context.CommandText = "EXEC sys.sp_set_session_context @key=N'ebt_tenant', @value=@tenant; EXEC sys.sp_set_session_context @key=N'ebt_system', @value=@system;";
        var tenant = context.CreateParameter(); tenant.ParameterName = "@tenant"; tenant.Value = scope.TenantId; tenant.DbType = System.Data.DbType.Guid; context.Parameters.Add(tenant);
        var system = context.CreateParameter(); system.ParameterName = "@system"; system.Value = scope.System ? 1 : 0; context.Parameters.Add(system);
        await context.ExecuteNonQueryAsync(ct);
    }
    public override async ValueTask<InterceptionResult<DbDataReader>> ReaderExecutingAsync(DbCommand command, CommandEventData eventData, InterceptionResult<DbDataReader> result, CancellationToken cancellationToken = default) { await Apply(command, cancellationToken); return result; }
    public override async ValueTask<InterceptionResult<int>> NonQueryExecutingAsync(DbCommand command, CommandEventData eventData, InterceptionResult<int> result, CancellationToken cancellationToken = default) { await Apply(command, cancellationToken); return result; }
    public override async ValueTask<InterceptionResult<object>> ScalarExecutingAsync(DbCommand command, CommandEventData eventData, InterceptionResult<object> result, CancellationToken cancellationToken = default) { await Apply(command, cancellationToken); return result; }
}
