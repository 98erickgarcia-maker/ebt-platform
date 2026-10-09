using Microsoft.EntityFrameworkCore;
using System.Text.Json;

namespace Ebt.Platform.Api;

public static class CrmEndpoints
{
    public static object TaskView(ContactTask x) => new { x.Id, x.ContactId, x.Title, x.OwnerId, x.DueAt, x.State, x.Result, x.ClosedAt, x.Version };
    public static async Task<object> ContactView(Contact x, PlatformDb db) => new
    {
        x.Id, x.Name, x.Email, x.Phone, x.ExternalKey, x.OrganizationId, x.OwnerId, x.Portfolio, x.Stage, x.Version, x.CreatedAt, x.ActiveSince,
        prospection = new { x.Source, x.SourceUrl, x.Segment, x.ContactRole, x.Need, x.PreferredChannel, x.BestTime, x.DecisionMaker },
        organizationName = await db.Organizations.Where(o => o.Id == x.OrganizationId && o.Portfolio == x.Portfolio).Select(o => o.Name).SingleOrDefaultAsync(),
        nextAction = await db.Tasks.Where(t => t.ContactId == x.Id && t.State == "open").OrderBy(t => t.DueAt).ThenBy(t => t.Id)
            .Select(t => new { t.Id, t.Title, t.DueAt, t.OwnerId }).FirstOrDefaultAsync()
    };
    public static Contact BuildContact(ContactCommand command, AccessScope access)
    {
        var portfolio = access.IsAdmin ? Contract.Optional(command.Portfolio, 60, "Carteira") : access.Portfolio;
        if (portfolio == "") portfolio = access.Portfolio;
        var stage = command.Stage ?? "novo";
        if (!Contract.Stages.Contains(stage)) throw new ApiFault(400, "invalid_stage", "Etapa inválida.");
        var row = new Contact { TenantId = access.TenantId, Name = Contract.Required(command.Name, 160, "Nome"), Email = Contract.Email(command.Email),
            Phone = Contract.Phone(command.Phone), ExternalKey = Contract.Optional(command.ExternalKey, 100, "Chave externa"), OrganizationId = command.OrganizationId,
            OwnerId = command.OwnerId ?? access.UserId, Portfolio = portfolio, Stage = stage, ActiveSince = stage == "ganho" ? DateTimeOffset.UtcNow : null };
        if (command.Prospection != null) ApplyProspection(row, command.Prospection);
        return row;
    }
    public static void ApplyProspection(Contact row, ProspectionCommand input)
    {
        row.Source = Contract.Optional(input.Source, 160, "Origem");
        row.SourceUrl = Contract.Optional(input.SourceUrl, 500, "Fonte da informação");
        if (row.SourceUrl != "" && (!Uri.TryCreate(row.SourceUrl, UriKind.Absolute, out var url) || url.Scheme != "https" || url.UserInfo != ""))
            throw new ApiFault(400, "invalid_source_url", "Use um endereço HTTPS sem credenciais para a fonte.");
        row.Segment = Contract.Optional(input.Segment, 100, "Segmento");
        row.ContactRole = Contract.Optional(input.ContactRole, 100, "Cargo");
        row.Need = Contract.Optional(input.Need, 2000, "Necessidade identificada", true);
        row.BestTime = Contract.Optional(input.BestTime, 160, "Melhor horário");
        row.PreferredChannel = Contract.Optional(input.PreferredChannel, 20, "Canal preferido");
        row.DecisionMaker = input.DecisionMaker ?? "unknown";
        if (row.PreferredChannel is not ("" or "email" or "whatsapp" or "phone" or "meeting") || row.DecisionMaker is not ("unknown" or "yes" or "no"))
            throw new ApiFault(400, "invalid_qualification", "Selecione canal e decisão nas opções disponíveis.");
    }
    public static async Task ValidateLinks(Contact contact, AccessScope access, PlatformDb db)
    {
        await db.Owner(contact.OwnerId, access, contact.Portfolio);
        if (contact.OrganizationId != null && !await db.Organizations.AnyAsync(x => x.Id == contact.OrganizationId && x.Portfolio == contact.Portfolio))
            throw new ApiFault(400, "invalid_organization", "Selecione uma organização desta carteira.");
    }
    public static void Map(WebApplication app)
    {
        const string prefix = "/api/connect/v1";
        app.MapGet(prefix + "/summary", async (PlatformDb db, AccessScope access) =>
        {
            var contacts = db.VisibleContacts(access);
            var tasks = db.Tasks.Where(x => contacts.Any(c => c.Id == x.ContactId) && x.State == "open");
            var now = DateTimeOffset.UtcNow;
            return Results.Ok(new { contacts = await contacts.CountAsync(), openTasks = await tasks.CountAsync(), overdue = await tasks.CountAsync(x => x.DueAt < now),
                withoutNextAction = await contacts.CountAsync(c => !db.Tasks.Any(t => t.ContactId == c.Id && t.State == "open")),
                stages = await contacts.GroupBy(x => x.Stage).Select(g => new { stage = g.Key, count = g.Count() }).ToListAsync() });
        });
        app.MapGet(prefix + "/contacts", async (string? search, string? stage, bool? withoutNextAction, int? page, int? limit, PlatformDb db, AccessScope access) =>
        {
            var query = db.VisibleContacts(access).AsNoTracking();
            var text = Contract.Optional(search, 160, "Busca");
            if (text != "") query = query.Where(x => x.Name.Contains(text) || x.Email.Contains(text) || x.Phone.Contains(text));
            if (!string.IsNullOrEmpty(stage)) query = query.Where(x => x.Stage == stage);
            if (withoutNextAction == true) query = query.Where(x => !db.Tasks.Any(t => t.ContactId == x.Id && t.State == "open"));
            var p = Math.Clamp(page ?? 1, 1, 10000); var size = Math.Clamp(limit ?? 25, 1, 100);
            var count = await query.CountAsync();
            var items = await query.OrderByDescending(x => x.CreatedAt).ThenBy(x => x.Id).Skip((p - 1) * size).Take(size).Select(x => new {
                x.Id, x.Name, x.Email, x.Phone, x.ExternalKey, x.OrganizationId, x.OwnerId, x.Portfolio, x.Stage, x.Version, x.CreatedAt, x.ActiveSince,
        prospection = new { x.Source, x.SourceUrl, x.Segment, x.ContactRole, x.Need, x.PreferredChannel, x.BestTime, x.DecisionMaker },
                organizationName = db.Organizations.Where(o => o.Id == x.OrganizationId && o.Portfolio == x.Portfolio).Select(o => o.Name).FirstOrDefault(),
                nextAction = db.Tasks.Where(t => t.ContactId == x.Id && t.State == "open").OrderBy(t => t.DueAt).ThenBy(t => t.Id).Select(t => new { t.Id, t.Title, t.DueAt, t.OwnerId }).FirstOrDefault()
            }).ToListAsync();
            return Results.Ok(new { items, total = count, page = p, limit = size });
        });
        app.MapGet(prefix + "/contacts/{id:guid}", async (Guid id, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            var contact = await db.Contact(id, access); http.Response.Headers.ETag = $"\"{contact.Version}\""; return Results.Ok(await ContactView(contact, db));
        });
        app.MapPost(prefix + "/contacts", async (ContactCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request);
            var row = BuildContact(command, access); if (row.ExternalKey == "") row.ExternalKey = "create:" + Contract.Hash(key);
            row.CreationHash = Contract.Payload(command);
            await using var tx = await db.Lock("contacts");
            var receipt = await db.ContactCreations.SingleOrDefaultAsync(x => x.OperationKey == key);
            if (receipt != null)
            {
                var priorContact = await db.Contact(receipt.ContactId, access); Contract.Replay(receipt.PayloadHash, row.CreationHash);
                return Results.Ok(await ContactView(priorContact, db));
            }
            var existing = await db.Contacts.SingleOrDefaultAsync(x => x.ExternalKey == row.ExternalKey);
            if (existing != null)
            {
                if (!access.IsAdmin && existing.Portfolio != access.Portfolio) throw new ApiFault(409, "external_key_unavailable", "Esta chave externa está indisponível.");
                Contract.Replay(existing.CreationHash, row.CreationHash);
                db.ContactCreations.Add(new ContactCreation { TenantId = access.TenantId, ContactId = existing.Id, OperationKey = key, PayloadHash = row.CreationHash });
                await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(await ContactView(existing, db));
            }
            await ValidateLinks(row, access, db);
            db.Contacts.Add(row); db.ContactCreations.Add(new ContactCreation { TenantId = access.TenantId, ContactId = row.Id, OperationKey = key, PayloadHash = row.CreationHash });
            db.Record(access, "contact.created", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync();
            return Results.Created(prefix + "/contacts/" + row.Id, await ContactView(row, db));
        });
        app.MapPut(prefix + "/contacts/{id:guid}", async (Guid id, ContactCommand command, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            access.RequireWrite(); await using var tx = await db.Lock("contact:" + id);
            var row = await db.Contact(id, access); Contract.Match(http.Request, row.Version);
            var candidate = BuildContact(command, access); await ValidateLinks(candidate, access, db);
            if (!access.IsAdmin && candidate.Portfolio != row.Portfolio) throw new ApiFault(403, "forbidden", "Não é permitido mover este contato de carteira.");
            if (candidate.Portfolio != row.Portfolio && await db.Conversations.AnyAsync(x => x.ContactId == row.Id))
                throw new ApiFault(409, "contact_channel_transfer_required", "Este contato possui conversa vinculada a um canal. Mantenha a carteira até existir uma transferência segura do canal e do histórico.");
            if (candidate.Portfolio != row.Portfolio && await db.MailDrafts.AnyAsync(x => x.ContactId == row.Id))
                throw new ApiFault(409, "contact_mail_transfer_required", "Este contato possui histórico de e-mail. A transferência exige revisão do canal e das permissões.");
            row.Name = candidate.Name; row.Email = candidate.Email; row.Phone = candidate.Phone; row.OrganizationId = candidate.OrganizationId;
            row.OwnerId = candidate.OwnerId; row.Stage = candidate.Stage; row.Portfolio = candidate.Portfolio;
            if (row.Stage == "ganho" && row.ActiveSince == null) row.ActiveSince = DateTimeOffset.UtcNow;
            if (command.Prospection != null) ApplyProspection(row, command.Prospection);
            db.Interactions.Add(new Interaction { TenantId = access.TenantId, ContactId = id, ActorId = access.UserId, Kind = "change", Content = "Cadastro, etapa ou responsável atualizado.", OccurredAt = DateTimeOffset.UtcNow, OperationKey = Guid.NewGuid().ToString("N") });
            db.Record(access, "contact.changed", id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(await ContactView(row, db));
        });
        app.MapGet(prefix + "/organizations", async (bool? paged, int? page, int? limit, string? search, AccessScope access, PlatformDb db) =>
        {
            var query = db.Organizations.Where(x => access.IsAdmin || x.Portfolio == access.Portfolio).AsNoTracking(); var term = Contract.Optional(search, 160, "Busca");
            if (term != "") query = query.Where(x => x.Name.Contains(term)); var index = Math.Clamp(page ?? 1, 1, 1000000); var size = Math.Clamp(limit ?? 25, 1, 100);
            var count = await query.CountAsync(); var items = await query.OrderBy(x => x.Name).ThenBy(x => x.Id).Skip(paged == true ? (index - 1) * size : 0).Take(paged == true ? size : 100).Select(x => new { x.Id, x.Name, x.ExternalKey, x.Portfolio, x.Version }).ToListAsync();
            return paged == true ? Results.Ok(new { items, total = count, page = index, limit = size }) : Results.Ok(items);
        });
        app.MapPost(prefix + "/organizations", async (OrganizationCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Required(command.ExternalKey, 100, "Chave externa");
            await using var tx = await db.Lock("organizations");
            var portfolio = access.IsAdmin ? Contract.Required(command.Portfolio ?? access.Portfolio, 60, "Carteira") : access.Portfolio;
            var name = Contract.Required(command.Name, 160, "Nome");
            var existing = await db.Organizations.SingleOrDefaultAsync(x => x.ExternalKey == key);
            if (existing != null) { if (existing.Name != name || existing.Portfolio != portfolio) throw new ApiFault(409, "organization_conflict", "Esta organização já foi cadastrada com outros dados."); return Results.Ok(new { existing.Id, existing.Name, existing.Portfolio, existing.Version }); }
            var row = new Organization { TenantId = access.TenantId, Name = name, ExternalKey = key, Portfolio = portfolio };
            db.Organizations.Add(row); db.Record(access, "organization.created", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(new { row.Id, row.Name, row.Portfolio, row.Version });
        });
        app.MapGet(prefix + "/contacts/{id:guid}/history", async (Guid id, bool? paged, int? page, int? limit, AccessScope access, PlatformDb db) =>
        {
            await db.Contact(id, access);
            var query = db.Interactions.Where(x => x.ContactId == id).AsNoTracking(); var index = Math.Clamp(page ?? 1, 1, 1000000); var size = Math.Clamp(limit ?? 25, 1, 100); var count = await query.CountAsync();
            var items = await query.OrderByDescending(x => x.OccurredAt).ThenByDescending(x => x.Id).Skip(paged == true ? (index - 1) * size : 0).Take(paged == true ? size : 100).Select(x => new { x.Id, x.Kind, x.Content, x.ActorId, x.OccurredAt, x.RecordedAt, x.Version }).ToListAsync();
            return paged == true ? Results.Ok(new { items, total = count, page = index, limit = size }) : Results.Ok(items);
        });
        app.MapPost(prefix + "/contacts/{id:guid}/history", async (Guid id, NoteCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); var content = Contract.Required(command.Content, 4000, "Nota", true);
            var occurred = command.OccurredAt ?? DateTimeOffset.UtcNow;
            if (occurred > DateTimeOffset.UtcNow.AddMinutes(5)) throw new ApiFault(400, "invalid_date", "A nota não pode estar no futuro.");
            var hash = Contract.Payload(command); await using var tx = await db.Lock("contact:" + id); await db.Contact(id, access);
            var existing = await db.Interactions.SingleOrDefaultAsync(x => x.ContactId == id && x.OperationKey == key);
            if (existing != null) { Contract.Replay(existing.PayloadHash, hash); return Results.Ok(new { existing.Id }); }
            var row = new Interaction { TenantId = access.TenantId, ContactId = id, ActorId = access.UserId, Content = content, OccurredAt = occurred, OperationKey = key, PayloadHash = hash };
            db.Interactions.Add(row); db.Record(access, "note.created", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(new { row.Id });
        });
        app.MapGet(prefix + "/tasks", async (Guid? contactId, Guid? ownerId, string? state, string? window, DateTimeOffset? dueFrom, DateTimeOffset? dueTo, bool? paged, int? page, int? limit, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            if (contactId != null) await db.Contact(contactId.Value, access);
            var contacts = db.VisibleContacts(access); var query = db.Tasks.AsNoTracking().Where(x => contacts.Any(c => c.Id == x.ContactId));
            if (contactId != null) query = query.Where(x => x.ContactId == contactId);
            if (ownerId != null) query = query.Where(x => x.OwnerId == ownerId);
            if (!string.IsNullOrEmpty(state)) query = query.Where(x => x.State == state);
            if (dueFrom != null) query = query.Where(x => x.DueAt >= dueFrom);
            if (dueTo != null) query = query.Where(x => x.DueAt < dueTo);
            var now = DateTimeOffset.UtcNow; var (today, tomorrow) = ConnectImprovements.Today(now);
            if (window == "late") query = query.Where(x => x.State == "open" && x.DueAt < now);
            else if (window == "today") query = query.Where(x => x.State == "open" && x.DueAt >= today && x.DueAt < tomorrow);
            else if (window == "week") query = query.Where(x => x.State == "open" && x.DueAt >= today && x.DueAt < today.AddDays(7));
            else if (!string.IsNullOrEmpty(window)) throw new ApiFault(400, "task_window", "Período inválido.");
            var count = await query.CountAsync(); http.Response.Headers["X-Total-Count"] = count.ToString(System.Globalization.CultureInfo.InvariantCulture);
            var index = Math.Clamp(page ?? 1, 1, 1000000); var size = Math.Clamp(limit ?? 25, 1, 100);
            var rows = await query.OrderBy(x => x.State == "open" ? 0 : 1).ThenBy(x => x.DueAt).ThenBy(x => x.Id).Skip(paged == true ? (index - 1) * size : 0).Take(paged == true ? size : 100).ToListAsync();
            return paged == true ? Results.Ok(new { items = rows.Select(TaskView), total = count, page = index, limit = size }) : Results.Ok(rows.Select(TaskView));
        });
        app.MapPost(prefix + "/contacts/{id:guid}/tasks", async (Guid id, TaskCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); var hash = Contract.Payload(command);
            await using var tx = await db.Lock("contact:" + id); var contact = await db.Contact(id, access);
            var existing = await db.Tasks.SingleOrDefaultAsync(x => x.ContactId == id && x.OperationKey == key);
            if (existing != null) { Contract.Replay(existing.PayloadHash, hash); return Results.Ok(TaskView(existing)); }
            var owner = command.OwnerId ?? contact.OwnerId; await db.Owner(owner, access, contact.Portfolio);
            if (command.DueAt < DateTimeOffset.UtcNow.AddYears(-1) || command.DueAt > DateTimeOffset.UtcNow.AddYears(5)) throw new ApiFault(400, "invalid_date", "Prazo fora do período permitido.");
            var row = new ContactTask { TenantId = access.TenantId, ContactId = id, OwnerId = owner, Title = Contract.Required(command.Title, 200, "Tarefa"), DueAt = command.DueAt, OperationKey = key, PayloadHash = hash };
            db.Tasks.Add(row); db.Record(access, "task.created", row.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(TaskView(row));
        });
        app.MapPost(prefix + "/tasks/{id:guid}/close", async (Guid id, CloseTaskCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); var hash = Contract.Payload(command);
            if (command.State is not ("done" or "cancelled")) throw new ApiFault(400, "invalid_state", "Escolha concluir ou cancelar.");
            await using var tx = await db.Lock("task:" + id);
            var task = await db.Tasks.SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound(); await db.Contact(task.ContactId, access);
            if (task.CloseKey == key) { Contract.Replay(task.CloseHash, hash); return Results.Ok(TaskView(task)); }
            Contract.Match(http.Request, task.Version);
            if (task.State != "open") throw new ApiFault(409, "task_closed", "Esta tarefa já foi encerrada.");
            task.State = command.State; task.Result = Contract.Required(command.Result, 2000, "Resultado ou motivo", true); task.ClosedAt = DateTimeOffset.UtcNow; task.CloseKey = key; task.CloseHash = hash;
            db.Interactions.Add(new Interaction { TenantId = access.TenantId, ContactId = task.ContactId, ActorId = access.UserId, Kind = "task", Content = $"{task.Title}: {task.Result}", OccurredAt = task.ClosedAt.Value, OperationKey = "task:" + id });
            db.Record(access, "task.closed", id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(TaskView(task));
        });
        app.MapPost(prefix + "/imports/preview", async (ImportCommand command, AccessScope access, PlatformDb db) =>
        {
            access.RequireWrite(); if (command.Rows == null || command.Rows.Length is < 1 or > 100) throw new ApiFault(400, "import_limit", "Envie de 1 a 100 contatos por lote.");
            var rows = command.Rows.Select(x => new ImportRow(Contract.Required(x.ExternalKey, 100, "Chave externa"), Contract.Required(x.Name, 160, "Nome"), Contract.Email(x.Email), Contract.Phone(x.Phone))).ToArray();
            if (rows.Select(x => x.ExternalKey).Distinct().Count() != rows.Length) throw new ApiFault(400, "import_duplicate", "O lote contém chaves externas repetidas.");
            var batch = new ImportBatch { TenantId = access.TenantId, UserId = access.UserId, Portfolio = access.Portfolio, Content = JsonSerializer.Serialize(rows), PayloadHash = Contract.Payload(rows), ExpiresAt = DateTimeOffset.UtcNow.AddHours(24) };
            db.Imports.Add(batch); await db.SaveChangesAsync(); return Results.Ok(new { batch.Id, batch.PayloadHash, batch.ExpiresAt, rows, count = rows.Length });
        });
        app.MapPost(prefix + "/imports/{id:guid}/confirm", async (Guid id, ConfirmImportCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireWrite(); var key = Contract.Idempotency(http.Request); await using var tx = await db.Lock("contacts");
            var batch = await db.Imports.SingleOrDefaultAsync(x => x.Id == id && x.UserId == access.UserId && x.Portfolio == access.Portfolio) ?? throw ApiFault.NotFound();
            Contract.Replay(batch.PayloadHash, command.PayloadHash);
            var prior = await db.Imports.SingleOrDefaultAsync(x => x.UserId == access.UserId && x.OperationKey == key);
            if (prior != null && prior.Id != id) throw new ApiFault(409, "idempotency_mismatch", "Chave usada em outro lote.");
            if (batch.State == "confirmed") { if (batch.OperationKey != key) throw new ApiFault(409, "import_confirmed", "Lote já confirmado."); return Results.Ok(JsonSerializer.Deserialize<JsonElement>(batch.ResultJson)); }
            if (batch.ExpiresAt <= DateTimeOffset.UtcNow) throw new ApiFault(409, "import_expired", "Preview expirado. Prepare o lote novamente.");
            var rows = JsonSerializer.Deserialize<ImportRow[]>(batch.Content)!; var result = new List<object>();
            foreach (var row in rows)
            {
                var existing = await db.Contacts.SingleOrDefaultAsync(x => x.ExternalKey == row.ExternalKey);
                if (existing != null && (existing.Portfolio != batch.Portfolio || existing.Name != row.Name || existing.Email != row.Email || existing.Phone != row.Phone)) throw new ApiFault(409, "import_changed", "Um contato mudou desde o preview. Revalide todo o lote.");
                if (existing == null)
                {
                    await db.Owner(access.UserId, access, batch.Portfolio);
                    existing = new Contact { TenantId = access.TenantId, Name = row.Name, ExternalKey = row.ExternalKey, Email = row.Email ?? "", Phone = row.Phone ?? "", Portfolio = batch.Portfolio, OwnerId = access.UserId, CreationHash = Contract.Payload(row) };
                    db.Contacts.Add(existing);
                }
                result.Add(new { externalKey = row.ExternalKey, contactId = existing.Id });
            }
            batch.State = "confirmed"; batch.OperationKey = key; batch.ResultJson = JsonSerializer.Serialize(result);
            db.Record(access, "import.confirmed", id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(result);
        });
        app.MapGet(prefix + "/imports/{id:guid}", async (Guid id, AccessScope access, PlatformDb db) =>
        {
            var batch = await db.Imports.AsNoTracking().SingleOrDefaultAsync(x => x.Id == id && x.UserId == access.UserId && x.Portfolio == access.Portfolio) ?? throw ApiFault.NotFound();
            return Results.Ok(new { batch.Id, batch.State, batch.PayloadHash, result = JsonSerializer.Deserialize<JsonElement>(batch.ResultJson) });
        });
        app.MapGet("/api/admin/audit", async (AccessScope access, PlatformDb db) =>
        {
            access.RequireAdmin(); return Results.Ok(await db.Audit.AsNoTracking().OrderByDescending(x => x.At).Take(100).Select(x => new { x.Id, x.ActorId, x.Action, x.ResourceId, x.TraceId, x.At }).ToListAsync());
        });
    }
}
