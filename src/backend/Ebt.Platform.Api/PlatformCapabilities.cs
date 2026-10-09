namespace Ebt.Platform.Api;

public sealed record PlatformModule(string Key, string Name, string Access);
public sealed record PlatformCapabilityView(string Platform, string Product, Guid TenantId, IReadOnlyList<PlatformModule> Modules);

public static class PlatformCapabilities
{
    // This is the catalog of this implemented slice, not a promise of the complete Core.
    public static PlatformCapabilityView For(AccessScope access)
    {
        if (!access.CanRead || access.UserId == Guid.Empty || access.TenantId == Guid.Empty)
            throw new ApiFault(401, "authentication_required", "Entre novamente para continuar.");
        var action = access.CanWrite ? "write" : "read";
        var modules = new List<PlatformModule>
        {
            new("people", "Contatos e organizações", action),
            new("history", "Histórico e próxima ação", action),
            new("tasks", "Tarefas", action),
            new("documents", "Documentos privados", action),
            new("communications", "Conversas", action),
        };
        if (access.IsAdmin) modules.Add(new("administration", "Acesso, auditoria e integrações", "admin"));
        return new("EBT Platform", "Connect", access.TenantId, modules);
    }

    public static void Map(WebApplication app) => app.MapGet("/api/platform/v1/capabilities", (AccessScope access) => Results.Ok(For(access)));
}
