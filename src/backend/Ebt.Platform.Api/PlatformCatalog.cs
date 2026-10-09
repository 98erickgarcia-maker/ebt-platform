using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public sealed class PlatformApplication
{
    public string Code { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public string State { get; set; } = "";
    public string? DataSchema { get; set; }
    public int SortOrder { get; set; }
}

public static class PlatformCatalog
{
    public static Task<List<PlatformApplication>> Read(PlatformDb db, CancellationToken ct = default) =>
        db.Database.SqlQueryRaw<PlatformApplication>(
            "SELECT Code,Name,Description,State,DataSchema,SortOrder FROM ebt_platform.Applications ORDER BY SortOrder,Code").ToListAsync(ct);

    public static void Map(WebApplication app)
    {
        app.MapGet("/api/platform/v1/applications", async (AccessScope access, PlatformDb db, HttpContext http) =>
        {
            // Existing active session/membership is mandatory; API keys remain Connect-only.
            if (!access.CanRead) throw new ApiFault(401, "authentication_required", "Entre novamente para continuar.");
            var rows = await Read(db, http.RequestAborted);
            return Results.Ok(new { family = "EBT Enterprise", platform = "EBT Platform", tenantId = access.TenantId,
                applications = rows.Select(x => new { x.Code, x.Name, x.Description,
                    state = x.State == "available" && x.Code != "connect" ? "planned" : x.State,
                    available = x.Code == "connect" && x.State == "available" }) });
        });
    }
}
