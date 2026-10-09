using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public sealed record MailSendResult(string State, string Code);
public static class GraphMail
{
    // One explicit EBT tenant/mailbox binding; never use another application's credentials.
    public static bool Configured(IConfiguration config, Guid tenant) => Guid.TryParse(config["Mail:PlatformTenantId"], out var bound) && bound == tenant
        && Guid.TryParse(config["Mail:MicrosoftTenantId"], out _) && Guid.TryParse(config["Mail:ClientId"], out _)
        && !string.IsNullOrWhiteSpace(config["Mail:ClientSecret"]) && config.GetValue<bool>("Mail:Enabled")
        && !string.IsNullOrWhiteSpace(config["Mail:Sender"]);
    public static string Sender(IConfiguration config, Guid tenant) => Configured(config, tenant) ? Contract.Email(config["Mail:Sender"]) : "";
    public static MailSendResult Classify(HttpStatusCode status) => (int)status switch
    {
        202 => new("accepted", "graph_accepted_not_delivery"),
        429 => new("failed", "graph_throttled"),
        >= 500 => new("unknown", "graph_uncertain"),
        _ => new("failed", "graph_rejected")
    };
    public static async Task<MailSendResult> Send(HttpClient client, IConfiguration config, MailDraft row, DocumentVersion? attachment, CancellationToken ct)
    {
        if (!Configured(config, row.TenantId)) return new("failed", "mail_unconfigured");
        string token;
        try
        {
            using var request = new HttpRequestMessage(HttpMethod.Post, "https://login.microsoftonline.com/" + Guid.Parse(config["Mail:MicrosoftTenantId"]!) + "/oauth2/v2.0/token")
            {
                Content = new FormUrlEncodedContent(new Dictionary<string, string> { ["client_id"] = config["Mail:ClientId"]!, ["client_secret"] = config["Mail:ClientSecret"]!, ["grant_type"] = "client_credentials", ["scope"] = "https://graph.microsoft.com/.default" })
            };
            using var response = await client.SendAsync(request, ct);
            if (!response.IsSuccessStatusCode) return new("failed", "graph_authentication_failed");
            using var payload = JsonDocument.Parse(await response.Content.ReadAsStringAsync(ct));
            if (payload.RootElement.ValueKind != JsonValueKind.Object ||
                !payload.RootElement.TryGetProperty("access_token", out var accessToken) ||
                accessToken.ValueKind != JsonValueKind.String ||
                string.IsNullOrWhiteSpace(accessToken.GetString()))
                return new("failed", "graph_authentication_failed");
            token = accessToken.GetString()!;
        }
        catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException or JsonException or KeyNotFoundException) { return new("failed", "graph_authentication_failed"); }
        var attachments = attachment == null ? Array.Empty<object>() : [new Dictionary<string, object> { ["@odata.type"] = "#microsoft.graph.fileAttachment", ["name"] = attachment.FileName, ["contentType"] = attachment.MediaType, ["contentBytes"] = Convert.ToBase64String(attachment.Content) }];
        using var message = new HttpRequestMessage(HttpMethod.Post, "https://graph.microsoft.com/v1.0/users/" + Uri.EscapeDataString(Sender(config, row.TenantId)) + "/sendMail")
        {
            Content = JsonContent.Create(new { message = new { subject = row.Subject, body = new { contentType = "Text", content = row.Body }, toRecipients = new[] { new { emailAddress = new { address = row.Recipient } } }, attachments, internetMessageHeaders = new[] { new { name = "x-ebt-operation", value = row.Id.ToString() } } }, saveToSentItems = true })
        };
        message.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        try { using var response = await client.SendAsync(message, ct); return Classify(response.StatusCode); }
        catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException) { return new("unknown", "graph_network_uncertain"); }
    }
}

