using System.Security.Cryptography;
using Ebt.Application.Configuration;
using Ebt.Application.Foundation;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Infrastructure.Foundation;

public sealed class QaProbeService : IQaProbeService
{
    private readonly QaInfrastructureOptions _options;
    private readonly DbContextOptions<QaFoundationDbContext> _dbOptions;

    public QaProbeService(QaInfrastructureOptions options)
    {
        _options = options;
        QaInfrastructureGuard.Validate(options, options.EnvironmentName);

        var databasePath = Path.GetFullPath(options.DatabaseFile);
        _dbOptions = new DbContextOptionsBuilder<QaFoundationDbContext>()
            .UseSqlite($"Data Source={databasePath}")
            .Options;
    }

    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
        Directory.CreateDirectory(Path.GetFullPath(_options.StorageRoot));
        var databaseDirectory = Path.GetDirectoryName(Path.GetFullPath(_options.DatabaseFile));
        if (!string.IsNullOrWhiteSpace(databaseDirectory))
            Directory.CreateDirectory(databaseDirectory);

        await using var db = new QaFoundationDbContext(_dbOptions);
        await db.Database.EnsureCreatedAsync(cancellationToken);
    }

    public async Task<QaProbeWriteResult> SaveAsync(
        string consumerKey,
        string fileName,
        byte[] content,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(consumerKey))
            throw new ArgumentException("ConsumerKey é obrigatório.", nameof(consumerKey));

        if (content.Length == 0)
            throw new ArgumentException("Conteúdo vazio não é aceito.", nameof(content));

        var safeFileName = Path.GetFileName(fileName);
        if (string.IsNullOrWhiteSpace(safeFileName))
            throw new ArgumentException("Nome de arquivo inválido.", nameof(fileName));

        await InitializeAsync(cancellationToken);

        var id = Guid.NewGuid();
        var storageKey = $"{id:N}.bin";
        var storagePath = Path.Combine(Path.GetFullPath(_options.StorageRoot), storageKey);
        var sha256 = Convert.ToHexString(SHA256.HashData(content)).ToLowerInvariant();
        var createdAt = DateTimeOffset.UtcNow;

        await File.WriteAllBytesAsync(storagePath, content, cancellationToken);

        var entity = new QaProbeMetadataEntity
        {
            Id = id,
            ConsumerKey = consumerKey.Trim(),
            FileName = safeFileName,
            StorageKey = storageKey,
            Sha256 = sha256,
            Length = content.LongLength,
            CreatedAt = createdAt
        };

        await using var db = new QaFoundationDbContext(_dbOptions);
        db.ProbeMetadata.Add(entity);
        try
        {
            await db.SaveChangesAsync(cancellationToken);
        }
        catch
        {
            File.Delete(storagePath);
            throw;
        }

        return ToResult(entity);
    }

    public async Task<QaProbeReadResult?> ReadAsync(
        Guid id,
        CancellationToken cancellationToken = default)
    {
        await InitializeAsync(cancellationToken);

        await using var db = new QaFoundationDbContext(_dbOptions);
        var entity = await db.ProbeMetadata
            .AsNoTracking()
            .SingleOrDefaultAsync(item => item.Id == id, cancellationToken);

        if (entity is null)
            return null;

        var storagePath = Path.Combine(Path.GetFullPath(_options.StorageRoot), entity.StorageKey);
        if (!File.Exists(storagePath))
            throw new InvalidDataException("Binário de QA não encontrado.");

        var content = await File.ReadAllBytesAsync(storagePath, cancellationToken);
        var actualHash = Convert.ToHexString(SHA256.HashData(content)).ToLowerInvariant();
        if (!CryptographicOperations.FixedTimeEquals(
                Convert.FromHexString(actualHash),
                Convert.FromHexString(entity.Sha256)))
            throw new InvalidDataException("Integridade do binário de QA inválida.");

        return new QaProbeReadResult(ToResult(entity), content);
    }

    public async Task<bool> CheckDatabaseAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            await InitializeAsync(cancellationToken);
            await using var db = new QaFoundationDbContext(_dbOptions);
            return await db.Database.CanConnectAsync(cancellationToken);
        }
        catch
        {
            return false;
        }
    }

    public async Task<bool> CheckStorageAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var root = Path.GetFullPath(_options.StorageRoot);
            Directory.CreateDirectory(root);
            var probe = Path.Combine(root, $".health-{Guid.NewGuid():N}");
            await File.WriteAllBytesAsync(probe, [0x45, 0x42, 0x54], cancellationToken);
            File.Delete(probe);
            return true;
        }
        catch
        {
            return false;
        }
    }

    private static QaProbeWriteResult ToResult(QaProbeMetadataEntity entity) =>
        new(
            entity.Id,
            entity.ConsumerKey,
            entity.FileName,
            entity.Sha256,
            entity.Length,
            entity.CreatedAt);
}
