using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public static class RecoveryChecks
{
    public static async Task Run(PlatformDb db, AccessScope scope, IDataProtectionProvider provider, IConfiguration config)
    {
        var sql = new Microsoft.Data.SqlClient.SqlConnectionStringBuilder(db.Database.GetConnectionString());
        if (!sql.InitialCatalog.StartsWith("EbtPlatformQa_", StringComparison.Ordinal) || sql.DataSource is not ("localhost" or "." or "127.0.0.1")) throw new InvalidOperationException("Recuperação de teste exige QA local exclusivo.");
        scope.System = true;
        var documents = await db.DocumentVersions.IgnoreQueryFilters().AsNoTracking().ToListAsync();
        if (documents.Count == 0) throw new InvalidOperationException("Fixture sem documentos; não comprova recuperação.");
        foreach (var version in documents)
            if (Convert.ToHexString(SHA256.HashData(version.Content)).ToLowerInvariant() != version.Sha256) throw new InvalidOperationException("Hash documental divergente.");
        var receipts = await db.Receipts.AsNoTracking().Where(x => x.ProtectedBody != "").ToListAsync();
        foreach (var receipt in receipts)
        {
            var v2 = receipt.ProtectedBody.StartsWith("v2:", StringComparison.Ordinal);
            var raw = v2 ? provider.CreateProtector("connect.webhook.v2", receipt.AppKey, receipt.BodyHash).Unprotect(receipt.ProtectedBody[3..]) : provider.CreateProtector("connect.webhook.v1").Unprotect(receipt.ProtectedBody);
            if (Convert.ToHexString(SHA256.HashData(Convert.FromBase64String(raw))).ToLowerInvariant() != receipt.BodyHash) throw new InvalidOperationException("Envelope recuperado divergente.");
        }
        var unknown = await db.Outbox.IgnoreQueryFilters().CountAsync(x => x.State == "unknown");
        if (unknown == 0 || receipts.Count == 0) throw new InvalidOperationException("Fixture deve incluir envelopes e envio incerto.");
        var report = new { generatedUtc = DateTimeOffset.UtcNow, environment = sql.InitialCatalog, passed = true, documentVersionsVerified = documents.Count, encryptedReceiptsVerified = receipts.Count, contacts = await db.Contacts.IgnoreQueryFilters().CountAsync(), messages = await db.Messages.IgnoreQueryFilters().CountAsync(), unknown };
        await File.WriteAllTextAsync(config["Qa:RecoveryReport"] ?? throw new InvalidOperationException("Configure relatório de recuperação."), JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine($"PASS {documents.Count} versões documentais e {receipts.Count} envelopes recuperados.");
    }
}
