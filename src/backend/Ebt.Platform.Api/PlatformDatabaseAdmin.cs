using Microsoft.Data.SqlClient;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Ebt.Platform.Api;

public static class PlatformDatabaseAdmin
{
    public static async Task Run(string connectionString, IConfiguration config)
    {
        var settings = new SqlConnectionStringBuilder(connectionString);
        if (settings.DataSource != "tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433" ||
            settings.InitialCatalog != "sqldb-crm-casst-dev-v2" || settings.TrustServerCertificate)
            throw new InvalidOperationException("Expected existing shared Azure database with TLS validation.");
        var output = config["Platform:CatalogReport"] ?? throw new InvalidOperationException("Report path required.");
        using var connection = new SqlConnection(connectionString)
        {
            AccessToken = Environment.GetEnvironmentVariable("EBT_SQL_ACCESS_TOKEN") ?? throw new InvalidOperationException("Temporary token required.")
        };
        await connection.OpenAsync();
        async Task<List<Dictionary<string, object>>> Rows(string sql)
        {
            using var command = new SqlCommand(sql, connection) { CommandTimeout = 60 };
            using var reader = await command.ExecuteReaderAsync();
            var rows = new List<Dictionary<string, object>>();
            while (await reader.ReadAsync())
            {
                var row = new Dictionary<string, object>();
                for (var i = 0; i < reader.FieldCount; i++) row[reader.GetName(i)] = reader.IsDBNull(i) ? "" : reader.GetValue(i);
                rows.Add(row);
            }
            return rows;
        }
        const string catalogSql = "SELECT s.name AS schemaName,o.name,o.type,o.object_id,o.modify_date,ISNULL(m.definition,'') AS definition FROM sys.objects o JOIN sys.schemas s ON o.schema_id=s.schema_id LEFT JOIN sys.sql_modules m ON m.object_id=o.object_id WHERE o.is_ms_shipped=0 AND s.name<>'ebt_platform' ORDER BY s.name,o.name,o.type,o.object_id";
        string Hash(object value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(value)))).ToLowerInvariant();
        var before = Hash(await Rows(catalogSql));
        var countsBefore = await Rows("SELECT s.name AS schemaName,t.name,SUM(p.rows) AS [rowCount] FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id JOIN sys.partitions p ON p.object_id=t.object_id AND p.index_id IN (0,1) WHERE s.name<>'ebt_platform' GROUP BY s.name,t.name ORDER BY s.name,t.name");
        var mode = config["Platform:CatalogOperation"] ?? "inspect";
        string? approvedHash = null;
        if (mode == "apply")
        {
            var path = config["Platform:CatalogScript"] ?? throw new InvalidOperationException("Reviewed script required.");
            var bytes = await File.ReadAllBytesAsync(path);
            approvedHash = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
            if (!string.Equals(approvedHash, config["Platform:CatalogApprovedSha256"], StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Script hash differs from approved bytes.");
            var script = Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF');
            if (!script.StartsWith("-- EBT Platform only.", StringComparison.Ordinal)) throw new InvalidOperationException("Unexpected script scope.");
            using var command = new SqlCommand(script, connection) { CommandTimeout = 120 };
            await command.ExecuteNonQueryAsync();
            // Public catalog only. Keep DDL and all catalog writes administrator-operated.
            const string grants = "IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name=N'id-ebt-connect-hml' AND type='E' AND sid=CONVERT(varbinary(16),CONVERT(uniqueidentifier,'196bebfa-0c4d-49a7-9e9c-46a823d8816d'))) THROW 51013, 'Runtime identity mismatch.', 1; GRANT SELECT ON OBJECT::ebt_platform.Applications TO [id-ebt-connect-hml];";
            using var grant = new SqlCommand(grants, connection); await grant.ExecuteNonQueryAsync();
        }
        else if (mode != "inspect") throw new InvalidOperationException("Unsupported operation.");
        var after = Hash(await Rows(catalogSql));
        var countsAfter = await Rows("SELECT s.name AS schemaName,t.name,SUM(p.rows) AS [rowCount] FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id JOIN sys.partitions p ON p.object_id=t.object_id AND p.index_id IN (0,1) WHERE s.name<>'ebt_platform' GROUP BY s.name,t.name ORDER BY s.name,t.name");
        var exists = (await Rows("SELECT COUNT(*) AS total FROM sys.tables WHERE schema_id=SCHEMA_ID('ebt_platform')"))[0]["total"];
        var applications = Convert.ToInt32(exists) > 0 ? await Rows("SELECT Code,Name,State,DataSchema FROM ebt_platform.Applications ORDER BY SortOrder,Code") : [];
        // Impersonation verifies the actual contained identity; never grant database-wide roles.
        var permissions = Convert.ToInt32(exists) > 0 ? await Rows("EXECUTE AS USER='id-ebt-connect-hml'; SELECT HAS_PERMS_BY_NAME('ebt_platform.Applications','OBJECT','SELECT') AS catalogRead,HAS_PERMS_BY_NAME('ebt_platform.Applications','OBJECT','INSERT') AS catalogInsert,HAS_PERMS_BY_NAME('ebt_platform','SCHEMA','ALTER') AS platformAlter,HAS_PERMS_BY_NAME('ebt_connect','SCHEMA','SELECT') AS connectRead,HAS_PERMS_BY_NAME('dbo','SCHEMA','SELECT') AS dboRead,HAS_PERMS_BY_NAME('ebt_site','SCHEMA','SELECT') AS siteRead,HAS_PERMS_BY_NAME('crp','SCHEMA','SELECT') AS crpRead,HAS_PERMS_BY_NAME('thaiane','SCHEMA','SELECT') AS thaianeRead; REVERT;") : [];
        var report = new { generatedUtc = DateTimeOffset.UtcNow, database = settings.InitialCatalog, schema = "ebt_platform", mode,
            scriptSha256 = approvedHash, otherSchemasBefore = before, otherSchemasAfter = after, otherSchemasUnchanged = before == after,
            otherTableCount = countsBefore.Count, otherTableCountsBeforeSha256 = Hash(countsBefore), otherTableCountsAfterSha256 = Hash(countsAfter), otherTableCountsUnchanged = Hash(countsBefore) == Hash(countsAfter),
            applications, permissions, newDatabaseCreated = false, movedApplicationData = false,
            limits = new[] { "Catalog hashes and table counts do not certify unchanged contents of every row", "Future application catalog entries are planned, not implemented modules" } };
        await File.WriteAllTextAsync(output, JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
        if (before != after) throw new InvalidOperationException("Other schema catalog changed; investigate before publishing.");
        if (mode == "apply" && (permissions.Count != 1 || Convert.ToInt32(permissions[0]["catalogRead"]) != 1 ||
            Convert.ToInt32(permissions[0]["catalogInsert"]) != 0 || Convert.ToInt32(permissions[0]["platformAlter"]) != 0 ||
            Convert.ToInt32(permissions[0]["connectRead"]) != 1 || new[] { "dboRead", "siteRead", "crpRead", "thaianeRead" }.Any(k => !permissions[0][k].Equals("") && Convert.ToInt32(permissions[0][k]) != 0)))
            throw new InvalidOperationException("Runtime permission boundary failed verification.");
        Console.WriteLine($"Platform catalog {mode}: {applications.Count} applications; other schema catalog preserved.");
    }
}
