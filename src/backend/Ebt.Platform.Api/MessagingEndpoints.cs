using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public static class MessagingEndpoints
{
    public static async Task<Conversation> VisibleConversation(Guid id, PlatformDb db, AccessScope access)
    {
        var conversation = await db.Conversations.SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound();
        await db.Contact(conversation.ContactId, access); return conversation;
    }
    public static object MessageView(ConnectMessage x) => new { messageId = x.Id, x.ConversationId, x.Direction, x.Content, x.Status, x.ProviderId, x.FailureCode, x.CreatedAt, x.ReplyToMessageId, x.ActorId, x.Version };
    public static object OperationView(ConnectMessage m, OutboxOperation op, Conversation c) => new { messageId = m.Id, operationId = op.Id, status = m.Status, statusUrl = "/api/connect/v1/messages/" + m.Id, version = $"\"{c.Version}\"" };
    public static void Map(WebApplication app)
    {
        const string prefix = "/api/connect/v1";
        app.MapGet(prefix + "/conversations", async (Guid? contactId, AccessScope access, PlatformDb db) =>
        {
            if (contactId != null) await db.Contact(contactId.Value, access);
            var visible = db.VisibleContacts(access).AsNoTracking();
            var rows = await db.Conversations
                .Where(x => contactId == null || x.ContactId == contactId)
                .Join(visible, conversation => conversation.ContactId, contact => contact.Id, (conversation, contact) => new { conversation, contact })
                .Join(db.Connections, x => x.conversation.ConnectionId, channel => channel.Id, (x, channel) => new
                {
                    x.conversation.Id, x.conversation.ContactId,
                    contactName = x.contact.Name, recipient = x.conversation.Recipient,
                    x.conversation.State, x.conversation.LastInboundAt, x.conversation.Version,
                    channelName = channel.Name, provider = channel.Provider
                })
                .OrderByDescending(x => x.LastInboundAt).ThenBy(x => x.Id).Take(100).ToListAsync();
            return Results.Ok(rows);
        });
        app.MapGet(prefix + "/conversations/{id:guid}/messages", async (Guid id, string? cursor, int? limit, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            var conversation = await VisibleConversation(id, db, access); http.Response.Headers.ETag = $"\"{conversation.Version}\"";
            var query = db.Messages.AsNoTracking().Where(x => x.ConversationId == id);
            if (!string.IsNullOrEmpty(cursor))
            {
                if (!Guid.TryParse(cursor, out var lastId)) throw new ApiFault(400, "invalid_cursor", "Página inválida.");
                var last = await db.Messages.AsNoTracking().SingleOrDefaultAsync(x => x.Id == lastId && x.ConversationId == id) ?? throw new ApiFault(400, "invalid_cursor", "Página inválida.");
                query = query.Where(x => x.CreatedAt < last.CreatedAt || x.CreatedAt == last.CreatedAt && x.Id.CompareTo(lastId) < 0);
            }
            var size = Math.Clamp(limit ?? 50, 1, 100); var rows = await query.OrderByDescending(x => x.CreatedAt).ThenByDescending(x => x.Id).Take(size + 1).ToListAsync();
            return Results.Ok(new { items = rows.Take(size).Reverse().Select(MessageView), nextCursor = rows.Count > size ? rows[size - 1].Id.ToString() : null, version = $"\"{conversation.Version}\"" });
        });
        app.MapGet(prefix + "/messages/{id:guid}", async (Guid id, AccessScope access, PlatformDb db) =>
        {
            var message = await db.Messages.AsNoTracking().SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound(); await VisibleConversation(message.ConversationId, db, access); return Results.Ok(MessageView(message));
        });
        app.MapPost(prefix + "/conversations/{id:guid}/messages", async (Guid id, ReplyCommand command, AccessScope access, PlatformDb db, HttpContext http, WorkPulse pulse) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request);
            if (command.ContentType != "text") throw new ApiFault(400, "unsupported_content", "O canal aceita respostas de texto.");
            var content = Contract.Required(command.Content, 4000, "Resposta", true); var hash = Contract.Payload(new { content, command.ContentType, command.ReplyToMessageId });
            await using var tx = await db.Lock("conversation:" + id);
            var conversation = await VisibleConversation(id, db, access);
            var prior = await db.Outbox.SingleOrDefaultAsync(x => x.ConversationId == id && x.OperationKey == key);
            if (prior != null) { Contract.Replay(prior.PayloadHash, hash); var previous = await db.Messages.SingleAsync(x => x.Id == prior.MessageId); return Results.Ok(OperationView(previous, prior, conversation)); }
            Contract.Match(http.Request, conversation.Version);
            var connection = await db.Connections.SingleAsync(x => x.Id == conversation.ConnectionId);
            if (!connection.Active || conversation.State != "open") throw new ApiFault(409, "channel_unavailable", "O canal não está disponível para resposta.");
            if (connection.Provider == "wazvox" && (!app.Configuration.GetValue<bool>("WazVox:Enabled") || conversation.LastInboundAt < DateTimeOffset.UtcNow.AddHours(-24) || conversation.LastInboundAt == null)) throw new ApiFault(409, "reply_policy_blocked", "Resposta de texto indisponível neste canal ou fora da janela de atendimento.");
            if (connection.Provider == "meta" && (!app.Configuration.GetValue<bool>("Meta:Enabled") || conversation.LastInboundAt < DateTimeOffset.UtcNow.AddHours(-24) || conversation.LastInboundAt == null)) throw new ApiFault(409, "reply_policy_blocked", "Resposta de texto indisponível neste canal ou fora da janela de atendimento.");
            if (command.ReplyToMessageId != null && !await db.Messages.AnyAsync(x => x.Id == command.ReplyToMessageId && x.ConversationId == id)) throw new ApiFault(400, "invalid_reply", "Mensagem de referência inválida nesta conversa.");
            var message = new ConnectMessage { TenantId = access.TenantId, ConnectionId = conversation.ConnectionId, ConversationId = id, Direction = "outgoing", Content = content, Status = "queued", ActorId = access.UserId, ReplyToMessageId = command.ReplyToMessageId };
            var operation = new OutboxOperation { TenantId = access.TenantId, MessageId = message.Id, ConversationId = id, ActorId = access.UserId, OperationKey = key, PayloadHash = hash };
            conversation.State = "open"; db.Entry(conversation).Property(x => x.State).IsModified = true;
            db.Messages.Add(message); db.Outbox.Add(operation); db.Record(access, "message.queued", message.Id, http.TraceIdentifier);
            await db.SaveChangesAsync(); await tx.CommitAsync(); pulse.Notify();
            return Results.Json(OperationView(message, operation, conversation), statusCode: 202);
        });
        app.MapGet("/webhooks/connect/meta/{appKey}", (string appKey, HttpRequest request, IConfiguration config) =>
        {
            var verifyToken = AppValue(config, appKey, "VerifyToken");
            var token = request.Query["hub.verify_token"].ToString(); var challenge = request.Query["hub.challenge"].ToString();
            if (verifyToken == null) return Results.NotFound();
            if (request.Query["hub.mode"] != "subscribe" || challenge.Length is < 1 or > 200 || !Contract.EqualsSecret(token, verifyToken)) return Results.Unauthorized();
            return Results.Text(challenge, "text/plain");
        });
        app.MapPost("/webhooks/connect/meta/{appKey}", async (string appKey, HttpRequest request, IConfiguration config, PlatformDb db, IDataProtectionProvider protector, WorkPulse pulse) =>
        {
            var secret = AppValue(config, appKey, "AppSecret");
            if (secret == null) return Results.NotFound();
            if (request.ContentLength > 1_048_576) return Results.StatusCode(413);
            using var body = new MemoryStream(); var buffer = new byte[16384];
            while (true) { var read = await request.Body.ReadAsync(buffer, request.HttpContext.RequestAborted); if (read == 0) break; if (body.Length + read > 1_048_576) return Results.StatusCode(413); await body.WriteAsync(buffer.AsMemory(0, read)); }
            var bytes = body.ToArray(); var signature = request.Headers["X-Hub-Signature-256"].ToString();
            byte[] supplied;
            try { supplied = signature.StartsWith("sha256=", StringComparison.Ordinal) ? Convert.FromHexString(signature[7..]) : []; } catch (FormatException) { return Results.Unauthorized(); }
            if (supplied.Length != 32 || !CryptographicOperations.FixedTimeEquals(supplied, HMACSHA256.HashData(Encoding.UTF8.GetBytes(secret), bytes))) return Results.Unauthorized();
            var hash = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
            var protectedBody = "v2:" + protector.CreateProtector("connect.webhook.v2", appKey, hash).Protect(Convert.ToBase64String(bytes));
            await using var tx = await db.Lock("global:receipt-storage");
            if (!await db.Receipts.AnyAsync(x => x.AppKey == appKey && x.BodyHash == hash))
            {
                var retainedBytes = await db.Receipts.SumAsync(x => (long)x.ProtectedBody.Length * 2);
                if (retainedBytes + protectedBody.Length * 2L > 100 * 1024 * 1024) return Results.StatusCode(503);
                db.Receipts.Add(new WebhookReceipt { AppKey = appKey, BodyHash = hash, ProtectedBody = protectedBody });
                await db.SaveChangesAsync();
            }
            await tx.CommitAsync(); pulse.Notify(); return Results.Ok(new { received = true });
        });
        app.MapGet("/api/admin/communications", async (AccessScope access, PlatformDb db) =>
        {
            access.RequireAdmin(); return Results.Ok(new {
                connections = await db.Connections.AsNoTracking().Select(x => new { x.Id, x.Name, x.Provider, x.AccountId, x.PhoneNumberId, x.Active }).ToListAsync(),
                operations = await db.Outbox.AsNoTracking().OrderByDescending(x => x.DueAt).Take(100).Select(x => new { x.Id, x.MessageId, x.State, x.Attempts, x.DueAt }).ToListAsync(),
                counts = new { pending = await db.Outbox.CountAsync(x => x.State == "pending"), unknown = await db.Outbox.CountAsync(x => x.State == "unknown") } });
        });
    }
    public static string? AppValue(IConfiguration config, string appKey, string field)
    {
        if (appKey.StartsWith("wz-", StringComparison.Ordinal)) return null;
        if (appKey.Length is < 1 or > 100 || !appKey.All(c => char.IsAsciiLetterOrDigit(c) || c == '-')) return null;
        if (appKey == "qa-app" && config["ASPNETCORE_ENVIRONMENT"] == "Development") return config["Qa:" + field];
        return config.GetValue<bool>("Meta:Enabled") ? config[$"Meta:Apps:{appKey}:{field}"] : null;
    }
}
