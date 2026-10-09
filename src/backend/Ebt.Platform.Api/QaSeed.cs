using Microsoft.EntityFrameworkCore;
using System.Text.Json;

namespace Ebt.Platform.Api;

public static class QaSeed
{
    public static async Task Run(PlatformDb db, IConfiguration config)
    {
        if (await db.Tenants.AnyAsync()) { Console.WriteLine("Schema QA já inicializado; dados preservados."); return; }
        var password = config["Qa:Password"] ?? throw new InvalidOperationException("Configure senha sintética QA.");
        var a = new Tenant { Name = "EBT • demonstração A", Product = "connect" };
        var b = new Tenant { Name = "EBT • demonstração B", Product = "relacionamento" };
        db.Tenants.AddRange(a, b);
        var users = new Dictionary<string, PlatformUser>();
        foreach (var (email, name) in new[] { ("admin@ebt.example", "Administrador QA"), ("operador@ebt.example", "Atendimento QA"), ("consulta@ebt.example", "Consulta QA"), ("apoio@ebt.example", "Apoio técnico QA"), ("outra@ebt.example", "Outra carteira QA") })
        {
            var user = new PlatformUser { Email = email, Name = name }; user.PasswordHash = Security.Password(user, password); users[email] = user; db.Users.Add(user);
        }
        foreach (var tenant in new[] { a, b })
        {
            db.Memberships.Add(new Membership { TenantId = tenant.Id, UserId = users["admin@ebt.example"].Id, Role = "admin" });
            if (tenant.Id == a.Id)
                foreach (var (email, role, portfolio) in new[] { ("operador@ebt.example", "operator", "principal"), ("consulta@ebt.example", "reader", "principal"), ("apoio@ebt.example", "support", "principal"), ("outra@ebt.example", "operator", "outra") })
                    db.Memberships.Add(new Membership { TenantId = a.Id, UserId = users[email].Id, Role = role, Portfolio = portfolio });
            var owner = tenant.Id == a.Id ? users["operador@ebt.example"].Id : users["admin@ebt.example"].Id;
            var org = new Organization { TenantId = tenant.Id, Name = "Empresa Exemplo " + (tenant.Id == a.Id ? "A" : "B"), ExternalKey = "org-demo" };
            var contact = new Contact { TenantId = tenant.Id, Name = tenant.Id == a.Id ? "Contato Exemplo A" : "Contato Exemplo B", Email = "contato@cliente.example", Phone = "5511999990001", ExternalKey = "demo", OwnerId = owner, OrganizationId = org.Id, CreationHash = "seed" };
            db.Organizations.Add(org); db.Contacts.Add(contact);
            db.Tasks.Add(new ContactTask { TenantId = tenant.Id, ContactId = contact.Id, OwnerId = owner, Title = "Apresentar o EBT Connect", DueAt = DateTimeOffset.UtcNow.AddDays(1), OperationKey = "seed" });
            var channel = new ChannelConnection { TenantId = tenant.Id, Name = "Canal de teste local", Provider = "qa", AppKey = "qa-app", AccountId = "qa-account", PhoneNumberId = tenant.Id == a.Id ? "qa-phone-a" : "qa-phone-b", SecretRef = "qa", OperatorId = owner };
            db.Connections.Add(channel);
            db.Conversations.Add(new Conversation { TenantId = tenant.Id, ContactId = contact.Id, ConnectionId = channel.Id, Recipient = contact.Phone, LastInboundAt = DateTimeOffset.UtcNow });
        }
        await db.SaveChangesAsync();
        var path = config["Qa:AccessFile"] ?? throw new InvalidOperationException("Configure arquivo local de acesso QA.");
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        await File.WriteAllTextAsync(path, JsonSerializer.Serialize(new { password, tenantA = a.Id, tenantB = b.Id, users = users.ToDictionary(x => x.Key, x => x.Value.Id) }, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine("QA sintético inicializado; acesso salvo no arquivo local privado configurado.");
    }
}