public sealed class MailWorker(IServiceScopeFactory services, IConfiguration config, IHostEnvironment environment, ILogger<MailWorker> logger) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (!config.GetValue("Platform:RunWorkers", true)) return;
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var service = services.CreateScope(); var db = service.ServiceProvider.GetRequiredService<PlatformDb>();
                var tenants = await db.Tenants.AsNoTracking().Where(x => x.Active).Select(x => x.Id).ToListAsync(stoppingToken);
                foreach (var tenant in tenants) await Process(tenant, stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested) { break; }
            catch (Exception ex) { logger.LogWarning("Mail worker interrupted: {Type}", ex.GetType().Name); }
            await Task.Delay(TimeSpan.FromSeconds(1), stoppingToken);
        }
    }
    public async Task Process(Guid tenant, CancellationToken ct)
    {
        using var service = services.CreateScope(); var access = service.ServiceProvider.GetRequiredService<AccessScope>(); access.TenantId = tenant;
        var db = service.ServiceProvider.GetRequiredService<PlatformDb>(); Guid draftId;
        // Durable reservation BEFORE HTTP. A crash leaves processing -> unknown, never automatic resend.
        await using (var tx = await db.Lock("mail-dispatch", ct))
        {
            var now = DateTimeOffset.UtcNow;
            var expired = await db.MailDrafts.Where(x => x.State == "processing" && x.AttemptedAt < now.AddMinutes(-2)).ToListAsync(ct);
            foreach (var item in expired) { item.State = "unknown"; item.Diagnostic = "worker_restart_uncertain"; MailEndpoints.Snapshot(db, item, Guid.Empty, item.Diagnostic); }
            await db.SaveChangesAsync(ct);
            var settings = await db.MailSettings.SingleOrDefaultAsync(ct);
            if (expired.Count > 0 && settings != null) { settings.Paused = true; await db.SaveChangesAsync(ct); }
            if (settings == null || settings.Paused || settings.NextSendAt > now || !GraphMail.Configured(config, tenant)) { await tx.CommitAsync(ct); return; }
            // Another replica may be between its durable reservation and HTTP completion.
            // It owns the only active call; never pause its reserved slot or claim a second one.
            if (await db.MailDrafts.AnyAsync(x => x.State == "processing", ct)) { await tx.CommitAsync(ct); return; }
            var row = await db.MailDrafts.Where(x => x.State == "queued").OrderBy(x => x.CreatedAt).ThenBy(x => x.Id).FirstOrDefaultAsync(ct);
            if (row == null) { await tx.CommitAsync(ct); return; }
            var day = MailEndpoints.Day(now); var quota = await db.MailQuotas.SingleOrDefaultAsync(x => x.Day == day, ct);
            if (quota == null) { quota = new MailQuota { TenantId = tenant, Day = day }; db.MailQuotas.Add(quota); }
            if (quota.Used >= settings.DailyCap) { settings.Paused = true; await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); return; }
            row.State = "processing"; row.AttemptedAt = now; quota.Used++; settings.NextSendAt = now.AddSeconds(settings.IntervalSeconds);
            MailEndpoints.Snapshot(db, row, Guid.Empty, "reserved"); await db.SaveChangesAsync(ct); await tx.CommitAsync(ct); draftId = row.Id;
        }
        // Cross-replica SQL lock serializes individual calls, not batches. No HTTP retry handler.
        await using (var tx = await db.Lock("mail-dispatch", ct))
        {
            db.ChangeTracker.Clear(); var row = await db.MailDrafts.SingleAsync(x => x.Id == draftId, ct); if (row.State != "processing") { await tx.CommitAsync(ct); return; }
            await db.LockResource("contact:" + row.ContactId, ct);
            var settings = await db.MailSettings.SingleAsync(ct); MailSendResult result;
            try
            {
                var member = await db.Memberships.SingleOrDefaultAsync(x => x.UserId == row.ActorId && x.Active, ct);
                var approver = await db.Memberships.SingleOrDefaultAsync(x => x.UserId == row.ApprovedBy && x.Active && x.Role == "admin", ct);
                var contact = await db.Contacts.SingleOrDefaultAsync(x => x.Id == row.ContactId, ct);
                var activeUsers = await db.Users.CountAsync(x => x.Active && (x.Id == row.ActorId || x.Id == row.ApprovedBy), ct);
                var expectedUsers = row.ActorId == row.ApprovedBy ? 1 : 2;
                if (settings.Paused || contact == null || member == null || approver == null || activeUsers != expectedUsers || member.Role is not ("operator" or "admin") || (member.Role != "admin" && member.Portfolio != contact.Portfolio) || contact.Email != row.Recipient || await MailEndpoints.Suppressed(db, row.Recipient)) result = new("failed", "mail_access_or_recipient_changed");
                else
                {
                    var attachment = await MailEndpoints.Attachment(db, row, environment.IsDevelopment());
                    result = await GraphMail.Send(service.ServiceProvider.GetRequiredService<IHttpClientFactory>().CreateClient("mail"), config, row, attachment, ct);
                }
            }
            catch (ApiFault ex) { result = new("failed", ex.Code); }
            row.State = result.State; row.Diagnostic = result.Code; settings.NextSendAt = DateTimeOffset.UtcNow.AddSeconds(settings.IntervalSeconds);
            if (result.State == "unknown" || result.Code is "graph_throttled" or "graph_authentication_failed") settings.Paused = true;
            MailEndpoints.Snapshot(db, row, Guid.Empty, result.Code);
            db.Interactions.Add(new Interaction { TenantId = tenant, ContactId = row.ContactId, ActorId = row.ActorId, Kind = "email", Content = "E-mail: " + row.Subject + " · " + row.State + " · " + row.Id, OccurredAt = DateTimeOffset.UtcNow, OperationKey = "mail:" + row.Id.ToString("N") });
            await db.SaveChangesAsync(ct); await tx.CommitAsync(ct);
        }
    }
}
