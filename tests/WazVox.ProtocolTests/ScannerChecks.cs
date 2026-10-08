using System.Net;
using System.Net.Sockets;
using System.Text;
using Ebt.Platform.Api;
using Microsoft.Extensions.Configuration;

static class ScannerChecks
{
    public static async Task Run()
    {
        await ExpectReply("stream: OK", false, "Unterminated scanner reply rejected");
        await ExpectReply("stream: OK\0", true, "Complete clean scanner reply accepted");
        await ExpectReply("stream: Synthetic-Test FOUND\0", false, "Malware verdict rejected");
        await ExpectReply("stream: ERROR\0", false, "Scanner failure rejected");
    }

    static async Task ExpectReply(string response, bool accepted, string name)
    {
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        var port = ((IPEndPoint)listener.LocalEndpoint).Port;
        var server = Task.Run(async () =>
        {
            using var peer = await listener.AcceptTcpClientAsync(timeout.Token);
            await using var stream = peer.GetStream();
            var command = new byte[10]; await stream.ReadExactlyAsync(command, timeout.Token);
            if (Encoding.ASCII.GetString(command) != "zINSTREAM\0") throw new Exception("Invalid scanner command");
            var header = new byte[4];
            while (true)
            {
                await stream.ReadExactlyAsync(header, timeout.Token);
                var length = System.Buffers.Binary.BinaryPrimitives.ReadInt32BigEndian(header);
                if (length == 0) break;
                if (length < 0 || length > 65536) throw new Exception("Invalid chunk length");
                var content = new byte[length]; await stream.ReadExactlyAsync(content, timeout.Token);
            }
            await stream.WriteAsync(Encoding.UTF8.GetBytes(response), timeout.Token);
        }, timeout.Token);
        var configuration = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?>
        { ["Documents:ScannerEnabled"] = "true", ["Documents:ScannerHost"] = "127.0.0.1", ["Documents:ScannerPort"] = port.ToString() }).Build();
        bool observed;
        try { observed = await CommercialScanner.Scan("synthetic QA"u8.ToArray(), configuration); }
        catch (ApiFault) { observed = false; }
        await server;
        if (observed != accepted) throw new Exception(name + " failed");
        Console.WriteLine("PASS " + name);
    }
}
