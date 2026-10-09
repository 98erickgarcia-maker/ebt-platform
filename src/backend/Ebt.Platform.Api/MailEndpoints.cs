using Microsoft.EntityFrameworkCore;
using System.Text;
using System.Text.RegularExpressions;

namespace Ebt.Platform.Api;

public static class MailEndpoints
{
    public static string Day(DateTimeOffset at) => TimeZoneInfo.ConvertTime(at, TimeZoneInfo.FindSystemTimeZoneById("America/Sao_Paulo")).ToString("yyyy-MM-dd");
    public static IQueryable<MailDraft> Visible(PlatformDb db, AccessScope access) => db.MailDrafts.Where(x => db.VisibleContacts(access).Any(c => c.Id == x.ContactId));
    static async Task<MailDraft> Draft(Guid id, PlatformDb db, AccessScope access) => await Visible(db, access).SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound();
    public static void Snapshot(PlatformDb db, MailDraft row, Guid actor, string reason, string key = "", string hash = "") => db.MailRevisions.Add(new MailRevision { TenantId = row.TenantId, DraftId = row.Id, ActorId = actor, Subject = row.Subject, Body = row.Body, Recipient = row.Recipient, State = row.State, Reason = reason, OperationKey = key, PayloadHash = hash });
    public static async Task<bool> Suppressed(PlatformDb db, string recipient) => await db.MailSuppressions.AnyAsync(x => x.Active && (x.Value == recipient || x.Value == recipient.Substring(recipient.IndexOf('@') + 1)));
    static async Task<MailTemplate> Template(Guid id, PlatformDb db, AccessScope access) => await db.MailTemplates.SingleOrDefaultAsync(x => x.Id == id && (access.IsAdmin || x.Portfolio == access.Portfolio)) ?? throw ApiFault.NotFound();
    public static string Personalize(string text, Contact contact, string company) => text.Replace("{nome}", contact.Name).Replace("{empresa}", company == "" ? "sua empresa" : company).Replace("{email}", contact.Email).Replace("{cargo}", contact.ContactRole).Replace("{necessidade}", contact.Need);
    static void ValidateTemplate(string text)
    {
        foreach (Match match in Regex.Matches(text, @"\{[^{}]*\}"))
            if (match.Value is not ("{nome}" or "{empresa}" or "{email}" or "{cargo}" or "{necessidade}")) throw new ApiFault(400, "mail_placeholder", "Use {nome}, {empresa}, {email}, {cargo} ou {necessidade}.");
    }
    static void ValidateTemplateOptions(MailTemplateCommand command)
    {
        if (command.Channel is not ("email" or "whatsapp" or "phone") || command.Purpose is not ("prospection" or "followup" or "proposal" or "relationship"))
            throw new ApiFault(400, "invalid_template_options", "Selecione canal e objetivo disponíveis.");
        ValidateTemplate(command.Subject + command.Body);
    }
    public static async Task<DocumentVersion?> Attachment(PlatformDb db, MailDraft draft, bool development)
    {
        if (draft.DocumentId == null) return null;
        var doc = await db.Documents.SingleOrDefaultAsync(x => x.Id == draft.DocumentId && x.ContactId == draft.ContactId) ?? throw ApiFault.NotFound();
        var version = await db.DocumentVersions.SingleOrDefaultAsync(x => x.DocumentId == doc.Id && x.Number == draft.DocumentNumber) ?? throw ApiFault.NotFound();
        if (doc.CurrentVersion != version.Number || doc.ReviewState != "approved" || version.ReviewState != "approved") throw new ApiFault(409, "mail_attachment_changed", "O anexo mudou ou aguarda aprovação. Revise o rascunho.");
        DocumentSafety.RequireRelease(development, version.ScanState);
        if (Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(version.Content)).ToLowerInvariant() != version.Sha256) throw new ApiFault(503, "document_integrity", "Integridade do anexo divergente.");
        return version;
    }
    static async Task Fill(MailDraft row, MailDraftCommand command, PlatformDb db, AccessScope access, bool development)
    {
        var contact = await db.Contact(command.ContactId, access);
        if (command.TemplateId != null)
        {
            var template = await Template(command.TemplateId.Value, db, access);
            if (!template.Active || template.Channel != "email" || template.Version != command.TemplateVersion)
                throw new ApiFault(409, "mail_template_changed", "O modelo mudou ou foi desativado. Aplique a versão atual antes de salvar.");
            row.Origin = $"template:{template.Id}:v{template.Version}";
        }
        if (contact.Email == "") throw new ApiFault(400, "mail_no_recipient", "Cadastre um e-mail no contato antes de preparar a mensagem.");
        row.Recipient = contact.Email; row.Subject = Contract.Required(command.Subject, 200, "Assunto"); row.Body = Contract.Required(command.Body, 12000, "Mensagem", true);
        row.DocumentId = command.DocumentId; row.DocumentNumber = null;
        if (command.DocumentId != null)
        {
            var doc = await db.Documents.SingleOrDefaultAsync(x => x.Id == command.DocumentId && x.ContactId == contact.Id) ?? throw ApiFault.NotFound();
            row.DocumentNumber = doc.CurrentVersion; await Attachment(db, row, development);
        }
    }
    public static void Map(WebApplication app)
    {
        const string p = "/api/connect/v1/mail";
        app.MapGet(p + "/status", async (PlatformDb db, AccessScope access, IConfiguration config) =>
        {
            var settings = await db.MailSettings.AsNoTracking().SingleOrDefaultAsync(); var day = Day(DateTimeOffset.UtcNow);
            var used = await db.MailQuotas.Where(x => x.Day == day).Select(x => x.Used).SingleOrDefaultAsync();
            var query = Visible(db, access);
            return Results.Ok(new { configured = GraphMail.Configured(config, access.TenantId), sender = GraphMail.Sender(config, access.TenantId), paused = settings?.Paused ?? true, intervalSeconds = settings?.IntervalSeconds ?? 3, dailyCap = settings?.DailyCap ?? 100, version = settings?.Version ?? 0, day, used, ai = "local_template", counts = await query.GroupBy(x => x.State).Select(x => new { state = x.Key, count = x.Count() }).ToListAsync() });
        });
        app.MapPut(p + "/settings", async (MailSettingsCommand command, PlatformDb db, AccessScope access, HttpContext http, IConfiguration config) =>
        {
            access.RequireAdmin(); if (command.IntervalSeconds is < 1 or > 60 || command.DailyCap is < 1 or > 2000) throw new ApiFault(400, "mail_limits", "Intervalo: 1 a 60 segundos. Limite diário: 1 a 2000.");
            if (!command.Paused && !GraphMail.Configured(config, access.TenantId)) throw new ApiFault(409, "mail_unconfigured", "A caixa Microsoft precisa de configuração e permissão de envio no servidor.");
            await using var tx = await db.Lock("mail-dispatch"); var row = await db.MailSettings.SingleOrDefaultAsync(); Contract.Match(http.Request, row?.Version ?? 0);
            if (row == null) { row = new MailSettings { TenantId = access.TenantId }; db.MailSettings.Add(row); }
            if (row.NextSendAt != null && command.IntervalSeconds > row.IntervalSeconds) row.NextSendAt = row.NextSendAt.Value.AddSeconds(command.IntervalSeconds - row.IntervalSeconds);
            row.IntervalSeconds = command.IntervalSeconds; row.DailyCap = command.DailyCap; row.Paused = command.Paused;
            db.Record(access, "mail.settings_changed", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(new { row.Version });
        });
        app.MapGet(p + "/templates", async (PlatformDb db, AccessScope access) => Results.Ok(await db.MailTemplates.AsNoTracking().Where(x => access.IsAdmin || x.Portfolio == access.Portfolio).OrderBy(x => x.Name).ThenBy(x => x.Id).ToListAsync()));
        app.MapPost(p + "/templates", async (MailTemplateCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); var hash = Contract.Payload(command); ValidateTemplateOptions(command);
            await using var tx = await db.Lock("mail-templates"); var row = await db.MailTemplates.SingleOrDefaultAsync(x => x.CreationKey == key);
            if (row != null) { await Template(row.Id, db, access); Contract.Replay(row.CreationHash, hash); return Results.Ok(row); }
            row = new MailTemplate { TenantId = access.TenantId, Portfolio = access.Portfolio, CreationKey = key, CreationHash = hash, Name = Contract.Required(command.Name, 100, "Nome do modelo"), Subject = Contract.Required(command.Subject, 200, "Assunto"), Body = Contract.Required(command.Body, 12000, "Mensagem", true), Active = command.Active, Channel = command.Channel, Purpose = command.Purpose };
            db.MailTemplates.Add(row); db.Record(access, "mail.template_created", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(row);
        });
        app.MapPut(p + "/templates/{id:guid}", async (Guid id, MailTemplateCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); ValidateTemplateOptions(command); var row = await Template(id, db, access); Contract.Match(http.Request, row.Version);
            row.Name = Contract.Required(command.Name, 100, "Nome do modelo"); row.Subject = Contract.Required(command.Subject, 200, "Assunto"); row.Body = Contract.Required(command.Body, 12000, "Mensagem", true); row.Active = command.Active; row.Channel = command.Channel; row.Purpose = command.Purpose;
            db.Record(access, "mail.template_updated", id, http.TraceIdentifier); await db.SaveChangesAsync(); return Results.Ok(row);
        });
        app.MapGet(p + "/templates/{id:guid}/preview", async (Guid id, Guid contactId, PlatformDb db, AccessScope access) =>
        {
            var template = await Template(id, db, access); var contact = await db.Contact(contactId, access);
            if (!template.Active) throw new ApiFault(409, "template_inactive", "Este modelo está desativado.");
            var company = await db.Organizations.Where(x => x.Id == contact.OrganizationId && x.Portfolio == contact.Portfolio).Select(x => x.Name).SingleOrDefaultAsync() ?? "";
            return Results.Ok(new { template.Id, template.Version, template.Channel, template.Purpose, subject = Personalize(template.Subject, contact, company), body = Personalize(template.Body, contact, company) });
        });
        app.MapGet(p + "/drafts", async (Guid? contactId, string? state, string? search, int? page, int? limit, PlatformDb db, AccessScope access) =>
        {
            if (contactId != null) await db.Contact(contactId.Value, access); var query = Visible(db, access).AsNoTracking();
            if (contactId != null) query = query.Where(x => x.ContactId == contactId); if (!string.IsNullOrWhiteSpace(state)) query = query.Where(x => x.State == state);
            var term = Contract.Optional(search, 160, "Busca"); if (term != "") query = query.Where(x => x.Subject.Contains(term) || x.Recipient.Contains(term));
            var size = Math.Clamp(limit ?? 25, 1, 100); var index = Math.Clamp(page ?? 1, 1, 1000000);
            return Results.Ok(new { total = await query.CountAsync(), page = index, limit = size, items = await query.OrderByDescending(x => x.CreatedAt).ThenBy(x => x.Id).Skip((index - 1) * size).Take(size).ToListAsync() });
        });
        app.MapGet(p + "/drafts/{id:guid}", async (Guid id, PlatformDb db, AccessScope access) => Results.Ok(await Draft(id, db, access)));
        app.MapGet(p + "/drafts/{id:guid}/history", async (Guid id, int? page, PlatformDb db, AccessScope access) =>
        {
            await Draft(id, db, access); var query = db.MailRevisions.AsNoTracking().Where(x => x.DraftId == id); var index = Math.Clamp(page ?? 1, 1, 1000000);
            return Results.Ok(new { total = await query.CountAsync(), items = await query.OrderByDescending(x => x.At).ThenBy(x => x.Id).Skip((index - 1) * 25).Take(25).ToListAsync() });
        });
        app.MapPost(p + "/drafts", async (MailDraftCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); var hash = Contract.Payload(command);
            await using var tx = await db.Lock("mail-drafts"); var row = await db.MailDrafts.SingleOrDefaultAsync(x => x.CreationKey == key);
            if (row != null) { await Draft(row.Id, db, access); Contract.Replay(row.CreationHash, hash); return Results.Ok(row); }
            row = new MailDraft { TenantId = access.TenantId, ContactId = command.ContactId, ActorId = access.UserId, CreationKey = key, CreationHash = hash };
            await Fill(row, command, db, access, app.Environment.IsDevelopment()); db.MailDrafts.Add(row); Snapshot(db, row, access.UserId, "created");
            db.Record(access, "mail.draft_created", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(row);
        });
        app.MapPost(p + "/batch", async (MailBatchCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); if (command.ContactIds == null || command.ContactIds.Length is < 1 or > 100 || command.ContactIds.Distinct().Count() != command.ContactIds.Length) throw new ApiFault(400, "mail_batch_limit", "Selecione de 1 a 100 contatos distintos.");
            var key = Contract.Idempotency(http.Request); var hash = Contract.Payload(command); await using var tx = await db.Lock("mail-drafts");
            var replayKey = "batch:" + Contract.Hash(key)[..48]; var prior = await db.MailDrafts.Where(x => x.CreationKey.StartsWith(replayKey + ":")).ToListAsync();
            if (prior.Count > 0) { foreach (var item in prior) { await Draft(item.Id, db, access); Contract.Replay(item.CreationHash, hash); } return Results.Ok(prior); }
            var template = await Template(command.TemplateId, db, access); if (!template.Active || template.Channel != "email") throw new ApiFault(409, "mail_template_inactive", "Modelo inativo.");
            var result = new List<MailDraft>(); var addresses = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var id in command.ContactIds)
            {
                var contact = await db.Contact(id, access); if (contact.Email == "" || !addresses.Add(contact.Email)) throw new ApiFault(400, "mail_ambiguous_recipient", "O lote contém e-mail ausente ou destinatário repetido. Revise os contatos.");
                if (await Suppressed(db, contact.Email)) throw new ApiFault(409, "mail_suppressed", "Um destinatário está bloqueado. Nenhum rascunho deste lote foi criado.");
                var company = contact.OrganizationId == null ? "" : await db.Organizations.Where(x => x.Id == contact.OrganizationId && x.Portfolio == contact.Portfolio).Select(x => x.Name).SingleOrDefaultAsync() ?? "";
                var row = new MailDraft { TenantId = access.TenantId, ContactId = id, ActorId = access.UserId, CreationKey = replayKey + ":" + id.ToString("N"), CreationHash = hash, Origin = "template:" + template.Id + ":" + template.Version };
                await Fill(row, new MailDraftCommand(id, Personalize(template.Subject, contact, company), Personalize(template.Body, contact, company)), db, access, app.Environment.IsDevelopment());
                db.MailDrafts.Add(row); Snapshot(db, row, access.UserId, "batch_created"); result.Add(row);
            }
            db.Record(access, "mail.batch_prepared", template.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(result);
        });
        app.MapPut(p + "/drafts/{id:guid}", async (Guid id, MailDraftCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); await using var tx = await db.Lock("mail-dispatch"); var row = await Draft(id, db, access); Contract.Match(http.Request, row.Version);
            if (row.ContactId != command.ContactId || row.State is "queued" or "processing" or "accepted" or "unknown" or "cancelled") throw new ApiFault(409, "mail_state", "Este estado não permite editar. Cancele a fila antes de revisar.");
            await Fill(row, command, db, access, app.Environment.IsDevelopment()); row.State = "draft"; row.ApprovedAt = null; row.ApprovedBy = null; row.Diagnostic = "";
            Snapshot(db, row, access.UserId, "edited_approval_invalidated"); db.Record(access, "mail.draft_edited", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(row);
        });
        app.MapPost(p + "/drafts/{id:guid}/action", async (Guid id, MailActionCommand command, PlatformDb db, AccessScope access, HttpContext http, IConfiguration config) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); var hash = Contract.Payload(command); await using var tx = await db.Lock("mail-dispatch"); var row = await Draft(id, db, access);
            var prior = await db.MailRevisions.SingleOrDefaultAsync(x => x.DraftId == id && x.OperationKey == key);
            if (prior != null) { Contract.Replay(prior.PayloadHash, hash); return Results.Ok(row); }
            Contract.Match(http.Request, row.Version); var contact = await db.Contact(row.ContactId, access);
            if (command.Action is "approve" or "queue")
            {
                if (row.Recipient != contact.Email || await Suppressed(db, row.Recipient)) throw new ApiFault(409, "mail_recipient_changed", "Destinatário alterado ou bloqueado. Revise a mensagem.");
                await Attachment(db, row, app.Environment.IsDevelopment());
            }
            switch (command.Action)
            {
                case "approve":
                    access.RequireAdmin(); if (row.State is not ("draft" or "failed")) throw new ApiFault(409, "mail_state", "Revise um rascunho antes de aprovar.");
                    row.State = "approved"; row.ApprovedBy = access.UserId; row.ApprovedAt = DateTimeOffset.UtcNow; break;
                case "queue":
                    if (row.State != "approved") throw new ApiFault(409, "mail_state", "É necessária aprovação da versão atual.");
                    if (!GraphMail.Configured(config, access.TenantId)) throw new ApiFault(409, "mail_unconfigured", "Envio real indisponível. Configure Microsoft Graph no servidor.");
                    row.State = "queued"; break;
                case "cancel":
                    if (row.State is not ("draft" or "approved" or "queued" or "failed")) throw new ApiFault(409, "mail_state", "Envio iniciado ou incerto precisa de reconciliação."); row.State = "cancelled"; break;
                case "reconcile":
                    access.RequireAdmin(); if (row.State != "unknown") throw new ApiFault(409, "mail_state", "Somente um envio incerto pode ser reconciliado.");
                    Contract.Required(command.Reason, 1000, "Evidência de conferência dos Itens Enviados", true); row.State = "reconciled"; break;
                default: throw new ApiFault(400, "mail_action", "Ação de e-mail inválida.");
            }
            Snapshot(db, row, access.UserId, Contract.Optional(command.Reason, 1000, "Motivo", true) is { Length: > 0 } reason ? reason : command.Action, key, hash);
            db.Record(access, "mail." + command.Action, id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(row);
        });
        app.MapGet(p + "/drafts/{id:guid}/eml", async (Guid id, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            var row = await Draft(id, db, access); db.Record(access, "mail.draft_exported", id, http.TraceIdentifier); await db.SaveChangesAsync();
            var subject = Convert.ToBase64String(Encoding.UTF8.GetBytes(row.Subject));
            var content = "To: " + row.Recipient + "\r\nSubject: =?utf-8?B?" + subject + "?=\r\nX-Unsent: 1\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" + Convert.ToBase64String(Encoding.UTF8.GetBytes(row.Body), Base64FormattingOptions.InsertLineBreaks);
            return Results.File(Encoding.UTF8.GetBytes(content), "message/rfc822", "rascunho-" + id + ".eml");
        });
        app.MapGet(p + "/suppression", async (PlatformDb db, AccessScope access) => { access.RequireAdmin(); return Results.Ok(await db.MailSuppressions.AsNoTracking().OrderBy(x => x.Value).ToListAsync()); });
        app.MapPost(p + "/suppression", async (MailSuppressionCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireAdmin(); var value = Contract.Required(command.Value, 254, "E-mail ou domínio").ToLowerInvariant();
            if (value.Contains('@')) value = Contract.Email(value); else if (!Uri.CheckHostName(value).Equals(UriHostNameType.Dns) || !value.Contains('.')) throw new ApiFault(400, "mail_domain", "Informe e-mail ou domínio válido.");
            await using var tx = await db.Lock("mail-dispatch"); var row = await db.MailSuppressions.SingleOrDefaultAsync(x => x.Value == value);
            if (row == null) { row = new MailSuppression { TenantId = access.TenantId, Value = value }; db.MailSuppressions.Add(row); }
            row.Reason = Contract.Required(command.Reason, 1000, "Motivo", true); row.ActorId = access.UserId; row.Active = command.Active;
            db.Record(access, command.Active ? "mail.suppressed" : "mail.suppression_released", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(row);
        });
    }
}
