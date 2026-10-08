using System.Net.Sockets;
using System.Text;

namespace Ebt.Platform.Api;

public static class CommercialScanner
{
    public static async Task<bool> Scan(byte[] content, IConfiguration configuration)
    {
        if (!configuration.GetValue<bool>("Documents:ScannerEnabled")) return false;
        var host = configuration["Documents:ScannerHost"] ?? throw new ApiFault(503, "document_scanner_unavailable", "Scanner não configurado.");
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(15)); using var client = new TcpClient();
        try
        {
            await client.ConnectAsync(host, configuration.GetValue("Documents:ScannerPort", 3310), timeout.Token);
            await using var stream = client.GetStream(); await stream.WriteAsync("zINSTREAM\0"u8.ToArray(), timeout.Token);
            for (var offset = 0; offset < content.Length; offset += 65536)
            {
                var size = Math.Min(65536, content.Length - offset); var header = new byte[4]; System.Buffers.Binary.BinaryPrimitives.WriteInt32BigEndian(header, size);
                await stream.WriteAsync(header, timeout.Token); await stream.WriteAsync(content.AsMemory(offset, size), timeout.Token);
            }
            await stream.WriteAsync(new byte[4], timeout.Token); var reply = new List<byte>(); var next = new byte[1];
            while (reply.Count < 1024 && await stream.ReadAsync(next, timeout.Token) > 0 && next[0] != 0) reply.Add(next[0]);
            var result = Encoding.UTF8.GetString(reply.ToArray());
            if (result == "stream: OK") return true;
            if (result.EndsWith(" FOUND", StringComparison.Ordinal)) throw new ApiFault(400, "document_malware_blocked", "O arquivo foi bloqueado pela verificação de segurança.");
            throw new ApiFault(503, "document_scanner_unavailable", "A verificação de segurança não confirmou o arquivo.");
        }
        catch (Exception ex) when (ex is SocketException or IOException or OperationCanceledException) { throw new ApiFault(503, "document_scanner_unavailable", "A verificação de segurança está indisponível."); }
    }
}
