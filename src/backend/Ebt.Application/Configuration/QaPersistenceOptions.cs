namespace Ebt.Application.Configuration;

public sealed class QaPersistenceOptions
{
    public const string SectionName = "QaPersistence";

    public bool Enabled { get; init; }
    public string SqlHost { get; init; } = "127.0.0.1";
    public int SqlPort { get; init; } = 1433;
    public string SqlUser { get; init; } = "sa";
    public string DatabaseName { get; init; } = "EbtQa_App";
    public string SqlPasswordEnvironmentVariable { get; init; } = "EBT_QA_SQL_PASSWORD";
    public string BlobConnectionEnvironmentVariable { get; init; } = "EBT_QA_BLOB_CONNECTION";
    public string BlobContainerName { get; init; } = "ebt-qa-app";
}
