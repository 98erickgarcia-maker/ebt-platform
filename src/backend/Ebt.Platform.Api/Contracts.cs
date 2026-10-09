using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Ebt.Platform.Api;

public sealed class ApiFault(int status, string code, string message) : Exception(message)
{
    public int Status { get; } = status;
    public string Code { get; } = code;
    public static ApiFault NotFound() => new(404, "not_found", "Registro não encontrado neste contexto.");
}
public static class Contract
{
    public static readonly string[] Stages = ["novo", "contato", "proposta", "ganho", "encerrado"];
    public static string Required(string? value, int max, string label, bool multiline = false)
    {
        var result = value?.Trim() ?? "";
        if (result.Length == 0 || result.Length > max || result.Any(c => char.IsControl(c) && (!multiline || c is not '\n' and not '\r' and not '\t')))
            throw new ApiFault(400, "invalid_input", $"{label}: informe entre 1 e {max} caracteres.");
        return result;
    }
    public static string Optional(string? value, int max, string label, bool multiline = false) => string.IsNullOrWhiteSpace(value) ? "" : Required(value, max, label, multiline);
    public static string Hash(string value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
    public static string Payload(object value) => Hash(JsonSerializer.Serialize(value));
    public static string Token() => Convert.ToHexString(RandomNumberGenerator.GetBytes(32)).ToLowerInvariant();
    public static bool EqualsSecret(string value, string expected) => CryptographicOperations.FixedTimeEquals(SHA256.HashData(Encoding.UTF8.GetBytes(value)), SHA256.HashData(Encoding.UTF8.GetBytes(expected)));
    public static string Idempotency(HttpRequest request) => Required(request.Headers["Idempotency-Key"].ToString(), 100, "Idempotency-Key");
    public static void Match(HttpRequest request, long version)
    {
        var value = request.Headers.IfMatch.ToString();
        if (string.IsNullOrEmpty(value)) throw new ApiFault(428, "precondition_required", "Atualize o registro antes de confirmar.");
        if (value != $"\"{version}\"") throw new ApiFault(409, "stale_version", "Este registro foi alterado. Atualize e confira antes de confirmar.");
    }
    public static string Phone(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return "";
        if (value.Any(c => !char.IsAsciiDigit(c) && c is not '+' and not ' ' and not '(' and not ')' and not '-' and not '.')) throw new ApiFault(400, "invalid_phone", "Use apenas os dígitos do telefone com DDI e DDD.");
        var digits = new string(value.Where(char.IsAsciiDigit).ToArray());
        if (digits.Length is < 10 or > 15 || digits[0] == '0') throw new ApiFault(400, "invalid_phone", "Use telefone internacional com DDI e DDD.");
        return digits;
    }
    public static string Email(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return "";
        var email = Required(value, 254, "E-mail").ToLowerInvariant();
        if (!System.Net.Mail.MailAddress.TryCreate(email, out var parsed) || parsed.Address != email)
            throw new ApiFault(400, "invalid_email", "Informe um e-mail válido.");
        return email;
    }
    public static void Replay(string expected, string supplied) { if (expected != supplied) throw new ApiFault(409, "idempotency_mismatch", "Esta chave já foi usada com outro conteúdo."); }
}
public sealed record LoginCommand(string Email, string Password);
public sealed record AcceptInviteCommand(string Token, string Name, string Password);
public sealed record AcceptExistingInviteCommand(string Token);
public sealed record InviteCommand(string Email, string Role, string Portfolio);
public sealed record MembershipCommand(string Role, string Portfolio, bool Active);
public sealed record ContactCommand(string Name, string? Email, string? Phone, string? ExternalKey, Guid? OrganizationId, Guid? OwnerId, string? Portfolio, string? Stage, ProspectionCommand? Prospection = null);
public sealed record ProspectionCommand(string? Source = null, string? SourceUrl = null, string? Segment = null, string? ContactRole = null, string? Need = null, string? PreferredChannel = null, string? BestTime = null, string? DecisionMaker = null);
public sealed record OrganizationCommand(string Name, string ExternalKey, string? Portfolio);
public sealed record NoteCommand(string Content, DateTimeOffset? OccurredAt);
public sealed record TaskCommand(string Title, DateTimeOffset DueAt, Guid? OwnerId);
public sealed record CloseTaskCommand(string State, string Result);
public sealed record ImportRow(string ExternalKey, string Name, string? Email, string? Phone);
public sealed record ImportCommand(ImportRow[] Rows);
public sealed record ConfirmImportCommand(string PayloadHash);
public sealed record ReplyCommand(string Content, string ContentType = "text", Guid? ReplyToMessageId = null);
public sealed record ReviewCommand(string State, string? Reason = null);
