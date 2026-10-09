using System.Net.Http.Headers;
using System.Text.Json;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public sealed class ConnectWorker(IServiceScopeFactory factory, IConfiguration config, IHostEnvironment environment, ILogger<ConnectWorker> logger, WorkPulse pulse) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (!config.GetValue("Platform:RunWorkers", true)) return;
        while (!stoppingToken.IsCancellationRequested)
        {
            var worked = false;
            try { worked = await ProcessReceipt(stoppingToken); worked |= await ProcessOutbox(stoppingToken); }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested) { break; }
            catch (Exception ex) { logger.LogWarning("Connect worker iteration failed: {Type}", ex.GetType().Name); }
            try { if (worked) await Task.Delay(TimeSpan.FromMilliseconds(100), stoppingToken); else await pulse.Wait(stoppingToken); } catch (OperationCanceledException) { break; }
        }
    }
    static string S(JsonElement e, string name) => e.ValueKind == JsonValueKind.Object && e.TryGetProperty(name, out var x) && x.ValueKind == JsonValueKind.String ? x.GetString() ?? "" : "";
    static IEnumerable<JsonElement> A(JsonElement e, string name) => e.ValueKind == JsonValueKind.Object && e.TryGetProperty(name, out var x) && x.ValueKind == JsonValueKind.Array ? x.EnumerateArray() : [];
    static DateTimeOffset Timestamp(JsonElement e)
    {
        var value = S(e, "timestamp");
        if (!long.TryParse(value, out var seconds) || seconds < 0 || seconds > 253402300799) throw new ApiFault(400, "invalid_event_time", "Evento sem instante válido.");
        var time = DateTimeOffset.FromUnixTimeSeconds(seconds);
        if (time > DateTimeOffset.UtcNow.AddMinutes(5)) throw new ApiFault(400, "invalid_event_time", "Evento fora do período permitido.");
        return time;
    }
    async Task<bool> ProcessReceipt(CancellationToken ct)
    {
        using var service = factory.CreateScope(); var db = service.ServiceProvider.GetRequiredService<PlatformDb>();
        var scope = service.ServiceProvider.GetRequiredService<AccessScope>(); scope.System = true;
        await using var tx = await db.Lock("worker-receipts", ct);
        var retentionCutoff = DateTimeOffset.UtcNow.AddDays(-7);
        await db.Receipts.Where(x => x.State == "processed" && x.ReceivedAt < retentionCutoff && x.ProtectedBody != "").ExecuteUpdateAsync(s => s.SetProperty(x => x.ProtectedBody, ""), ct);
        var receipt = await db.Receipts.Where(x => x.State == "pending").OrderBy(x => x.ReceivedAt).FirstOrDefaultAsync(ct);
        if (receipt == null) return false;
        var diagnostic = new HashSet<string>();
        JsonDocument payload;
        try
        {
            var provider = service.ServiceProvider.GetRequiredService<IDataProtectionProvider>();
            var v2 = receipt.ProtectedBody.StartsWith("v2:", StringComparison.Ordinal);
            var raw = v2 ? provider.CreateProtector("connect.webhook.v2", receipt.AppKey, receipt.BodyHash).Unprotect(receipt.ProtectedBody[3..]) : provider.CreateProtector("connect.webhook.v1").Unprotect(receipt.ProtectedBody);
            var bytes = Convert.FromBase64String(raw);
            if (Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant() != receipt.BodyHash) throw new System.Security.Cryptography.CryptographicException("Envelope integrity mismatch");
            payload = JsonDocument.Parse(bytes, new JsonDocumentOptions { MaxDepth = 48 });
            if (receipt.AppKey.StartsWith("wz-", StringComparison.Ordinal))
            {
                using var original = payload;
                var workspace = WazVoxProtocol.Value(config, receipt.AppKey, "WorkspaceId") ?? "";
                WazVoxProtocol.ValidateEnvelope(bytes, receipt.ProviderEventId, workspace);
                payload = WazVoxProtocol.Normalize(original.RootElement);
            }
        }
        catch (ApiFault ex) { receipt.State = "quarantined"; receipt.Diagnostic = ex.Code; await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); return true; }
        catch (Exception ex) when (ex is JsonException or FormatException or System.Security.Cryptography.CryptographicException) { receipt.State = "quarantined"; receipt.Diagnostic = ex is System.Security.Cryptography.CryptographicException ? "key_unavailable" : "invalid_json"; await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); return true; }
        using (payload)
        {
            if (S(payload.RootElement, "object") != "whatsapp_business_account") diagnostic.Add("unsupported_object");
            else foreach (var entry in A(payload.RootElement, "entry")) foreach (var change in A(entry, "changes"))
            {
                if (change.ValueKind != JsonValueKind.Object || !change.TryGetProperty("value", out var value) || value.ValueKind != JsonValueKind.Object || !value.TryGetProperty("metadata", out var meta) || meta.ValueKind != JsonValueKind.Object) { diagnostic.Add("missing_metadata"); continue; }
                var account = S(entry, "id"); var phone = S(meta, "phone_number_id");
                var connection = await db.Connections.IgnoreQueryFilters().SingleOrDefaultAsync(x => x.AppKey == receipt.AppKey && x.AccountId == account && x.PhoneNumberId == phone && x.Active, ct);
                if (connection == null || !await db.Tenants.AnyAsync(x => x.Id == connection.TenantId && x.Active, ct)) { diagnostic.Add("unknown_connection"); continue; }
                if (connection.Provider == "qa" && !environment.IsDevelopment()) { diagnostic.Add("qa_channel_disabled"); continue; }
                if ((connection.Provider == "wazvox") != receipt.AppKey.StartsWith("wz-", StringComparison.Ordinal)) { diagnostic.Add("provider_mismatch"); continue; }
                scope.TenantId = connection.TenantId;
                if (S(change, "field") != "messages") { diagnostic.Add("unsupported_field"); continue; }
                foreach (var incoming in A(value, "messages"))
                {
                    try { await Incoming(db, connection, incoming, ct); }
                    catch (ApiFault ex) { diagnostic.Add(ex.Code); }
                }
                foreach (var status in A(value, "statuses"))
                {
                    try { await Status(db, connection, status, ct); }
                    catch (ApiFault ex) { diagnostic.Add(ex.Code); }
                }
            }
        }
        receipt.State = diagnostic.Count == 0 ? "processed" : "quarantined"; receipt.Diagnostic = string.Join(',', diagnostic.Order());
        await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); return true;
    }
    static async Task LockConversation(PlatformDb db, Guid tenant, Guid id, CancellationToken ct)
    {
        var resource = $"ebt:{tenant}:conversation:{id}";
        await db.Database.ExecuteSqlInterpolatedAsync($"DECLARE @r int; EXEC @r = sp_getapplock @Resource={resource}, @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=15000; IF @r < 0 THROW 51001, 'Operation busy', 1;", ct);
    }
    static async Task Incoming(PlatformDb db, ChannelConnection connection, JsonElement incoming, CancellationToken ct)
    {
        if (S(incoming, "type") != "text" || !incoming.TryGetProperty("text", out var text)) throw new ApiFault(400, "unsupported_message", "Tipo de mensagem não suportado.");
        var providerId = Contract.Required(S(incoming, "id"), 250, "ID externo"); var recipient = Contract.Phone(S(incoming, "from"));
        if (recipient == "") throw new ApiFault(400, "invalid_phone", "Mensagem sem origem.");
        var content = Contract.Required(S(text, "body"), 4000, "Mensagem", true); var at = Timestamp(incoming);
        if (await db.Messages.AnyAsync(x => x.ConnectionId == connection.Id && x.ProviderId == providerId, ct)) return;
        var operatorMembership = await db.Memberships.SingleOrDefaultAsync(x => x.UserId == connection.OperatorId && x.Active && (x.Role == "admin" || x.Role == "operator") && (x.Role == "admin" || x.Portfolio == connection.Portfolio), ct);
        if (operatorMembership == null) throw new ApiFault(400, "inactive_channel_operator", "Operador do canal inativo.");
        var conversation = await db.Conversations.SingleOrDefaultAsync(x => x.ConnectionId == connection.Id && x.Recipient == recipient, ct);
        if (conversation == null)
        {
            var candidates = await db.Contacts.Where(x => x.Phone == recipient && x.Portfolio == connection.Portfolio).OrderBy(x => x.Id).Take(2).ToListAsync(ct);
            if (candidates.Count > 1) throw new ApiFault(400, "ambiguous_contact", "Contato precisa de reconciliação.");
            var contact = candidates.FirstOrDefault();
            if (contact != null)
            {
                // Serialize the first channel link with an administrator's portfolio change.
                await db.LockResource("contact:" + contact.Id, ct);
                await db.Entry(contact).ReloadAsync(ct);
                if (contact.Portfolio != connection.Portfolio)
                    throw new ApiFault(400, "channel_portfolio_changed", "A carteira do contato mudou.");
            }
            if (contact == null)
            {
                contact = new Contact { TenantId = connection.TenantId, Name = "Novo contato " + recipient[^4..], Phone = recipient, ExternalKey = $"wa:{connection.Id:N}:{recipient}", Portfolio = connection.Portfolio, OwnerId = connection.OperatorId, CreationHash = "webhook" };
                db.Contacts.Add(contact);
            }
            conversation = new Conversation { TenantId = connection.TenantId, ContactId = contact.Id, ConnectionId = connection.Id, Recipient = recipient };
            db.Conversations.Add(conversation); await db.SaveChangesAsync(ct);
        }
        await LockConversation(db, connection.TenantId, conversation.Id, ct);
        await db.Entry(conversation).ReloadAsync(ct);
        if (!await db.Contacts.AnyAsync(x => x.Id == conversation.ContactId && x.Portfolio == connection.Portfolio, ct)) throw new ApiFault(400, "channel_portfolio_changed", "A carteira do contato mudou.");
        if (await db.Messages.AnyAsync(x => x.ConversationId == conversation.Id && x.ProviderId == providerId, ct)) return;
        db.Messages.Add(new ConnectMessage { TenantId = connection.TenantId, ConnectionId = connection.Id, ConversationId = conversation.Id, Content = content, ProviderId = providerId, CreatedAt = at });
        if (conversation.LastInboundAt == null || at > conversation.LastInboundAt) conversation.LastInboundAt = at;
        await db.SaveChangesAsync(ct);
    }
    static async Task Status(PlatformDb db, ChannelConnection connection, JsonElement status, CancellationToken ct)
    {
        var providerId = Contract.Required(S(status, "id"), 250, "ID externo"); var state = S(status, "status");
        if (state is not ("sent" or "delivered" or "read" or "failed")) throw new ApiFault(400, "unsupported_status", "Status não suportado.");
        var at = Timestamp(status); var eventKey = Contract.Payload(new { providerId, state, at, recipient = S(status, "recipient_id") });
        if (!await db.DeliveryEvents.AnyAsync(x => x.ConnectionId == connection.Id && x.EventKey == eventKey, ct))
            db.DeliveryEvents.Add(new DeliveryEvent { TenantId = connection.TenantId, ConnectionId = connection.Id, ProviderId = providerId, Status = state, OccurredAt = at, EventKey = eventKey });
        var query = db.Messages.Where(x => x.ProviderId == providerId && x.ConnectionId == connection.Id);
        var message = await query.SingleOrDefaultAsync(ct);
        if (message == null && Guid.TryParse(S(status, "biz_opaque_callback_data"), out var opId))
        {
            var op = await db.Outbox.SingleOrDefaultAsync(x => x.Id == opId && db.Conversations.Any(c => c.Id == x.ConversationId && c.ConnectionId == connection.Id), ct);
            if (op != null) { message = await db.Messages.SingleAsync(x => x.Id == op.MessageId, ct); if (message.ProviderId == "") message.ProviderId = providerId; else if (message.ProviderId != providerId) throw new ApiFault(400, "provider_reference_conflict", "Referência externa divergente."); }
        }
        await db.SaveChangesAsync(ct);
        if (message != null)
        {
            await LockConversation(db, connection.TenantId, message.ConversationId, ct); await db.Entry(message).ReloadAsync(ct); await Reduce(db, message, connection.Id, ct);
            var uncertain = await db.Outbox.Where(x => x.MessageId == message.Id && x.State == "unknown").ToListAsync(ct);
            foreach (var operation in uncertain) { operation.State = "reconciled"; db.Audit.Add(new AuditEntry { TenantId = connection.TenantId, Action = "outbox.reconciled_by_callback", ResourceId = operation.Id, TraceId = "callback" }); }
            await db.SaveChangesAsync(ct);
        }
    }
    static async Task Reduce(PlatformDb db, ConnectMessage message, Guid connectionId, CancellationToken ct)
    {
        var states = await db.DeliveryEvents.Where(x => x.ConnectionId == connectionId && x.ProviderId == message.ProviderId).Select(x => x.Status).Distinct().ToListAsync(ct);
        foreach (var state in new[] { "read", "delivered", "sent", "failed" }) if (states.Contains(state)) { message.Status = state; message.FailureCode = states.Contains("failed") ? "provider_reported_failure" : ""; break; }
        await db.SaveChangesAsync(ct);
    }
    async Task<bool> ProcessOutbox(CancellationToken ct)
    {
        using var service = factory.CreateScope(); var db = service.ServiceProvider.GetRequiredService<PlatformDb>(); var scope = service.ServiceProvider.GetRequiredService<AccessScope>(); scope.System = true;
        OutboxOperation? operation; ConnectMessage message; Conversation conversation; ChannelConnection connection;
        await using (var tx = await db.Lock("worker-outbox", ct))
        {
            var now = DateTimeOffset.UtcNow;
            operation = await db.Outbox.IgnoreQueryFilters().Where(x => x.State == "pending" && x.DueAt <= now || x.State == "sending" && x.LeaseUntil < now).OrderBy(x => x.DueAt).FirstOrDefaultAsync(ct);
            if (operation == null) return false;
            scope.TenantId = operation.TenantId;
            message = await db.Messages.SingleAsync(x => x.Id == operation.MessageId, ct); conversation = await db.Conversations.SingleAsync(x => x.Id == operation.ConversationId, ct); connection = await db.Connections.SingleAsync(x => x.Id == conversation.ConnectionId, ct);
            if (operation.State == "sending")
            {
                var confirmed = message.ProviderId != "" && message.Status is "sent" or "delivered" or "read" or "failed";
                operation.State = confirmed ? "reconciled" : "unknown";
                if (!confirmed) { message.Status = message.ProviderId == "" ? "unknown" : message.Status; message.FailureCode = "worker_interrupted_after_claim"; }
                await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); return true;
            }
            var actor = await db.Memberships.SingleOrDefaultAsync(x => x.UserId == operation.ActorId && x.Active && (x.Role == "operator" || x.Role == "admin"), ct);
            var contact = await db.Contacts.SingleAsync(x => x.Id == conversation.ContactId, ct);
            var validActor = actor != null && (actor.Role == "admin" || actor.Portfolio == contact.Portfolio);
            var valid = validActor && connection.Active && conversation.State == "open" && contact.Portfolio == connection.Portfolio && await db.Users.AnyAsync(x => x.Id == operation.ActorId && x.Active, ct) && await db.Tenants.AnyAsync(x => x.Id == scope.TenantId && x.Active, ct);
            if (connection.Provider == "qa") valid &= environment.IsDevelopment();
            else if (connection.Provider == "wazvox") valid &= config.GetValue<bool>("WazVox:Enabled") && conversation.LastInboundAt > now.AddHours(-24) && !string.IsNullOrWhiteSpace(config[$"WazVox:Connections:{connection.SecretRef}:ApiKey"]) && !string.IsNullOrWhiteSpace(WazVoxProtocol.Value(config, connection.AppKey, "WorkspaceId"));
            else valid &= connection.Provider == "meta" && config.GetValue<bool>("Meta:Enabled") && conversation.LastInboundAt > now.AddHours(-24) && !string.IsNullOrEmpty(config[$"Meta:Connections:{connection.SecretRef}:AccessToken"]) && !string.IsNullOrEmpty(config["Meta:ApiVersion"]);
            if (!valid) { operation.State = "failed"; message.Status = "failed"; message.FailureCode = "policy_or_access_changed"; await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); return true; }
            operation.State = "sending"; operation.Attempts++; operation.Fence = Guid.NewGuid().ToString("N"); operation.LeaseUntil = now.AddMinutes(2);
            await db.SaveChangesAsync(ct); await tx.CommitAsync(ct);
        }
        var result = "unknown"; var reference = ""; var failure = "provider_result_unknown";
        if (connection.Provider == "qa")
        {
            if (message.Content.StartsWith("QA:unknown", StringComparison.Ordinal)) { /* Simulate a lost response after transmission; never resend. */ }
            else if (message.Content.StartsWith("QA:reject", StringComparison.Ordinal)) { result = "failed"; failure = "provider_rejected"; }
            else { result = "accepted"; reference = "qa." + operation.Id.ToString("N"); failure = ""; }
        }
        else if (connection.Provider == "wazvox")
        {
            try
            {
                var client = service.ServiceProvider.GetRequiredService<IHttpClientFactory>().CreateClient("wazvox");
                var sent = await WazVoxProtocol.Send(client, config[$"WazVox:Connections:{connection.SecretRef}:ApiKey"]!, connection.PhoneNumberId, conversation.Recipient, message.Content, operation.Id, ct);
                result = sent.State; reference = sent.Reference; if (result == "accepted") failure = "";
            }
            catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException or JsonException or InvalidOperationException) { }
        }
        else
        {
            try
            {
                var client = service.ServiceProvider.GetRequiredService<IHttpClientFactory>().CreateClient("meta");
                var version = config["Meta:ApiVersion"]!;
                if (version.Length > 12 || !version.StartsWith('v') || !version[1..].All(c => char.IsAsciiDigit(c) || c == '.')) throw new InvalidOperationException("Invalid configured API version");
                using var request = new HttpRequestMessage(HttpMethod.Post, $"{version}/{Uri.EscapeDataString(connection.PhoneNumberId)}/messages");
                request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", config[$"Meta:Connections:{connection.SecretRef}:AccessToken"]);
                request.Content = JsonContent.Create(new { messaging_product = "whatsapp", recipient_type = "individual", to = conversation.Recipient, type = "text", text = new { body = message.Content }, biz_opaque_callback_data = operation.Id.ToString() });
                using var response = await client.SendAsync(request, ct);
                if (response.IsSuccessStatusCode)
                {
                    using var payload = await JsonDocument.ParseAsync(await response.Content.ReadAsStreamAsync(ct), cancellationToken: ct);
                    reference = A(payload.RootElement, "messages").Select(x => S(x, "id")).FirstOrDefault() ?? "";
                    if (reference.Length is > 0 and <= 250) { result = "accepted"; failure = ""; }
                }
                // Error/timeout semantics require channel homologation. No inferred safe automatic retry.
            }
            catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException or JsonException or InvalidOperationException) { }
        }
        if (ct.IsCancellationRequested) return true; // Expired lease is resolved as unknown on restart.
        await using var final = await db.Lock("conversation:" + conversation.Id, ct);
        var fence = operation.Fence; await db.Entry(operation).ReloadAsync(ct); await db.Entry(message).ReloadAsync(ct);
        if (operation.State != "sending" || operation.Fence != fence) return true;
        if (message.ProviderId != "") { result = "reconciled"; if (reference != "" && reference != message.ProviderId) failure = "provider_reference_conflict"; reference = message.ProviderId; }
        operation.State = result; if (result != "reconciled") message.Status = result; message.ProviderId = reference; message.FailureCode = failure;
        await db.SaveChangesAsync(ct); if (reference != "") await Reduce(db, message, connection.Id, ct);
        await final.CommitAsync(ct); return true;
    }
}
