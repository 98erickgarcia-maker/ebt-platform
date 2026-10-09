using Microsoft.Data.SqlClient;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Ebt.Platform.Api;

// Explicit, hash-bound operator command; never invoked by application startup.
public static class FlowDatabaseAdmin
{
    public static async Task Run(string connectionString, IConfiguration config)
    {
        var settings = new SqlConnectionStringBuilder(connectionString);
        if (settings.DataSource != "tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433" || settings.InitialCatalog != "sqldb-crm-casst-dev-v2" || settings.TrustServerCertificate)
            throw new InvalidOperationException("Unexpected approved Azure database.");
        var path = config["Flow:MigrationScript"] ?? throw new InvalidOperationException("Reviewed script required.");
        var bytes = await File.ReadAllBytesAsync(path);
        var hash = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        if (hash != config["Flow:ApprovedSha256"]) throw new InvalidOperationException("Reviewed hash differs.");
        var script = Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF');
        if (!script.StartsWith("-- EBT Flow only.") || Regex.IsMatch(script, @"(?im)^\s*(CREATE|ALTER|DROP)\s+DATABASE\b")) throw new InvalidOperationException("Unexpected migration scope.");
        using var conn = new SqlConnection(connectionString) { AccessToken = Environment.GetEnvironmentVariable("EBT_SQL_ACCESS_TOKEN") ?? throw new InvalidOperationException("Temporary SQL token required.") };
        await conn.OpenAsync();
        async Task<string> Fingerprint()
        {
            using var cmd = new SqlCommand("SELECT s.name,o.name,o.type,o.object_id,o.modify_date,ISNULL(m.definition,'') FROM sys.objects o JOIN sys.schemas s ON s.schema_id=o.schema_id LEFT JOIN sys.sql_modules m ON m.object_id=o.object_id WHERE o.is_ms_shipped=0 AND s.name<>'ebt_flow' ORDER BY s.name,o.name,o.type,o.object_id",conn);
            using var reader = await cmd.ExecuteReaderAsync(); var rows = new List<object[]>();
            while(await reader.ReadAsync()) { var row=new object[reader.FieldCount];reader.GetValues(row);rows.Add(row); }
            return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(rows)))).ToLowerInvariant();
        }
        var before = await Fingerprint();
        using(var cmd = new SqlCommand(script,conn){CommandTimeout=120}) await cmd.ExecuteNonQueryAsync();
        const string grants = "IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name=N'id-ebt-connect-hml' AND type='E' AND sid=CONVERT(varbinary(16),CONVERT(uniqueidentifier,'196bebfa-0c4d-49a7-9e9c-46a823d8816d'))) THROW 51013,'Runtime identity mismatch.',1; GRANT SELECT,INSERT,UPDATE ON OBJECT::ebt_flow.Protocols TO [id-ebt-connect-hml]; GRANT SELECT,INSERT ON OBJECT::ebt_flow.Movements TO [id-ebt-connect-hml];";
        using(var cmd = new SqlCommand(grants,conn)) await cmd.ExecuteNonQueryAsync();
        using(var cmd = new SqlCommand("EXECUTE AS USER='id-ebt-connect-hml'; SELECT HAS_PERMS_BY_NAME('ebt_flow.Protocols','OBJECT','INSERT'),HAS_PERMS_BY_NAME('ebt_flow.Movements','OBJECT','INSERT'),HAS_PERMS_BY_NAME('ebt_flow.Movements','OBJECT','UPDATE'),HAS_PERMS_BY_NAME('ebt_flow','SCHEMA','ALTER'); REVERT;",conn))
        using(var reader=await cmd.ExecuteReaderAsync())
            if(!await reader.ReadAsync() || reader.GetInt32(0)!=1 || reader.GetInt32(1)!=1 || reader.GetInt32(2)!=0 || reader.GetInt32(3)!=0) throw new InvalidOperationException("Flow grants outside reviewed scope.");
        var after=await Fingerprint();
        if(before!=after)throw new InvalidOperationException("Other schema definitions changed.");
        var enableCatalog = config["Flow:EnableCatalog"] == "true";
        if(enableCatalog)
        {
            using var catalog = new SqlCommand("UPDATE ebt_platform.Applications SET [State]='available',DataSchema=N'ebt_flow',Description=N'Protocolos com abertura, análise, conclusão e histórico privado.' WHERE Code='flow'; IF @@ROWCOUNT<>1 THROW 51014,'Flow catalog missing.',1;",conn);
            await catalog.ExecuteNonQueryAsync();
        }
        var report=new { generatedUtc=DateTimeOffset.UtcNow,schema="ebt_flow",scriptSha256=hash,otherSchemasBefore=before,otherSchemasAfter=after,otherSchemasUnchanged=before==after,explicitObjectGrants=true,seedApplied=false,newDatabaseCreated=false,catalogEnabled=enableCatalog };
        await File.WriteAllTextAsync(config["Flow:Report"] ?? throw new InvalidOperationException("Report path required."),JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine("PASS Flow schema applied; other schema definitions preserved; restricted object grants verified.");
    }
}
