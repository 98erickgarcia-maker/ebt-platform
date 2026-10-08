using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

// Operator-only CLI. Never reachable through the public API or invoked at startup.
public static class Provisioning
{
    public static async Task ConfigureWazVox(PlatformDb db, AccessScope scope, IConfiguration config, HttpClient client)
    {
        scope.System = true;
        var tenant = Guid.Parse(config["Channel:TenantId"] ?? "");
        var operatorId = Guid.Parse(config["Channel:OperatorId"] ?? "");
        var portfolio = Contract.Required(config["Channel:Portfolio"], 100, "Carteira");
        var appKey = Contract.Required(config["Channel:AppKey"], 100, "Aplicativo");
        var secretRef = Contract.Required(config["Channel:SecretRef"], 100, "Referência de credencial");
        var workspace = WazVoxProtocol.Value(config, appKey, "WorkspaceId");
        if (string.IsNullOrWhiteSpace(workspace) || string.IsNullOrWhiteSpace(WazVoxProtocol.Value(config, appKey, "SigningSecret")) || string.IsNullOrWhiteSpace(config[$"WazVox:Connections:{secretRef}:ApiKey"]))
            throw new InvalidOperationException("Configure WazVox, aplicativo wz-, workspace, assinatura e credencial privada antes do canal.");
        var account = Contract.Required(config["Channel:AccountId"], 100, "Conta");
        var phone = Contract.Required(config["Channel:PhoneNumberId"], 100, "Número do canal");
        await WazVoxProtocol.VerifyAccount(client, config[$"WazVox:Connections:{secretRef}:ApiKey"]!, workspace, account, phone, CancellationToken.None);
        scope.TenantId = tenant;
        await using var tx = await db.Lock("global:channel-configuration");
        if (!await db.Tenants.AnyAsync(x => x.Id == tenant && x.Active)) throw new InvalidOperationException("Empresa inativa ou inexistente.");
        await db.Owner(operatorId, scope, portfolio);
        if (await db.Connections.IgnoreQueryFilters().AnyAsync(x => x.AppKey == appKey && x.AccountId == account && x.PhoneNumberId == phone)) throw new InvalidOperationException("Canal já cadastrado; preserve e revise a conexão existente.");
        var channel = new ChannelConnection { TenantId = tenant, OperatorId = operatorId, Portfolio = portfolio, Provider = "wazvox", AppKey = appKey, AccountId = account, PhoneNumberId = phone, SecretRef = secretRef, Name = Contract.Required(config["Channel:Name"], 120, "Nome do canal") };
        db.Connections.Add(channel); db.Audit.Add(new AuditEntry { TenantId = tenant, Action = "channel.configured", ResourceId = channel.Id, TraceId = "operator-cli" });
        await db.SaveChangesAsync(); await tx.CommitAsync(); Console.WriteLine("Canal WazVox cadastrado; homologação de webhook/envio ainda é necessária.");
    }
    public static async Task Bootstrap(PlatformDb db, AccessScope scope, IConfiguration config)
    {
        scope.System = true;
        var email = Contract.Email(config["Bootstrap:Email"]);
        if (email == "") throw new InvalidOperationException("Informe Bootstrap__Email.");
        var name = Contract.Required(config["Bootstrap:TenantName"], 120, "Empresa");
        var password = config["Bootstrap:Password"] ?? "";
        if (password.Length is < 12 or > 128 || !password.Any(char.IsLetter) || !password.Any(char.IsDigit)) throw new InvalidOperationException("Senha inicial deve conter 12-128 caracteres, letras e números.");
        await using var tx = await db.Lock("global:bootstrap");
        if (await db.Tenants.AnyAsync() || await db.Users.AnyAsync()) throw new InvalidOperationException("Bootstrap permite somente a primeira empresa em um schema vazio. Use convites depois.");
        var tenant = new Tenant { Name = name };
        var user = new PlatformUser { Email = email, Name = Contract.Required(config["Bootstrap:AdminName"], 120, "Administrador") };
        user.PasswordHash = new PasswordHasher<PlatformUser>().HashPassword(user, password);
        db.Tenants.Add(tenant); db.Users.Add(user);
        db.Memberships.Add(new Membership { TenantId = tenant.Id, UserId = user.Id, Role = "admin" });
        db.Audit.Add(new AuditEntry { TenantId = tenant.Id, ActorId = user.Id, Action = "platform.bootstrap", TraceId = "operator-cli" });
        await db.SaveChangesAsync(); await tx.CommitAsync();
        Console.WriteLine("Empresa e administrador inicial cadastrados. Nenhuma senha será exibida.");
    }

    public static async Task ConfigureMeta(PlatformDb db, AccessScope scope, IConfiguration config)
    {
        scope.System = true;
        var tenant = Guid.Parse(config["Channel:TenantId"] ?? "");
        var operatorId = Guid.Parse(config["Channel:OperatorId"] ?? "");
        var portfolio = Contract.Required(config["Channel:Portfolio"], 100, "Carteira");
        var appKey = Contract.Required(config["Channel:AppKey"], 100, "Aplicativo");
        var secretRef = Contract.Required(config["Channel:SecretRef"], 100, "Referência de credencial");
        if (!config.GetValue<bool>("Meta:Enabled") || MessagingEndpoints.AppValue(config, appKey, "AppSecret") == null || MessagingEndpoints.AppValue(config, appKey, "VerifyToken") == null || string.IsNullOrWhiteSpace(config[$"Meta:Connections:{secretRef}:AccessToken"]) || string.IsNullOrWhiteSpace(config["Meta:ApiVersion"]))
            throw new InvalidOperationException("Configure o aplicativo, versão e credenciais Meta antes do canal.");
        scope.TenantId = tenant;
        await using var tx = await db.Lock("global:channel-configuration");
        if (!await db.Tenants.AnyAsync(x => x.Id == tenant && x.Active)) throw new InvalidOperationException("Empresa inativa ou inexistente.");
        await db.Owner(operatorId, scope, portfolio);
        var account = Contract.Required(config["Channel:AccountId"], 100, "Conta");
        var phone = Contract.Required(config["Channel:PhoneNumberId"], 100, "Número do canal");
        if (await db.Connections.IgnoreQueryFilters().AnyAsync(x => x.AppKey == appKey && x.AccountId == account && x.PhoneNumberId == phone)) throw new InvalidOperationException("Canal já cadastrado. Revise a configuração existente antes de alterar.");
        var channel = new ChannelConnection { TenantId = tenant, OperatorId = operatorId, Portfolio = portfolio, Provider = "meta", AppKey = appKey, AccountId = account, PhoneNumberId = phone, SecretRef = secretRef, Name = Contract.Required(config["Channel:Name"], 120, "Nome do canal") };
        db.Connections.Add(channel); db.Audit.Add(new AuditEntry { TenantId = tenant, Action = "channel.configured", ResourceId = channel.Id, TraceId = "operator-cli" });
        await db.SaveChangesAsync(); await tx.CommitAsync(); Console.WriteLine("Canal cadastrado. Homologação externa ainda é necessária.");
    }
}
