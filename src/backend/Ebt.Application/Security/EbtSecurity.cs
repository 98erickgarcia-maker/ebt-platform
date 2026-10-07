using System.Security.Claims;

namespace Ebt.Application.Security;

public enum EbtRole
{
    Administrator = 1,
    Operator = 2,
    ReadOnly = 3,
    TechnicalSupport = 4
}

public enum EbtPermission
{
    FoundationRecordRead = 1,
    FoundationRecordWrite = 2,
    FoundationAttachmentDownload = 3
}

public static class EbtAccessMatrix
{
    public static bool Allows(EbtRole role, EbtPermission permission) => role switch
    {
        EbtRole.Administrator => true,
        EbtRole.Operator => true,
        EbtRole.ReadOnly => permission is EbtPermission.FoundationRecordRead
            or EbtPermission.FoundationAttachmentDownload,
        EbtRole.TechnicalSupport => false,
        _ => false
    };
}

public sealed record EbtIdentityProfile(
    Guid UserId,
    Guid? TenantId,
    string? TenantKey,
    string Email,
    string DisplayName,
    EbtRole Role,
    bool IsActive);

public interface IEbtIdentityCatalog
{
    EbtIdentityProfile? FindByEmail(string email);
    EbtIdentityProfile? FindByUserId(Guid userId);
}

public interface IEbtTenantContext
{
    EbtIdentityProfile? Current { get; }
}

public static class EbtSessionClaims
{
    public const string ExpiresAtUnix = "ebt:session:exp";

    public static bool IsSessionCurrent(ClaimsPrincipal principal, TimeProvider clock)
    {
        var raw = principal.FindFirst(ExpiresAtUnix)?.Value;
        return long.TryParse(raw, out var expiresAt)
            && clock.GetUtcNow() < DateTimeOffset.FromUnixTimeSeconds(expiresAt);
    }
}
