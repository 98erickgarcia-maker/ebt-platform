namespace Ebt.Application.Foundation;

public sealed record QaProbeWriteResult(
    Guid Id,
    string ConsumerKey,
    string FileName,
    string Sha256,
    long Length,
    DateTimeOffset CreatedAt);

public sealed record QaProbeReadResult(
    QaProbeWriteResult Metadata,
    byte[] Content);

public interface IQaProbeService
{
    Task InitializeAsync(CancellationToken cancellationToken = default);
    Task<QaProbeWriteResult> SaveAsync(
        string consumerKey,
        string fileName,
        byte[] content,
        CancellationToken cancellationToken = default);
    Task<QaProbeReadResult?> ReadAsync(
        Guid id,
        CancellationToken cancellationToken = default);
    Task<bool> CheckDatabaseAsync(CancellationToken cancellationToken = default);
    Task<bool> CheckStorageAsync(CancellationToken cancellationToken = default);
}
