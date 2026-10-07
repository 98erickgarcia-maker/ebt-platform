namespace Ebt.Domain.Foundation;

public sealed record ConsumerUserProfile(
    Guid UserId,
    string DisplayName,
    string Role,
    bool IsActive);

public sealed record ConsumerProfile(
    Guid TenantId,
    string Key,
    string DisplayName,
    string BrandKey,
    IReadOnlyList<ConsumerUserProfile> Users);
