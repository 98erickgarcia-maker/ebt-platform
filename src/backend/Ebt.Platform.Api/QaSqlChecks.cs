using Microsoft.Data.SqlClient;
using System.Text.Json;

namespace Ebt.Platform.Api;

public static class QaSqlChecks
{
    public static async Task Run(string connectionString, string output)
    {
        var settings = new SqlConnectionStringBuilder(connectionString);
        if (!settings.InitialCatalog.StartsWith("EbtPlatformQa_", StringComparison.Ordinal) || settings.DataSource is not ("localhost" or "127.0.0.1" or ".")) throw new InvalidOperationException("Somente QA local sintético.");
        await using var connection = new SqlConnection(connectionString); await connection.OpenAsync();
        var cases = new List<object>();
        async Task Check(string name, string sql)
        {
            await using var command = new SqlCommand(sql, connection);
            await command.ExecuteNonQueryAsync(); cases.Add(new { name, result = "passed" }); Console.WriteLine("PASS " + name);
        }
        await Check("RLS enabled on EBT schema", "IF NOT EXISTS(SELECT 1 FROM sys.security_policies WHERE name='tenant_barrier' AND SCHEMA_NAME(schema_id)='ebt_connect' AND is_enabled=1) THROW 51020,'RLS missing',1;");
        await Check("Runtime identity granted only own schema", "IF SCHEMA_ID('qa_other') IS NULL EXEC('CREATE SCHEMA qa_other'); IF OBJECT_ID('qa_other.Sentinel') IS NULL BEGIN CREATE TABLE qa_other.Sentinel(Id int PRIMARY KEY, Marker varchar(20) NOT NULL); INSERT qa_other.Sentinel VALUES(1,'preserve'); END; IF USER_ID('EbtConnectQaRuntime') IS NULL CREATE USER EbtConnectQaRuntime WITHOUT LOGIN; GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::ebt_connect TO EbtConnectQaRuntime;");
        await Check("RLS no context sees no contacts", "EXECUTE AS USER='EbtConnectQaRuntime'; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value=NULL; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; IF EXISTS(SELECT 1 FROM ebt_connect.Contacts) BEGIN REVERT; THROW 51021,'Contextless leak',1; END; REVERT;");
        await Check("RLS A cannot read B, including documents", "DECLARE @a uniqueidentifier=(SELECT Id FROM ebt_connect.Tenants WHERE Name LIKE N'%demonstração A'); DECLARE @b uniqueidentifier=(SELECT Id FROM ebt_connect.Tenants WHERE Name LIKE N'%demonstração B'); EXECUTE AS USER='EbtConnectQaRuntime'; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value=@a; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; IF NOT EXISTS(SELECT 1 FROM ebt_connect.Contacts WHERE TenantId=@a) OR EXISTS(SELECT 1 FROM ebt_connect.Contacts WHERE TenantId=@b) OR EXISTS(SELECT 1 FROM ebt_connect.DocumentVersions WHERE TenantId=@b) BEGIN REVERT; THROW 51022,'A/B read barrier failed',1; END; REVERT;");
        await Check("RLS B cannot read existing A document versions", "DECLARE @a uniqueidentifier=(SELECT Id FROM ebt_connect.Tenants WHERE Name LIKE N'%demonstração A'); DECLARE @b uniqueidentifier=(SELECT Id FROM ebt_connect.Tenants WHERE Name LIKE N'%demonstração B'); IF NOT EXISTS(SELECT 1 FROM ebt_connect.DocumentVersions WHERE TenantId=@a) THROW 51026,'Create synthetic A document before document RLS verification',1; EXECUTE AS USER='EbtConnectQaRuntime'; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value=@b; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; IF EXISTS(SELECT 1 FROM ebt_connect.DocumentVersions WHERE TenantId=@a) BEGIN REVERT; THROW 51027,'B can read A documents',1; END; REVERT;");
        await Check("RLS blocks a cross-tenant SQL write", "DECLARE @a uniqueidentifier=(SELECT Id FROM ebt_connect.Tenants WHERE Name LIKE N'%demonstração A'); DECLARE @b uniqueidentifier=(SELECT Id FROM ebt_connect.Tenants WHERE Name LIKE N'%demonstração B'); DECLARE @blocked bit=0; EXECUTE AS USER='EbtConnectQaRuntime'; EXEC sys.sp_set_session_context @key=N'ebt_tenant',@value=@a; EXEC sys.sp_set_session_context @key=N'ebt_system',@value=0; BEGIN TRY INSERT ebt_connect.Organizations(Id,TenantId,Version,Name,ExternalKey,Portfolio) VALUES(NEWID(),@b,1,'Invalid synthetic cross-write',CONVERT(varchar(100),NEWID()),'principal'); END TRY BEGIN CATCH IF ERROR_NUMBER()=33504 SET @blocked=1; ELSE BEGIN REVERT; THROW; END; END CATCH; REVERT; IF @blocked=0 THROW 51023,'Cross write not blocked',1;");
        await Check("Runtime cannot read another application's schema", "DECLARE @blocked bit=0; EXECUTE AS USER='EbtConnectQaRuntime'; BEGIN TRY SELECT * FROM qa_other.Sentinel; END TRY BEGIN CATCH IF ERROR_NUMBER()=229 SET @blocked=1; ELSE BEGIN REVERT; THROW; END; END CATCH; REVERT; IF @blocked=0 THROW 51024,'Other schema accessible',1;");
        await Check("Sentinel preserved", "IF (SELECT COUNT(*) FROM qa_other.Sentinel WHERE Id=1 AND Marker='preserve')<>1 THROW 51025,'Other schema changed',1;");
        await File.WriteAllTextAsync(output, JsonSerializer.Serialize(new { generatedUtc = DateTimeOffset.UtcNow, environment = settings.InitialCatalog, passed = true, cases }, new JsonSerializerOptions { WriteIndented = true }));
    }
}
