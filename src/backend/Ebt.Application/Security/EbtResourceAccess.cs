using Ebt.Domain.Foundation;

namespace Ebt.Application.Security;

public static class EbtResourceAccess
{
    public static bool CanRead(EbtIdentityProfile identity, FoundationStoredRecord record) =>
        identity.IsActive && identity.TenantId is not null
        && identity.TenantKey == record.TenantKey
        && EbtAccessMatrix.Allows(identity.Role, EbtPermission.FoundationRecordRead)
        && (identity.Role != EbtRole.Operator || record.OwnerUserId == identity.UserId);

    public static bool HasTenantAccess(EbtIdentityProfile identity, EbtPermission permission) =>
        identity.IsActive && identity.TenantId is not null
        && !string.IsNullOrWhiteSpace(identity.TenantKey)
        && EbtAccessMatrix.Allows(identity.Role, permission);
}
