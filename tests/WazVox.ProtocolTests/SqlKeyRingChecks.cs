using Ebt.Platform.Api;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Xml.Linq;
using System.Text.Json;

public static class SqlKeyRingChecks
{
    public static void Run()
    {
        var database="EbtPlatformQa_KeyRing_"+Guid.NewGuid().ToString("N");
        using(var master=new Microsoft.Data.SqlClient.SqlConnection("Server=localhost;Database=master;Integrated Security=True;Encrypt=True;TrustServerCertificate=True"))
        {
            master.Open();using var create=master.CreateCommand();create.CommandText=$"CREATE DATABASE [{database}]";create.ExecuteNonQuery();
        }
        var connection=$"Server=localhost;Database={database};Integrated Security=True;Encrypt=True;TrustServerCertificate=True";
        using(var setup=new Microsoft.Data.SqlClient.SqlConnection(connection))
        {
            setup.Open();using var schema=setup.CreateCommand();schema.CommandText="CREATE SCHEMA ebt_connect";schema.ExecuteNonQuery();
            using var table=setup.CreateCommand();table.CommandText="CREATE TABLE ebt_connect.DataProtectionKeys (Id int IDENTITY PRIMARY KEY, FriendlyName nvarchar(max) NULL, Xml nvarchar(max) NULL)";table.ExecuteNonQuery();
        }
        using var rsa=RSA.Create(3072);
        var request=new CertificateRequest("CN=EBT synthetic keyring only",rsa,HashAlgorithmName.SHA256,RSASignaturePadding.Pkcs1);
        using var cert=request.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1),DateTimeOffset.UtcNow.AddYears(1));
        var password=Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
        var base64=Convert.ToBase64String(cert.Export(X509ContentType.Pfx,password));
        var testName="EBT.KeyRing.Qa."+Guid.NewGuid().ToString("N");
        ServiceProvider Create(string encodedCertificate,string pass)
        {
            var services=new ServiceCollection();services.AddLogging();services.AddScoped<AccessScope>();
            services.AddDbContext<PlatformDb>(o=>o.UseSqlServer(connection));
            var config=new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string,string?>{{"Platform:KeyStorage","sql"},{"Platform:KeyCertificateBase64",encodedCertificate},{"Platform:KeyCertificatePassword",pass}}).Build();
            KeyProtection.Configure(services,config,false).SetApplicationName(testName);
            return services.BuildServiceProvider();
        }
        using var first=Create(base64,password); var protector=first.GetRequiredService<IDataProtectionProvider>().CreateProtector(testName);var raw="QA encrypted envelope "+Guid.NewGuid();var protectedValue=protector.Protect(raw);
        using(var scope=first.CreateScope())
        {
            var db=scope.ServiceProvider.GetRequiredService<PlatformDb>();var keys=db.DataProtectionKeys.AsNoTracking().ToList();
            if(keys.Count==0||!keys.Any(k=>k.Xml!=null && XDocument.Parse(k.Xml).Descendants().Any(x=>x.Name.LocalName=="encryptedSecret")))throw new Exception("No encrypted persistent key");
        }
        using var second=Create(base64,password);
        if(second.GetRequiredService<IDataProtectionProvider>().CreateProtector(testName).Unprotect(protectedValue)!=raw)throw new Exception("New runtime cannot recover encrypted payload");
        using var otherRsa=RSA.Create(3072);var otherRequest=new CertificateRequest("CN=EBT wrong certificate",otherRsa,HashAlgorithmName.SHA256,RSASignaturePadding.Pkcs1);using var wrongCert=otherRequest.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1),DateTimeOffset.UtcNow.AddYears(1));
        using var wrong=Create(Convert.ToBase64String(wrongCert.Export(X509ContentType.Pfx,password)),password);
        try{wrong.GetRequiredService<IDataProtectionProvider>().CreateProtector(testName).Unprotect(protectedValue);throw new Exception("Wrong certificate decrypted payload");}catch(CryptographicException){}
        try{using var unavailable=Create("","");throw new Exception("SQL keyring accepted missing certificate");}catch(InvalidOperationException){}
        var report=new{generatedUtc=DateTimeOffset.UtcNow,environment="Synthetic localhost SQL keyring and independent runtimes",database,passed=true,cases=4,checks=new[]{"Persistent SQL key XML encrypted by certificate","New runtime recovers protected envelope","Wrong certificate cannot recover envelope","Missing certificate fails startup"}};
        File.WriteAllText("evidencias/testes_connect_sql_keyring.json",JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true}));Console.WriteLine("PASS 4 SQL keyring checks; no Azure changes.");
    }
}
