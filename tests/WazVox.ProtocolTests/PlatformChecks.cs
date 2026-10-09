using Ebt.Platform.Api;

static class PlatformChecks
{
    public static void Run()
    {
        var tenant = Guid.NewGuid();
        var admin = PlatformCapabilities.For(new AccessScope { TenantId = tenant, UserId = Guid.NewGuid(), Role = "admin" });
        if (admin.Platform != "EBT Platform" || admin.Product != "Connect" || admin.TenantId != tenant) throw new Exception("Platform/product identity boundary failed");
        if (admin.Modules.Select(m => m.Key).Distinct().Count() != admin.Modules.Count || admin.Modules.Any(m => m.Key is "sst" or "clinical" or "workflow" or "builder")) throw new Exception("Unimplemented or vertical capability advertised");
        var reader = PlatformCapabilities.For(new AccessScope { TenantId = tenant, UserId = Guid.NewGuid(), Role = "reader" });
        if (reader.Modules.Any(m => m.Access != "read") || reader.Modules.Any(m => m.Key == "administration")) throw new Exception("Reader permissions expanded");
        try { PlatformCapabilities.For(new AccessScope { Role = "support" }); throw new Exception("Support was granted commercial capabilities"); }
        catch (ApiFault fault) when (fault.Status == 401) { }
        Console.WriteLine("PASS Generic platform and product identity separated");
        Console.WriteLine("PASS Catalog includes actual capabilities only");
        Console.WriteLine("PASS Reader and support boundaries preserved");
        foreach (var state in new[] { "not_scanned", "unknown", "infected", "pending" })
            if (DocumentSafety.CanRelease(false, state)) throw new Exception("Unverified production document released");
        foreach (var state in new[] { "unknown", "infected", "pending" })
            if (DocumentSafety.CanRelease(true, state)) throw new Exception("Unsafe development document released");
        if (!DocumentSafety.CanRelease(false, "clean") || !DocumentSafety.CanRelease(true, "not_scanned")) throw new Exception("Document release policy failed");
        Console.WriteLine("PASS Unverified production document download blocked");
    }
}
