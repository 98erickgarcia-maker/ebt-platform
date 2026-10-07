using Ebt.Application.Foundation;
using Ebt.Application.Security;
using Ebt.Domain.Foundation;

namespace Ebt.Foundation.Tests;

public sealed class Pac06ResourceTests
{
    private static readonly Guid Owner = Guid.Parse("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
    private static EbtIdentityProfile Identity(EbtRole role, string tenant = "orbe") =>
        new(Owner, Guid.NewGuid(), tenant, "qa@demo.invalid", "QA", role, true);

    [Theory]
    [InlineData(EbtRole.Administrator, false, true)]
    [InlineData(EbtRole.Operator, false, false)]
    [InlineData(EbtRole.Operator, true, true)]
    [InlineData(EbtRole.ReadOnly, false, true)]
    [InlineData(EbtRole.TechnicalSupport, true, false)]
    public void Resource_scope_is_enforced(EbtRole role, bool owned, bool allowed)
    {
        var record = new FoundationStoredRecord(Guid.NewGuid(), "orbe", "QA", null,
            DateTimeOffset.UtcNow, owned ? Owner : null);
        Assert.Equal(allowed, EbtResourceAccess.CanRead(Identity(role), record));
        Assert.False(EbtResourceAccess.CanRead(Identity(role, "nexo"), record));
        Assert.False(EbtResourceAccess.CanRead(Identity(role) with { IsActive = false }, record));
    }

    [Fact]
    public async Task Denied_resource_does_not_read_Blob_and_client_owner_is_ignored()
    {
        var repository = new MemoryRepository();
        var binary = new CountingBinaryStore();
        var service = new FoundationRecordService(repository, binary);
        var admin = Identity(EbtRole.Administrator) with { UserId = Guid.NewGuid() };
        var record = await service.SaveForIdentityAsync(new("nexo", "QA", "proof.txt", "text/plain", [1, 2], Owner), admin);
        Assert.Equal("orbe", record.TenantKey);
        Assert.Equal(admin.UserId, record.OwnerUserId);
        Assert.Null(await service.DownloadForIdentityAsync(record.Id, Identity(EbtRole.Operator)));
        Assert.Equal(0, binary.Reads);
        Assert.Empty(await service.ListForIdentityAsync(Identity(EbtRole.Operator)));
        Assert.NotNull(await service.DownloadForIdentityAsync(record.Id, admin));
        Assert.Equal(1, binary.Reads);
    }

    private sealed class MemoryRepository : IFoundationRecordRepository
    {
        private readonly List<FoundationStoredRecord> records = [];
        public Task AddAsync(FoundationStoredRecord record, CancellationToken cancellationToken = default) { records.Add(record); return Task.CompletedTask; }
        public Task<FoundationStoredRecord?> FindAsync(Guid id, string tenantKey, CancellationToken cancellationToken = default) =>
            Task.FromResult(records.SingleOrDefault(r => r.Id == id && r.TenantKey == tenantKey));
        public Task<IReadOnlyList<FoundationStoredRecord>> ListAsync(string tenantKey, CancellationToken cancellationToken = default, Guid? ownerUserId = null) =>
            Task.FromResult<IReadOnlyList<FoundationStoredRecord>>(records.Where(r => r.TenantKey == tenantKey && (ownerUserId is null || r.OwnerUserId == ownerUserId)).ToArray());
        public Task<bool> CanConnectAsync(CancellationToken cancellationToken = default) => Task.FromResult(true);
        public Task EnsureCreatedAsync(CancellationToken cancellationToken = default) => Task.CompletedTask;
    }
    private sealed class CountingBinaryStore : IFoundationBinaryStore
    {
        public int Reads { get; private set; }
        public Task<FoundationAttachmentMetadata> UploadAsync(string blobName, string fileName, string contentType, byte[] content, CancellationToken cancellationToken = default) =>
            Task.FromResult(new FoundationAttachmentMetadata(blobName, fileName, contentType, content.Length));
        public Task<byte[]?> DownloadAsync(string blobName, CancellationToken cancellationToken = default) { Reads++; return Task.FromResult<byte[]?>([1, 2]); }
        public Task DeleteIfExistsAsync(string blobName, CancellationToken cancellationToken = default) => Task.CompletedTask;
        public Task<bool> CanConnectAsync(CancellationToken cancellationToken = default) => Task.FromResult(true);
        public Task EnsureContainerAsync(CancellationToken cancellationToken = default) => Task.CompletedTask;
    }
}
