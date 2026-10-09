using Microsoft.AspNetCore.DataProtection;
using System.Security.Cryptography.X509Certificates;

namespace Ebt.Platform.Api;

public static class KeyProtection
{
    public static IDataProtectionBuilder Configure(IServiceCollection services, IConfiguration configuration, bool development)
    {
        var storage = configuration["Platform:KeyStorage"] ?? "files";
        if (storage is not ("files" or "sql")) throw new InvalidOperationException("KeyStorage inválido.");
        var encoded = configuration["Platform:KeyCertificateBase64"];
        var path = configuration["Platform:KeyCertificatePath"];
        X509Certificate2? certificate = null;
        if (!string.IsNullOrWhiteSpace(encoded))
            certificate = X509CertificateLoader.LoadPkcs12(Convert.FromBase64String(encoded), configuration["Platform:KeyCertificatePassword"], X509KeyStorageFlags.EphemeralKeySet);
        else if (!string.IsNullOrWhiteSpace(path))
            certificate = X509CertificateLoader.LoadPkcs12FromFile(path, configuration["Platform:KeyCertificatePassword"], X509KeyStorageFlags.EphemeralKeySet);
        if (certificate is not null && !certificate.HasPrivateKey) throw new InvalidOperationException("O certificado exige chave privada.");
        if (storage == "sql" && certificate is null) throw new InvalidOperationException("Keyring SQL exige certificado privado para cifrar as chaves persistidas.");
        var protection = services.AddDataProtection().SetApplicationName("Ebt.Platform.Connect.v1");
        if (storage == "sql") protection.PersistKeysToDbContext<PlatformDb>();
        else
        {
            var directory = configuration["Platform:KeyPath"] ?? throw new InvalidOperationException("Configure Platform__KeyPath para persistir as chaves.");
            Directory.CreateDirectory(directory);
            protection.PersistKeysToFileSystem(new DirectoryInfo(directory));
            if (certificate is null && OperatingSystem.IsWindows()) protection.ProtectKeysWithDpapi();
            else if (certificate is null && !development) throw new InvalidOperationException("Produção exige proteção explícita da chave persistente.");
        }
        if (certificate is not null) protection.ProtectKeysWithCertificate(certificate);
        return protection;
    }
}
