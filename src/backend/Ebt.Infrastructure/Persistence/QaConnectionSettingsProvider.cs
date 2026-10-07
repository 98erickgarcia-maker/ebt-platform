using Azure.Storage.Blobs;
using Ebt.Application.Configuration;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Options;

namespace Ebt.Infrastructure.Persistence;

public sealed record QaConnectionSettings(
    string SqlConnectionString,
    string BlobConnectionString,
    string BlobContainerName);

public sealed class QaConnectionSettingsProvider(
    IOptions<QaPersistenceOptions> options)
{
    public QaConnectionSettings Get()
    {
        var current = options.Value;

        if (!current.Enabled)
            throw new InvalidOperationException("Persistência QA está desabilitada.");

        QaTargetGuard.ValidatePrivateConfiguration(current, Environment.GetEnvironmentVariable);

        var password = Environment.GetEnvironmentVariable(current.SqlPasswordEnvironmentVariable)!;
        var blobConnection = Environment.GetEnvironmentVariable(current.BlobConnectionEnvironmentVariable)!;

        var builder = new SqlConnectionStringBuilder
        {
            DataSource = $"{current.SqlHost},{current.SqlPort}",
            InitialCatalog = current.DatabaseName,
            UserID = current.SqlUser,
            Password = password,
            Encrypt = true,
            TrustServerCertificate = true,
            ConnectTimeout = 5,
            MultipleActiveResultSets = false,
            ApplicationName = "EBT Platform QA"
        };

        _ = new BlobServiceClient(blobConnection);

        return new QaConnectionSettings(
            builder.ConnectionString,
            blobConnection,
            current.BlobContainerName);
    }
}
