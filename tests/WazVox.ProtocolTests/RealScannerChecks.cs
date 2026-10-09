using Ebt.Platform.Api;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;
using System.Text;
using System.Text.Json;

static class RealScannerChecks
{
    public static async Task Run()
    {
        var configuration = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
        { ["Documents:ScannerEnabled"] = "true", ["Documents:ScannerHost"] = "127.0.0.1", ["Documents:ScannerPort"] = "3310" }).Build();
        using var deadline = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        using var engine = Process.Start(new ProcessStartInfo("clamd", "--version")
        { RedirectStandardOutput = true, UseShellExecute = false }) ?? throw new Exception("ClamAV binary unavailable");
        var version = (await engine.StandardOutput.ReadToEndAsync(deadline.Token)).Trim();
        await engine.WaitForExitAsync(deadline.Token);
        if (engine.ExitCode != 0) throw new Exception("ClamAV binary metadata unavailable");
        if (!version.StartsWith("ClamAV ", StringComparison.Ordinal)) throw new Exception("Real ClamAV version not confirmed");
        Console.WriteLine("Engine version: " + version);
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
