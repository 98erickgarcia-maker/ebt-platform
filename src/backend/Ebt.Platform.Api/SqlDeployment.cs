using Microsoft.Data.SqlClient;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Ebt.Platform.Api;

public static class SqlDeployment
{
    public static async Task Run(string connectionString, IConfiguration config)
    {
        var settings=new SqlConnectionStringBuilder(connectionString);
        if(settings.DataSource!="tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433"||settings.InitialCatalog!="sqldb-crm-casst-dev-v2"||settings.TrustServerCertificate)
            throw new InvalidOperationException("Implantação exige o banco compartilhado confirmado e certificado TLS validado.");
        var path=config["Platform:MigrationScript"]??throw new InvalidOperationException("Script revisado necessário.");
        var expected=config["Platform:MigrationApprovedSha256"]??throw new InvalidOperationException("Hash revisado necessário.");
        var output=config["Platform:MigrationOutput"]??throw new InvalidOperationException("Destino de evidência necessário.");
        var bytes=await File.ReadAllBytesAsync(path);
        var hash=Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        if(!string.Equals(hash,expected,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("Script diverge do hash revisado.");
        var script=Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF');
        if(!script.StartsWith("-- EBT-only schema.",StringComparison.Ordinal)||Regex.IsMatch(script,@"(?im)^\s*(CREATE|ALTER|DROP)\s+DATABASE\b"))throw new InvalidOperationException("Script fora do recorte autorizado.");
        using var connection=new SqlConnection(connectionString){AccessToken=Environment.GetEnvironmentVariable("EBT_SQL_ACCESS_TOKEN")??throw new InvalidOperationException("Token temporário necessário.")};
        await connection.OpenAsync();
        async Task<string> OtherSchemasFingerprint()
        {
            using var command=new SqlCommand("SELECT s.name,o.name,o.type,o.object_id,o.modify_date,ISNULL(m.definition,'') FROM sys.objects o INNER JOIN sys.schemas s ON o.schema_id=s.schema_id LEFT JOIN sys.sql_modules m ON m.object_id=o.object_id WHERE o.is_ms_shipped=0 AND s.name<>'ebt_connect' ORDER BY s.name,o.name,o.type,o.object_id",connection);
            using var reader=await command.ExecuteReaderAsync();var values=new List<object[]>();
            while(await reader.ReadAsync()){var row=new object[reader.FieldCount];reader.GetValues(row);values.Add(row);}
            return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(values)))).ToLowerInvariant();
        }
        async Task<string> OtherTableCountsFingerprint()
        {
            using var command=new SqlCommand("SELECT s.name,t.name,SUM(p.rows) FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id JOIN sys.partitions p ON p.object_id=t.object_id AND p.index_id IN (0,1) WHERE s.name<>'ebt_connect' GROUP BY s.name,t.name ORDER BY s.name,t.name",connection);
            using var reader=await command.ExecuteReaderAsync();var values=new List<object[]>();
            while(await reader.ReadAsync()){var row=new object[reader.FieldCount];reader.GetValues(row);values.Add(row);}
            return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(values)))).ToLowerInvariant();
        }
        var countsBefore=await OtherTableCountsFingerprint();
        var before=await OtherSchemasFingerprint();
        foreach(var batch in Regex.Split(script,@"^\s*GO\s*$",RegexOptions.Multiline|RegexOptions.IgnoreCase))
        {
            if(string.IsNullOrWhiteSpace(batch))continue;
            using var command=new SqlCommand(batch,connection){CommandTimeout=120};await command.ExecuteNonQueryAsync();
        }
        var after=await OtherSchemasFingerprint(); var countsAfter=await OtherTableCountsFingerprint();
        using var ledger=new SqlCommand("SELECT MigrationId FROM ebt_connect.__EFMigrationsHistory ORDER BY MigrationId",connection);using var history=await ledger.ExecuteReaderAsync();var migrations=new List<string>();while(await history.ReadAsync())migrations.Add(history.GetString(0));
        var report=new{generatedUtc=DateTimeOffset.UtcNow,database=settings.InitialCatalog,schema="ebt_connect",scriptSha256=hash,migrations,otherSchemasBefore=before,otherSchemasAfter=after,otherSchemasUnchanged=before==after,otherTableCountsBefore=countsBefore,otherTableCountsAfter=countsAfter,otherTableCountsUnchanged=countsBefore==countsAfter,newDatabaseCreated=false,seedApplied=false,identityGrantsApplied=false};
        await File.WriteAllTextAsync(output,JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true}));
        if(before!=after || countsBefore!=countsAfter)throw new InvalidOperationException("Catálogo de outros schemas mudou; conferir evidência antes de prosseguir.");
        Console.WriteLine($"Schema ebt_connect aplicado: {migrations.Count} migrations; catálogo dos outros schemas preservado. Nenhum seed ou banco novo.");
    }
}
