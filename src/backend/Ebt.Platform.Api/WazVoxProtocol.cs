using System.Globalization;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Ebt.Platform.Api;

// WazVox v1 canonical events are distinct from raw Meta envelopes.
public static class WazVoxProtocol
{
    public static string Text(JsonElement e, string key) => e.ValueKind == JsonValueKind.Object && e.TryGetProperty(key, out var p) && p.ValueKind == JsonValueKind.String ? p.GetString() ?? "" : "";
    public static bool Verify(byte[] body, string timestamp, string signature, string secret, DateTimeOffset now)
    {
        if (timestamp.Length is < 1 or > 12 || !timestamp.All(char.IsAsciiDigit) || !long.TryParse(timestamp, out var seconds) || Math.Abs(now.ToUnixTimeSeconds() - seconds) > 300) return false;
        byte[] supplied;
        try { supplied = signature.StartsWith("sha256=", StringComparison.Ordinal) ? Convert.FromHexString(signature[7..]) : []; } catch (FormatException) { return false; }
        var prefix = Encoding.UTF8.GetBytes(timestamp + ".");
        var signed = new byte[prefix.Length + body.Length]; prefix.CopyTo(signed, 0); body.CopyTo(signed, prefix.Length);
        return supplied.Length == 32 && CryptographicOperations.FixedTimeEquals(supplied, HMACSHA256.HashData(Encoding.UTF8.GetBytes(secret), signed));
    }
    public static string ValidateEnvelope(byte[] body, string headerEventId, string expectedWorkspace)
    {
        using var p = JsonDocument.Parse(body, new JsonDocumentOptions { MaxDepth = 48 }); var e = p.RootElement;
        var id = Text(e, "eventId");
        if (id.Length is < 1 or > 200 || headerEventId != id || Text(e, "version") != "1" || string.IsNullOrWhiteSpace(expectedWorkspace) || Text(e, "tenantId") != expectedWorkspace)
            throw new ApiFault(400, "invalid_wazvox_envelope", "Evento incompatível com a integração configurada.");
        return id;
    }
    public static JsonDocument Normalize(JsonElement e)
    {
        var account = Contract.Required(Text(e, "wabaId"), 100, "Conta do evento");
        var phone = Contract.Required(Text(e, "phoneNumberId"), 100, "Número do evento");
        if (!DateTimeOffset.TryParse(Text(e, "occurredAt"), CultureInfo.InvariantCulture, DateTimeStyles.None, out var at) || at > DateTimeOffset.UtcNow.AddMinutes(5) || at < DateTimeOffset.UnixEpoch || !e.TryGetProperty("data", out var data) || data.ValueKind != JsonValueKind.Object)
            throw new ApiFault(400, "invalid_wazvox_event", "Evento sem conteúdo ou instante válido.");
        object[] messages = []; object[] statuses = [];
        var stamp = at.ToUnixTimeSeconds().ToString(CultureInfo.InvariantCulture);
        switch (Text(e, "type"))
        {
            case "message.received":
                if (!data.TryGetProperty("message", out var m) || Text(m, "type") != "text" || !m.TryGetProperty("text", out var text)) throw new ApiFault(400, "unsupported_message", "O recorte aceita mensagens de texto.");
                messages = [new { id = Text(m, "id"), from = Text(data, "from"), type = "text", timestamp = stamp, text = new { body = Text(text, "body") } }];
                break;
            case "message.status":
                // Live callbacks use data.id for the wamid; API replies use waMessageId.
                // An internal WazVox UUID is never a valid fallback WhatsApp reference.
                var canonicalReference = Text(data, "waMessageId");
                var callbackReference = Text(data, "id");
                var callbackIsWhatsApp = callbackReference.StartsWith("wamid.", StringComparison.Ordinal) && callbackReference.Length > 6;
                if (canonicalReference.Length > 0 && callbackIsWhatsApp && canonicalReference != callbackReference)
                    throw new ApiFault(400, "provider_reference_conflict", "Referências WhatsApp divergentes.");
                var reference = Contract.Required(canonicalReference.Length > 0 ? canonicalReference : callbackIsWhatsApp ? callbackReference : "", 250, "Referência WhatsApp");
                var state = Text(data, "status");
                if (state is not ("sent" or "delivered" or "read" or "failed")) throw new ApiFault(400, "unsupported_status", "Status não suportado.");
                var recipient = Text(data, "to");
                if (recipient.Length == 0) recipient = Text(data, "recipient_id");
                statuses = [new { id = reference, status = state, timestamp = stamp, recipient_id = recipient }];
                break;
            default: throw new ApiFault(400, "unsupported_wazvox_event", "Evento fora do recorte de mensagens.");
        }
        return JsonDocument.Parse(JsonSerializer.SerializeToUtf8Bytes(new { @object = "whatsapp_business_account", entry = new[] { new { id = account, changes = new[] { new { field = "messages", value = new { metadata = new { phone_number_id = phone }, messages, statuses } } } } } }));
    }
    public static async Task<(string State, string Reference)> Send(HttpClient client, string apiKey, string phone, string recipient, string content, Guid operationId, CancellationToken ct)
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, "messages");
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);
        request.Headers.Add("Idempotency-Key", "ebt-connect-" + operationId.ToString("N"));
        request.Content = JsonContent.Create(new { phoneNumberId = phone, to = recipient, type = "text", text = content });
        using var response = await client.SendAsync(request, ct);
        if (!response.IsSuccessStatusCode) return ("unknown", "");
        using var result = JsonDocument.Parse(await response.Content.ReadAsByteArrayAsync(ct));
        var reference = Text(result.RootElement, "waMessageId");
        return Text(result.RootElement, "status") == "accepted" && reference.Length is > 0 and <= 250 ? ("accepted", reference) : ("unknown", "");
    }
    public static string? Value(IConfiguration config, string appKey, string field) => config.GetValue<bool>("WazVox:Enabled") && appKey.StartsWith("wz-", StringComparison.Ordinal) && appKey.Length is > 3 and <= 100 && appKey.All(c => char.IsAsciiLetterOrDigit(c) || c == '-') ? config[$"WazVox:Apps:{appKey}:{field}"] : null;
    public static async Task VerifyAccount(HttpClient client, string apiKey, string workspace, string account, string phone, CancellationToken ct)
    {
        async Task<JsonDocument> Read(string path)
        {
            using var request = new HttpRequestMessage(HttpMethod.Get, path);
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);
            using var response = await client.SendAsync(request, ct);
            if (!response.IsSuccessStatusCode) throw new InvalidOperationException("WazVox recusou a verificação da conta; nenhum canal será cadastrado.");
            return JsonDocument.Parse(await response.Content.ReadAsByteArrayAsync(ct));
        }
        using var me = await Read("me"); using var numbers = await Read("numbers");
        if (!me.RootElement.TryGetProperty("data", out var owner) || Text(owner,"tenantId") != workspace || !numbers.RootElement.TryGetProperty("data", out var rows) || rows.ValueKind != JsonValueKind.Array || !rows.EnumerateArray().Any(x => Text(x,"phoneNumberId") == phone && Text(x,"wabaId") == account && Text(x,"connectionStatus") == "connected" && x.TryGetProperty("registered",out var registered) && registered.ValueKind == JsonValueKind.True))
            throw new InvalidOperationException("Workspace, conta ou número WazVox divergem ou estão desconectados; nenhum canal será cadastrado.");
    }
}
