using Microsoft.Data.SqlClient;
using System.Text.Json;

namespace Ebt.Platform.Api;

public static class SqlInspection
{
    public static async Task Run(string connectionString, string output)
    {
        var settings = new SqlConnectionStringBuilder(connectionString);
        if (settings.DataSource != "tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433" || settings.InitialCatalog != "sqldb-crm-casst-dev-v2" || settings.TrustServerCertificate)
            throw new InvalidOperationException("Inspeção Azure exige o destino compartilhado confirmado e validação de certificado.");
        using var connection = new SqlConnection(connectionString) { AccessToken = Environment.GetEnvironmentVariable("EBT_SQL_ACCESS_TOKEN") ?? throw new InvalidOperationException("Token temporário necessário.") };
        await connection.OpenAsync(); var reports = new Dictionary<string, object>();
        foreach (var (name, sql) in new[] {
            ("schemas", "SELECT s.name, COUNT(t.object_id) AS tables FROM sys.schemas s INNER JOIN sys.tables t ON t.schema_id=s.schema_id GROUP BY s.name ORDER BY s.name"),
            ("storage", "SELECT SUM(CONVERT(bigint,FILEPROPERTY(name,'SpaceUsed')))*8192 AS usedBytes,SUM(CONVERT(bigint,size))*8192 AS allocatedBytes FROM sys.database_files WHERE type=0"),
            ("securityPolicies", "SELECT SCHEMA_NAME(schema_id) AS schemaName,name,is_enabled FROM sys.security_policies ORDER BY name") })
        {
            using var command = new SqlCommand(sql, connection); using var reader = await command.ExecuteReaderAsync(); var rows = new List<Dictionary<string, object>>();
            while (await reader.ReadAsync()) { var row = new Dictionary<string, object>(); for (var i = 0; i < reader.FieldCount; i++) row[reader.GetName(i)] = reader.IsDBNull(i) ? "" : reader.GetValue(i); rows.Add(row); }
            reports[name] = rows;
        }
        await File.WriteAllTextAsync(output, JsonSerializer.Serialize(new { generatedUtc = DateTimeOffset.UtcNow, environment = "Azure SQL shared database", server = settings.DataSource, database = settings.InitialCatalog, mode = "read-only metadata", reports }, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine("Metadados Azure conferidos, sem alterações de schema, dados, permissões ou plano.");
    }
}
