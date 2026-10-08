using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public static class WazVoxEndpoints
{
    public static void Map(WebApplication app)
    {
        app.MapPost("/webhooks/connect/wazvox/{appKey}", async (string appKey, HttpRequest request, IConfiguration config, PlatformDb db, IDataProtectionProvider protector, WorkPulse pulse) =>
        {
            var secret = WazVoxProtocol.Value(config, appKey, "SigningSecret");
            var workspace = WazVoxProtocol.Value(config, appKey, "WorkspaceId");
            if (string.IsNullOrWhiteSpace(secret) || string.IsNullOrWhiteSpace(workspace)) return Results.NotFound();
            if (request.ContentLength > 1_048_576) return Results.StatusCode(413);
            using var body = new MemoryStream(); var buffer = new byte[16384];
            while (true) { var read = await request.Body.ReadAsync(buffer, request.HttpContext.RequestAborted); if (read == 0) break; if (body.Length + read > 1_048_576) return Results.StatusCode(413); await body.WriteAsync(buffer.AsMemory(0, read)); }
            var bytes = body.ToArray();
            if (!WazVoxProtocol.Verify(bytes, request.Headers["X-BSP-Timestamp"].ToString(), request.Headers["X-BSP-Signature"].ToString(), secret, DateTimeOffset.UtcNow)) return Results.Unauthorized();
            string eventId;
            try { eventId = WazVoxProtocol.ValidateEnvelope(bytes, request.Headers["X-BSP-Event-Id"].ToString(), workspace); }
            catch (JsonException) { return Results.BadRequest(new { code = "invalid_wazvox_envelope" }); }
            var hash = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
            var protectedBody = "v2:" + protector.CreateProtector("connect.webhook.v2", appKey, hash).Protect(Convert.ToBase64String(bytes));
            await using var tx = await db.Lock("global:receipt-storage");
            var prior = await db.Receipts.SingleOrDefaultAsync(x => x.AppKey == appKey && x.ProviderEventId == eventId);
            if (prior != null) { if (prior.BodyHash != hash) throw new ApiFault(409, "event_payload_conflict", "O evento já foi registrado com outro conteúdo."); }
            else
            {
                var retained = await db.Receipts.SumAsync(x => (long)x.ProtectedBody.Length * 2);
                if (retained + protectedBody.Length * 2L > 100 * 1024 * 1024) return Results.StatusCode(503);
                db.Receipts.Add(new WebhookReceipt { AppKey = appKey, BodyHash = hash, ProviderEventId = eventId, ProtectedBody = protectedBody });
                await db.SaveChangesAsync();
            }
            await tx.CommitAsync(); pulse.Notify(); return Results.Ok(new { received = true, eventId });
        });
    }
}
