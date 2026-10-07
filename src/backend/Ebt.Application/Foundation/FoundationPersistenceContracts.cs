using Ebt.Domain.Foundation;
using Ebt.Application.Security;

namespace Ebt.Application.Foundation;

public sealed record FoundationRecordDraft(
    string TenantKey,
    string Title,
    string? AttachmentFileName = null,
    string? AttachmentContentType = null,
    byte[]? AttachmentContent = null,
    Guid? OwnerUserId = null);

public sealed record FoundationDownload(
    string FileName,
    string ContentType,
    byte[] Content);

public interface IFoundationRecordRepository
{
    Task AddAsync(FoundationStoredRecord record, CancellationToken cancellationToken = default);
    Task<FoundationStoredRecord?> FindAsync(Guid id, string tenantKey, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<FoundationStoredRecord>> ListAsync(string tenantKey, CancellationToken cancellationToken = default, Guid? ownerUserId = null);
    Task<bool> CanConnectAsync(CancellationToken cancellationToken = default);
    Task EnsureCreatedAsync(CancellationToken cancellationToken = default);
}

public interface IFoundationBinaryStore
{
    Task<FoundationAttachmentMetadata> UploadAsync(
        string blobName,
        string fileName,
        string contentType,
        byte[] content,
        CancellationToken cancellationToken = default);

    Task<byte[]?> DownloadAsync(string blobName, CancellationToken cancellationToken = default);
    Task DeleteIfExistsAsync(string blobName, CancellationToken cancellationToken = default);
    Task<bool> CanConnectAsync(CancellationToken cancellationToken = default);
    Task EnsureContainerAsync(CancellationToken cancellationToken = default);
}

public sealed class FoundationRecordService(
    IFoundationRecordRepository repository,
    IFoundationBinaryStore binaryStore)
{
    public Task<FoundationStoredRecord> SaveForIdentityAsync(
        FoundationRecordDraft draft, EbtIdentityProfile identity, CancellationToken cancellationToken = default)
    {
        if (!EbtResourceAccess.HasTenantAccess(identity, EbtPermission.FoundationRecordWrite))
            throw new UnauthorizedAccessException();
        return SaveAsync(draft with { TenantKey = identity.TenantKey!, OwnerUserId = identity.UserId }, cancellationToken);
    }

    public async Task<FoundationStoredRecord?> GetForIdentityAsync(
        Guid id, EbtIdentityProfile identity, CancellationToken cancellationToken = default)
    {
        if (!EbtResourceAccess.HasTenantAccess(identity, EbtPermission.FoundationRecordRead))
            return null;
        var record = await GetAsync(id, identity.TenantKey!, cancellationToken);
        return record is not null && EbtResourceAccess.CanRead(identity, record) ? record : null;
    }

    public async Task<IReadOnlyList<FoundationStoredRecord>> ListForIdentityAsync(
        EbtIdentityProfile identity, CancellationToken cancellationToken = default)
    {
        if (!EbtResourceAccess.HasTenantAccess(identity, EbtPermission.FoundationRecordRead))
            return [];
        var records = await repository.ListAsync(NormalizeTenantKey(identity.TenantKey), cancellationToken,
            identity.Role == EbtRole.Operator ? identity.UserId : null);
        return records.Where(record => EbtResourceAccess.CanRead(identity, record)).ToArray();
    }

    public async Task<FoundationDownload?> DownloadForIdentityAsync(
        Guid id, EbtIdentityProfile identity, CancellationToken cancellationToken = default)
    {
        if (!EbtResourceAccess.HasTenantAccess(identity, EbtPermission.FoundationAttachmentDownload))
            return null;
        var record = await GetForIdentityAsync(id, identity, cancellationToken);
        if (record?.Attachment is null) return null;
        var binary = await binaryStore.DownloadAsync(record.Attachment.BlobName, cancellationToken);
        return binary is null ? null : new FoundationDownload(
            record.Attachment.FileName, record.Attachment.ContentType, binary);
    }

    public async Task<FoundationStoredRecord> SaveAsync(
        FoundationRecordDraft draft,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(draft);

        var tenantKey = NormalizeTenantKey(draft.TenantKey);
        var title = draft.Title?.Trim();

        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("TÃ­tulo obrigatÃ³rio.", nameof(draft));

        if (title.Length > 200)
            throw new ArgumentException("TÃ­tulo excede o limite permitido.", nameof(draft));

        var id = Guid.NewGuid();
        FoundationAttachmentMetadata? attachment = null;

        try
        {
            if (draft.AttachmentContent is { Length: > 0 } binary)
            {
                var fileName = NormalizeFileName(draft.AttachmentFileName);
                var contentType = NormalizeContentType(draft.AttachmentContentType);
                var blobName = $"{tenantKey}/{id:N}/{fileName}";

                attachment = await binaryStore.UploadAsync(
                    blobName,
                    fileName,
                    contentType,
                    binary,
                    cancellationToken);
            }

            var record = new FoundationStoredRecord(
                id,
                tenantKey,
                title,
                attachment,
                DateTimeOffset.UtcNow,
                draft.OwnerUserId);

            await repository.AddAsync(record, cancellationToken);
            return record;
        }
        catch
        {
            if (attachment is not null)
            {
                try
                {
                    await binaryStore.DeleteIfExistsAsync(attachment.BlobName, cancellationToken);
                }
                catch
                {
                    // Preserve the original persistence failure.
                }
            }

            throw;
        }
    }

    public Task<FoundationStoredRecord?> GetAsync(
        Guid id,
        string tenantKey,
        CancellationToken cancellationToken = default) =>
        repository.FindAsync(id, NormalizeTenantKey(tenantKey), cancellationToken);

    public Task<IReadOnlyList<FoundationStoredRecord>> ListAsync(
        string tenantKey,
        CancellationToken cancellationToken = default) =>
        repository.ListAsync(NormalizeTenantKey(tenantKey), cancellationToken);

    public async Task<FoundationDownload?> DownloadAsync(
        Guid id,
        string tenantKey,
        CancellationToken cancellationToken = default)
    {
        var record = await repository.FindAsync(
            id,
            NormalizeTenantKey(tenantKey),
            cancellationToken);
        if (record?.Attachment is null)
            return null;

        var binary = await binaryStore.DownloadAsync(record.Attachment.BlobName, cancellationToken);
        if (binary is null)
            return null;

        return new FoundationDownload(
            record.Attachment.FileName,
            record.Attachment.ContentType,
            binary);
    }

    private static string NormalizeTenantKey(string? value)
    {
        var tenantKey = value?.Trim().ToLowerInvariant();
        if (string.IsNullOrWhiteSpace(tenantKey)
            || tenantKey.Length > 64
            || tenantKey.Any(character =>
                !char.IsAsciiLetterOrDigit(character) && character is not '-' and not '_'))
            throw new ArgumentException("Identificador de consumidor invÃ¡lido.", nameof(value));

        return tenantKey;
    }

    private static string NormalizeFileName(string? value)
    {
        var fileName = Path.GetFileName(value?.Trim());
        if (string.IsNullOrWhiteSpace(fileName))
            return "anexo.bin";

        return fileName.Length <= 120
            ? fileName
            : fileName[..120];
    }

    private static string NormalizeContentType(string? value)
    {
        var contentType = value?.Trim();
        if (string.IsNullOrWhiteSpace(contentType)
            || contentType.Length > 120
            || contentType.Contains((char)13)
            || contentType.Contains((char)10))
            return "application/octet-stream";

        return contentType;
    }
}
