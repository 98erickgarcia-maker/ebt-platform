using System.Data;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

// An isolated first Flow vertical slice. The new schema is installed only through its
// reviewed migration; this code never creates production tables at runtime.
public static class FlowProtocol
{
    private const string Prefix = "/api/flow/v1";
    private static SqlParameter P(string name, object? value) => new(name, value ?? DBNull.Value);

    public static void Map(WebApplication app)
    {
        app.MapGet(Prefix + "/protocols", async (AccessScope access, PlatformDb db, CancellationToken ct) =>
        {
            await using var conn = new SqlConnection(db.Database.GetConnectionString());
            await conn.OpenAsync(ct);
            await using var cmd = new SqlCommand(@"
SELECT TOP (100) Id, Number, [Year], Subject, [State], Portfolio, Version, CreatedAt
FROM ebt_flow.Protocols
WHERE TenantId=@tenant AND (@admin=1 OR Portfolio=@portfolio)
ORDER BY CreatedAt DESC, Id DESC", conn);
            cmd.Parameters.AddRange([P("@tenant", access.TenantId), P("@admin", access.IsAdmin ? 1 : 0), P("@portfolio", access.Portfolio)]);
            var rows = new List<object>();
            await using var reader = await cmd.ExecuteReaderAsync(ct);
            while (await reader.ReadAsync(ct)) rows.Add(new {
                id = reader.GetGuid(0), number = reader.GetInt32(1), year = reader.GetInt32(2),
                subject = reader.GetString(3), state = reader.GetString(4), portfolio = reader.GetString(5),
                version = reader.GetInt64(6), createdAt = reader.GetDateTimeOffset(7)
            });
            return Results.Ok(new { items = rows });
        });

        app.MapPost(Prefix + "/protocols", async (FlowCreate input, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite();
            var key = Contract.Idempotency(http.Request);
            var subject = Contract.Required(input.Subject, 180, "Assunto");
            var portfolio = access.Portfolio;
            var year = DateTimeOffset.UtcNow.Year;
            var id = Guid.NewGuid();
            var hash = Contract.Payload(new { subject, portfolio });
            await using var conn = new SqlConnection(db.Database.GetConnectionString());
            await conn.OpenAsync(http.RequestAborted);
            await using var tx = (SqlTransaction)await conn.BeginTransactionAsync(IsolationLevel.Serializable, http.RequestAborted);
            try
            {
                // A lock covers the sequence and the idempotency key across concurrent requests.
                await using var cmd = new SqlCommand(@"
DECLARE @prior uniqueidentifier, @priorhash varchar(64), @n int;
SELECT @prior=Id, @priorhash=PayloadHash FROM ebt_flow.Protocols WITH (UPDLOCK,HOLDLOCK)
 WHERE TenantId=@tenant AND OperationKey=@key;
IF @prior IS NOT NULL
BEGIN SELECT Id,Number,[Year],Subject,[State],Version,PayloadHash FROM ebt_flow.Protocols WHERE TenantId=@tenant AND Id=@prior; END
ELSE
BEGIN
 SELECT @n=ISNULL(MAX(Number),0)+1 FROM ebt_flow.Protocols WITH (UPDLOCK,HOLDLOCK)
 WHERE TenantId=@tenant AND [Year]=@year;
 INSERT INTO ebt_flow.Protocols (TenantId,Id,Number,[Year],Subject,[State],Portfolio,Version,CreatedAt,OperationKey,PayloadHash,CreatedBy)
 VALUES (@tenant,@id,@n,@year,@subject,'open',@portfolio,1,SYSUTCDATETIME(),@key,@hash,@actor);
 INSERT INTO ebt_flow.Movements (TenantId,Id,ProtocolId,ActorId,[Action],OccurredAt)
 VALUES (@tenant,NEWID(),@id,@actor,'created',SYSUTCDATETIME());
 SELECT Id,Number,[Year],Subject,[State],Version,PayloadHash FROM ebt_flow.Protocols WHERE TenantId=@tenant AND Id=@id;
END", conn, tx);
                cmd.Parameters.AddRange([P("@tenant", access.TenantId),P("@actor",access.UserId),P("@key",key),P("@hash",hash),P("@id",id),P("@year",year),P("@subject",subject),P("@portfolio",portfolio)]);
                await using var reader = await cmd.ExecuteReaderAsync(http.RequestAborted);
                if (!await reader.ReadAsync(http.RequestAborted)) throw new ApiFault(503,"flow_unavailable","Não foi possível confirmar o protocolo.");
                var storedHash=reader.GetString(6);
                if (storedHash != hash) throw new ApiFault(409,"idempotency_mismatch","Esta chave já foi utilizada com outro conteúdo.");
                var result = new { id=reader.GetGuid(0), number=reader.GetInt32(1), year=reader.GetInt32(2), subject=reader.GetString(3), state=reader.GetString(4), version=reader.GetInt64(5) };
                await reader.DisposeAsync();
                await tx.CommitAsync(http.RequestAborted);
                return Results.Ok(result);
            }
            catch { await tx.RollbackAsync(CancellationToken.None); throw; }
        });

        app.MapPost(Prefix + "/protocols/{id:guid}/transition", async (Guid id, FlowTransition input, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite();
            var action=Contract.Required(input.Action, 32,"Ação");
            if (action is not ("start" or "complete")) throw new ApiFault(400,"invalid_transition","Transição não permitida.");
            var resultText = action=="complete" ? Contract.Required(input.Result,1000,"Resultado",true) : "";
            await using var conn=new SqlConnection(db.Database.GetConnectionString());
            await conn.OpenAsync(http.RequestAborted);
            await using var tx=(SqlTransaction)await conn.BeginTransactionAsync(IsolationLevel.Serializable,http.RequestAborted);
            try {
                await using var cmd=new SqlCommand(@"
SELECT [State],Version FROM ebt_flow.Protocols WITH (UPDLOCK,HOLDLOCK)
 WHERE TenantId=@tenant AND Id=@id AND (@admin=1 OR Portfolio=@portfolio)",conn,tx);
                cmd.Parameters.AddRange([P("@tenant",access.TenantId),P("@id",id),P("@admin",access.IsAdmin?1:0),P("@portfolio",access.Portfolio)]);
                string old;long version;
                await using(var reader=await cmd.ExecuteReaderAsync(http.RequestAborted)) {
                    if(!await reader.ReadAsync(http.RequestAborted)) throw ApiFault.NotFound();
                    old=reader.GetString(0);version=reader.GetInt64(1);
                }
                Contract.Match(http.Request,version);
                var expected=action=="start"?"open":"in_review";
                if(old!=expected) throw new ApiFault(409,"invalid_transition","Estado não permite a transição solicitada.");
                var next=action=="start"?"in_review":"complete";
                await using var update=new SqlCommand(@"
UPDATE ebt_flow.Protocols SET [State]=@next,Version=Version+1 WHERE TenantId=@tenant AND Id=@id AND Version=@version;
INSERT INTO ebt_flow.Movements (TenantId,Id,ProtocolId,ActorId,[Action],Result,OccurredAt)
 VALUES (@tenant,NEWID(),@id,@actor,@action,@result,SYSUTCDATETIME());",conn,tx);
                update.Parameters.AddRange([P("@tenant",access.TenantId),P("@id",id),P("@version",version),P("@actor",access.UserId),P("@action",action),P("@result",resultText),P("@next",next)]);
                await update.ExecuteNonQueryAsync(http.RequestAborted);
                await tx.CommitAsync(http.RequestAborted);
                return Results.Ok(new { id, state=next, version=version+1 });
            } catch { await tx.RollbackAsync(CancellationToken.None); throw; }
        });
    }
}
public sealed record FlowCreate(string Subject);
public sealed record FlowTransition(string Action,string? Result);
