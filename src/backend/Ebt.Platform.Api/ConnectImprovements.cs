using Microsoft.EntityFrameworkCore;
using System.Text;

namespace Ebt.Platform.Api;
public static class ConnectImprovements
{
    public static string CalendarText(string value) => value.Replace("\\", "\\\\").Replace("\r\n", "\n").Replace("\r", "\n").Replace("\n", "\\n").Replace(";", "\\;").Replace(",", "\\,");
    public static (DateTimeOffset Start, DateTimeOffset End) Today(DateTimeOffset now)
    {
        var zone = TimeZoneInfo.FindSystemTimeZoneById("America/Sao_Paulo"); var date = TimeZoneInfo.ConvertTime(now, zone).Date;
        return (new DateTimeOffset(date, zone.GetUtcOffset(date)), new DateTimeOffset(date.AddDays(1), zone.GetUtcOffset(date.AddDays(1))));
    }
    public static void Map(WebApplication app)
    {
        const string p = "/api/connect/v1";
        app.MapGet(p + "/search", async (string? search, PlatformDb db, AccessScope access) =>
        {
            var text = Contract.Optional(search, 160, "Busca"); if (text.Length < 2) return Results.Ok(Array.Empty<object>());
            var visible = db.VisibleContacts(access); var results = new List<object>();
            results.AddRange(await visible.AsNoTracking().Where(x => x.Name.Contains(text) || x.Email.Contains(text) || x.Phone.Contains(text) || db.Organizations.Any(o => o.Id == x.OrganizationId && o.Name.Contains(text) && o.Portfolio == x.Portfolio)).OrderBy(x => x.Name).ThenBy(x => x.Id).Take(10).Select(x => new { kind = "contact", id = x.Id, contactId = x.Id, title = x.Name, context = x.Email }).ToListAsync());
            results.AddRange(await db.Tasks.AsNoTracking().Where(x => x.Title.Contains(text) && visible.Any(c => c.Id == x.ContactId)).OrderBy(x => x.DueAt).ThenBy(x => x.Id).Take(5).Select(x => new { kind = "task", id = x.Id, contactId = x.ContactId, title = x.Title, context = x.State }).ToListAsync());
            results.AddRange(await db.Documents.AsNoTracking().Where(x => x.Title.Contains(text) && visible.Any(c => c.Id == x.ContactId)).OrderBy(x => x.Title).ThenBy(x => x.Id).Take(5).Select(x => new { kind = "document", id = x.Id, contactId = x.ContactId, title = x.Title, context = x.ReviewState }).ToListAsync());
            return Results.Ok(results);
        });
        app.MapGet(p + "/contacts/duplicates", async (string? email, string? phone, Guid? exclude, PlatformDb db, AccessScope access) =>
        {
            var address = Contract.Email(email); var number = Contract.Phone(phone);
            return Results.Ok(await db.VisibleContacts(access).AsNoTracking().Where(x => x.Id != exclude && ((address != "" && x.Email == address) || (number != "" && x.Phone == number))).OrderBy(x => x.Name).ThenBy(x => x.Id).Take(5).Select(x => new { x.Id, x.Name }).ToListAsync());
        });
        app.MapGet(p + "/tasks/{id:guid}/calendar.ics", async (Guid id, PlatformDb db, AccessScope access, HttpContext http) =>
        {
            var row = await db.Tasks.SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound(); await db.Contact(row.ContactId, access);
            if (row.State != "open") throw new ApiFault(409, "task_closed", "Exporte um compromisso em aberto.");
            var content = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//EBT Enterprise//Connect//PT-BR\r\nBEGIN:VEVENT\r\nUID:" + row.Id.ToString("N") + "@ebt-connect\r\nDTSTAMP:" + DateTimeOffset.UtcNow.ToString("yyyyMMdd'T'HHmmss'Z'") + "\r\nDTSTART:" + row.DueAt.UtcDateTime.ToString("yyyyMMdd'T'HHmmss'Z'") + "\r\nSUMMARY:" + CalendarText(row.Title) + "\r\nDESCRIPTION:" + CalendarText("Compromisso EBT Connect. Referência: " + row.Id) + "\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n";
            db.Record(access, "task.calendar_exported", row.Id, http.TraceIdentifier); await db.SaveChangesAsync();
            return Results.File(Encoding.UTF8.GetBytes(content), "text/calendar; charset=utf-8", "compromisso-" + id + ".ics");
        });
    }
}
