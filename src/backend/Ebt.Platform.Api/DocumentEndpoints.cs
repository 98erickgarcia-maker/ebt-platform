using System.Security.Cryptography;
using System.Text;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public static class DocumentEndpoints
{
    public static object View(CommercialDocument doc) => new { doc.Id, doc.ContactId, doc.TaskId, doc.Title, doc.CurrentVersion, doc.ReviewState, doc.Version };
    static async Task<CommercialDocument> Visible(Guid id, AccessScope access, PlatformDb db)
    {
        var doc = await db.Documents.SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound(); await db.Contact(doc.ContactId, access); return doc;
    }
    public static void Map(WebApplication app)
    {
        const string prefix = "/api/connect/v1";
        app.MapGet(prefix + "/documents", async (Guid? contactId, AccessScope access, PlatformDb db) =>
        {
            if (contactId != null) await db.Contact(contactId.Value, access);
            var contacts = db.VisibleContacts(access);
            var docs = await db.Documents.AsNoTracking().Where(x => contacts.Any(c => c.Id == x.ContactId) && (contactId == null || x.ContactId == contactId)).OrderBy(x => x.Title).Take(100).ToListAsync();
            return Results.Ok(docs.Select(View));
        });
        app.MapGet(prefix + "/documents/{id:guid}/versions", async (Guid id, AccessScope access, PlatformDb db) =>
        {
            await Visible(id, access, db);
            return Results.Ok(await db.DocumentVersions.Where(x => x.DocumentId == id).AsNoTracking().OrderByDescending(x => x.Number).Select(x => new { x.Id, x.Number, x.FileName, x.MediaType, x.Sha256, size = x.Content.Length, x.ActorId, x.CreatedAt, x.ReviewState, x.ReviewReason, x.ReviewedBy, x.ReviewedAt, x.ScanState }).ToListAsync());
        });
        app.MapPost(prefix + "/contacts/{contactId:guid}/documents", async (Guid contactId, AccessScope access, PlatformDb db, HttpContext http) => await Upload(contactId, null, access, db, http));
        app.MapPost(prefix + "/documents/{id:guid}/versions", async (Guid id, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            var doc = await Visible(id, access, db); return await Upload(doc.ContactId, doc.Id, access, db, http);
        });
        app.MapPost(prefix + "/documents/{id:guid}/review", async (Guid id, ReviewCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireAdmin(); if (command.State is not ("approved" or "rejected")) throw new ApiFault(400, "invalid_review", "Escolha aprovar ou rejeitar.");
            await using var tx = await db.Lock("global:document-storage"); var doc = await Visible(id, access, db); Contract.Match(http.Request, doc.Version);
            var version = await db.DocumentVersions.SingleAsync(x => x.DocumentId == id && x.Number == doc.CurrentVersion);
            if (command.State == "approved") DocumentSafety.RequireRelease(app.Environment.IsDevelopment(), version.ScanState);
            version.ReviewState = command.State; version.ReviewReason = command.State == "rejected" ? Contract.Required(command.Reason, 2000, "Motivo da rejeição", true) : Contract.Optional(command.Reason, 2000, "Motivo", true);
            version.ReviewedBy = access.UserId; version.ReviewedAt = DateTimeOffset.UtcNow;
            doc.ReviewState = command.State; db.Record(access, "document." + command.State, id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(View(doc));
        });
        app.MapGet(prefix + "/documents/{id:guid}/download/{number:int}", async (Guid id, int number, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            var doc = await Visible(id, access, db);
            var version = await db.DocumentVersions.AsNoTracking().SingleOrDefaultAsync(x => x.DocumentId == id && x.Number == number) ?? throw ApiFault.NotFound();
            if (version.ReviewState != "approved" && !access.CanWrite) throw new ApiFault(403, "document_not_approved", "Esta versão aguarda revisão.");
            DocumentSafety.RequireRelease(app.Environment.IsDevelopment(), version.ScanState);
            if (Convert.ToHexString(SHA256.HashData(version.Content)).ToLowerInvariant() != version.Sha256) throw new ApiFault(503, "document_integrity", "A integridade do arquivo precisa de conferência.");
            db.Record(access, "document.downloaded", id, http.TraceIdentifier); await db.SaveChangesAsync();
            return Results.File(version.Content, version.MediaType, version.FileName, enableRangeProcessing: false);
        });
    }
    static async Task<IResult> Upload(Guid contactId, Guid? documentId, AccessScope access, PlatformDb db, HttpContext http)
    {
        access.RequireWrite(); var key = Contract.Idempotency(http.Request); await db.Contact(contactId, access);
        if (!http.Request.HasFormContentType) throw new ApiFault(400, "invalid_upload", "Use um formulário com arquivo.");
        var form = await http.Request.ReadFormAsync();
        if (form.Files.Count != 1) throw new ApiFault(400, "invalid_upload", "Selecione um arquivo por versão.");
        var file = form.Files[0];
        if (file.Length is < 1 or > 2_097_152) throw new ApiFault(400, "document_size", "O arquivo deve ter até 2 MiB.");
        if (file.FileName.Contains('/') || file.FileName.Contains('\\') || file.FileName.Contains("..", StringComparison.Ordinal)) throw new ApiFault(400, "invalid_filename", "O nome do arquivo não pode conter caminho.");
        var name = file.FileName;
        name = Contract.Required(name, 180, "Nome do arquivo");
        await using var memory = new MemoryStream(); await file.CopyToAsync(memory); var bytes = memory.ToArray();
        var media = "";
        if (Path.GetExtension(name).Equals(".pdf", StringComparison.OrdinalIgnoreCase) && bytes.AsSpan().StartsWith("%PDF-"u8)) media = "application/pdf";
        else if (Path.GetExtension(name).Equals(".txt", StringComparison.OrdinalIgnoreCase))
        {
            try { var text = new UTF8Encoding(false, true).GetString(bytes); if (text.Contains('\0')) throw new DecoderFallbackException(); media = "text/plain"; }
            catch (DecoderFallbackException) { throw new ApiFault(400, "document_type", "O texto deve ser UTF-8 válido."); }
        }
        if (media == "") throw new ApiFault(400, "document_type", "Envie PDF ou texto UTF-8.");
        var scanned = await CommercialScanner.Scan(bytes, http.RequestServices.GetRequiredService<IConfiguration>(), http.RequestAborted);
        var title = Contract.Required(form["title"].ToString(), 200, "Título");
        Guid? taskId = null; if (!string.IsNullOrEmpty(form["taskId"])) { if (!Guid.TryParse(form["taskId"], out var task)) throw new ApiFault(400, "invalid_task", "Tarefa inválida."); taskId = task; }
        var sha = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant(); var hash = Contract.Payload(new { title, taskId, name, sha });
        await using var tx = await db.Lock("global:document-storage");
        await db.Contact(contactId, access);
        if (taskId != null && !await db.Tasks.AnyAsync(x => x.Id == taskId && x.ContactId == contactId)) throw new ApiFault(400, "invalid_task", "O documento deve estar ligado a uma tarefa deste contato.");
        CommercialDocument doc;
        if (documentId == null)
        {
            var existing = await db.Documents.SingleOrDefaultAsync(x => x.ContactId == contactId && x.CreationKey == key);
            if (existing != null) { Contract.Replay(existing.CreationHash, hash); return Results.Ok(View(existing)); }
            doc = new CommercialDocument { TenantId = access.TenantId, ContactId = contactId, TaskId = taskId, Title = title, CreationKey = key, CreationHash = hash };
            db.Documents.Add(doc);
        }
        else
        {
            doc = await Visible(documentId.Value, access, db);
            var previous = await db.DocumentVersions.SingleOrDefaultAsync(x => x.DocumentId == doc.Id && x.OperationKey == key);
            if (previous != null) { Contract.Replay(previous.PayloadHash, hash); return Results.Ok(View(doc)); }
            Contract.Match(http.Request, doc.Version);
            doc.Title = title; doc.TaskId = taskId;
        }
        var own = await db.DocumentVersions.SumAsync(x => (long)x.Content.Length);
        var all = await db.GlobalDocumentBytes();
        if (own + bytes.Length > 20 * 1024 * 1024 || all + bytes.Length > 100 * 1024 * 1024) throw new ApiFault(409, "document_quota", "Capacidade documental do piloto atingida.");
        doc.CurrentVersion++; doc.ReviewState = "pending";
        db.DocumentVersions.Add(new DocumentVersion { TenantId = access.TenantId, DocumentId = doc.Id, Number = doc.CurrentVersion, Content = bytes, FileName = name, MediaType = media, Sha256 = sha, ActorId = access.UserId, OperationKey = key, PayloadHash = hash, ScanState = scanned ? "clean" : "not_scanned" });
        db.Record(access, "document.version_created", doc.Id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(View(doc));
    }
}
