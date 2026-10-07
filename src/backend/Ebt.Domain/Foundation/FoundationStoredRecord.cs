namespace Ebt.Domain.Foundation;

public sealed record FoundationAttachmentMetadata(
    string BlobName,
    string FileName,
    string ContentType,
    long Length);

public sealed record FoundationStoredRecord(
    Guid Id,
    string TenantKey,
    string Title,
    FoundationAttachmentMetadata? Attachment,
    DateTimeOffset CreatedAtUtc,
    Guid? OwnerUserId = null);
