using Ebt.Platform.Api;
using Microsoft.Extensions.Configuration;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;

static class RealScannerChecks
{
    public static async Task Run()
    {
        var configuration = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
        { ["Documents:ScannerEnabled"] = "true", ["Documents:ScannerHost"] = "127.0.0.1", ["Documents:ScannerPort"] = "3310" }).Build();
        using var deadline = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        using var client = new TcpClient();
        await client.ConnectAsync("127.0.0.1", 3310, deadline.Token);
        await using var stream = client.GetStream();
        await stream.WriteAsync("zVERSION\0"u8.ToArray(), deadline.Token);
        var reply = new byte[512]; var length = await stream.ReadAsync(reply, deadline.Token);
        var version = Encoding.UTF8.GetString(reply, 0, length).TrimEnd('\0', '\n');
        if (!version.StartsWith("ClamAV ", StringComparison.Ordinal)) throw new Exception("Real ClamAV version not confirmed");
        if (!await CommercialScanner.Scan("Synthetic safe text."u8.ToArray(), configuration)) throw new Exception("Real engine did not confirm clean input");
        Console.WriteLine("PASS Real ClamAV clean stream confirmed");
        // Harmless standard antivirus test signature, assembled only in memory.
        var signature = "X5O!P%@AP[4\\PZX54(P^)7CC)7}" + "$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*";
        try { await CommercialScanner.Scan(Encoding.ASCII.GetBytes(signature), configuration); throw new Exception("Real engine accepted EICAR"); }
        catch (ApiFault fault) when (fault.Status == 400 && fault.Code == "document_malware_blocked")
        { Console.WriteLine("PASS Real ClamAV EICAR stream blocked"); }
        Directory.CreateDirectory("evidencias");
        await File.WriteAllTextAsync("evidencias/testes_scanner_real_ci.json", JsonSerializer.Serialize(new
        { generatedUtc = DateTimeOffset.UtcNow, environment = "isolated CI loopback; official ClamAV signatures", engine = version,
          passed = true, cases = 2, cleanAccepted = true, eicarBlocked = true, productionScannerConfigured = false }, new JsonSerializerOptions { WriteIndented = true }));
    }
}
