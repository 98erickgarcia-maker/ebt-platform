using Ebt.Platform.Api;
using Microsoft.Extensions.Configuration;
using System.Text;

static class RealScannerChecks
{
    public static async Task Run()
    {
        var configuration = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
        { ["Documents:ScannerEnabled"] = "true", ["Documents:ScannerHost"] = "127.0.0.1", ["Documents:ScannerPort"] = "3310" }).Build();
        if (!await CommercialScanner.Scan("Synthetic safe text."u8.ToArray(), configuration)) throw new Exception("Real engine did not confirm clean input");
        Console.WriteLine("PASS Real ClamAV clean stream confirmed");
        // Standard harmless antivirus test signature, assembled in memory only.
        var signature = "X5O!P%@AP[4\\PZX54(P^)7CC)7}" + "$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*";
        try { await CommercialScanner.Scan(Encoding.ASCII.GetBytes(signature), configuration); throw new Exception("Real engine accepted EICAR"); }
        catch (ApiFault fault) when (fault.Status == 400 && fault.Code == "document_malware_blocked")
        { Console.WriteLine("PASS Real ClamAV EICAR stream blocked"); }
    }
}
