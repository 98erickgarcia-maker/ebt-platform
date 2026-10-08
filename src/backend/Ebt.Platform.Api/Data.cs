using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using System.Data;
using Microsoft.AspNetCore.DataProtection.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public sealed class AccessScope
{
    public Guid TenantId { get; set; }
    public Guid UserId { get; set; }
    public string Role { get; set; } = "";
    public string Portfolio { get; set; } = "";
    public bool System { get; set; }
    public bool IsAdmin => Role == "admin";
    public bool CanRead => Role is "admin" or "operator" or "reader";
    public bool CanWrite => Role is "admin" or "operator";
    public void RequireWrite() { if (!CanWrite) throw new ApiFault(403, "forbidden", "Seu perfil permite somente consulta."); }
    public void RequireAdmin() { if (!IsAdmin) throw new ApiFault(403, "forbidden", "Esta ação exige administrador da empresa."); }
}

public sealed class PlatformDb(DbContextOptions<PlatformDb> options, AccessScope scope) : DbContext(options), IDataProtectionKeyContext
{
    public DbSet<DataProtectionKey> DataProtectionKeys { get; set; } = null!;
    public DbSet<Tenant> Tenants => Set<Tenant>();
    public DbSet<PlatformUser> Users => Set<PlatformUser>();
    public DbSet<UserSession> Sessions => Set<UserSession>();
    public DbSet<Membership> Memberships => Set<Membership>();
    public DbSet<Contact> Contacts => Set<Contact>();
    public DbSet<ContactCreation> ContactCreations => Set<ContactCreation>();
    public DbSet<Organization> Organizations => Set<Organization>();
    public DbSet<Interaction> Interactions => Set<Interaction>();
    public DbSet<ContactTask> Tasks => Set<ContactTask>();
    public DbSet<Invitation> Invitations => Set<Invitation>();
    public DbSet<ApiCredential> Credentials => Set<ApiCredential>();
    public DbSet<ImportBatch> Imports => Set<ImportBatch>();
    public DbSet<ChannelConnection> Connections => Set<ChannelConnection>();
    public DbSet<Conversation> Conversations => Set<Conversation>();
    public DbSet<ConnectMessage> Messages => Set<ConnectMessage>();
    public DbSet<OutboxOperation> Outbox => Set<OutboxOperation>();
    public DbSet<WebhookReceipt> Receipts => Set<WebhookReceipt>();
    public DbSet<DeliveryEvent> DeliveryEvents => Set<DeliveryEvent>();
    public DbSet<CommercialDocument> Documents => Set<CommercialDocument>();
    public DbSet<DocumentVersion> DocumentVersions => Set<DocumentVersion>();
    public DbSet<AuditEntry> Audit => Set<AuditEntry>();

    private void Configure<T>(EntityTypeBuilder<T> entity) where T : TenantRow
    {
        entity.HasBaseType((Type?)null);
        entity.HasKey(x => new { x.TenantId, x.Id });
        entity.Property(x => x.Version).IsConcurrencyToken();
        entity.HasQueryFilter(x => x.TenantId == scope.TenantId);
        entity.HasOne<Tenant>().WithMany().HasForeignKey(x => x.TenantId).OnDelete(DeleteBehavior.Restrict);
    }
    protected override void OnModelCreating(ModelBuilder b)
    {
        b.HasDefaultSchema("ebt_connect");
        b.Ignore<TenantRow>();
        Configure(b.Entity<Membership>()); Configure(b.Entity<Invitation>()); Configure(b.Entity<ApiCredential>());
        Configure(b.Entity<Organization>()); Configure(b.Entity<Contact>()); Configure(b.Entity<Interaction>());
        Configure(b.Entity<ContactCreation>());
        Configure(b.Entity<ContactTask>()); Configure(b.Entity<ImportBatch>()); Configure(b.Entity<ChannelConnection>());
        Configure(b.Entity<Conversation>()); Configure(b.Entity<ConnectMessage>()); Configure(b.Entity<OutboxOperation>());
        Configure(b.Entity<DeliveryEvent>()); Configure(b.Entity<CommercialDocument>()); Configure(b.Entity<DocumentVersion>());
        Configure(b.Entity<AuditEntry>());
        b.Entity<PlatformUser>().HasIndex(x => x.Email).IsUnique();
        b.Entity<PlatformUser>().Property(x => x.Email).HasMaxLength(254);
        b.Entity<Membership>().HasIndex(x => new { x.TenantId, x.UserId }).IsUnique();
        b.Entity<Membership>().HasOne<PlatformUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Restrict);
        b.Entity<UserSession>().HasOne<Membership>().WithMany().HasForeignKey(x => new { x.TenantId, x.UserId }).HasPrincipalKey(x => new { x.TenantId, x.UserId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<UserSession>().HasIndex(x => x.ExpiresAt);
        b.Entity<Invitation>().Property(x => x.TokenHash).HasMaxLength(64);
        b.Entity<Invitation>().HasIndex(x => x.TokenHash).IsUnique();
        b.Entity<ApiCredential>().Property(x => x.TokenHash).HasMaxLength(64);
        b.Entity<ApiCredential>().HasIndex(x => x.TokenHash).IsUnique();
        b.Entity<ApiCredential>().HasOne<PlatformUser>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Restrict);
        b.Entity<Contact>().Property(x => x.ExternalKey).HasMaxLength(100);
        b.Entity<Contact>().HasIndex(x => new { x.TenantId, x.ExternalKey }).IsUnique();
        b.Entity<Contact>().HasOne<Organization>().WithMany().HasForeignKey(x => new { x.TenantId, x.OrganizationId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<Contact>().HasOne<Membership>().WithMany().HasForeignKey(x => new { x.TenantId, x.OwnerId }).HasPrincipalKey(x => new { x.TenantId, x.UserId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<ContactCreation>().HasOne<Contact>().WithMany().HasForeignKey(x => new { x.TenantId, x.ContactId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<ContactCreation>().Property(x => x.OperationKey).HasMaxLength(100);
        b.Entity<ContactCreation>().HasIndex(x => new { x.TenantId, x.OperationKey }).IsUnique();
        b.Entity<Organization>().Property(x => x.ExternalKey).HasMaxLength(100);
        b.Entity<Organization>().HasIndex(x => new { x.TenantId, x.ExternalKey }).IsUnique();
        b.Entity<Interaction>().HasOne<Contact>().WithMany().HasForeignKey(x => new { x.TenantId, x.ContactId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<Interaction>().Property(x => x.OperationKey).HasMaxLength(100);
        b.Entity<Interaction>().HasIndex(x => new { x.TenantId, x.ContactId, x.OperationKey }).IsUnique();
        b.Entity<ContactTask>().HasOne<Contact>().WithMany().HasForeignKey(x => new { x.TenantId, x.ContactId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<ContactTask>().HasOne<Membership>().WithMany().HasForeignKey(x => new { x.TenantId, x.OwnerId }).HasPrincipalKey(x => new { x.TenantId, x.UserId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<ContactTask>().Property(x => x.OperationKey).HasMaxLength(100);
        b.Entity<ContactTask>().HasIndex(x => new { x.TenantId, x.ContactId, x.OperationKey }).IsUnique();
        b.Entity<ImportBatch>().Property(x => x.OperationKey).HasMaxLength(100);
        b.Entity<ImportBatch>().HasIndex(x => new { x.TenantId, x.UserId, x.OperationKey }).IsUnique().HasFilter("[OperationKey] <> ''");
        b.Entity<ChannelConnection>().Property(x => x.PhoneNumberId).HasMaxLength(100);
        b.Entity<ChannelConnection>().Property(x => x.AppKey).HasMaxLength(100);
        b.Entity<ChannelConnection>().Property(x => x.AccountId).HasMaxLength(100);
        b.Entity<ChannelConnection>().HasIndex(x => new { x.AppKey, x.AccountId, x.PhoneNumberId }).IsUnique();
        b.Entity<Conversation>().HasOne<Contact>().WithMany().HasForeignKey(x => new { x.TenantId, x.ContactId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<Conversation>().HasOne<ChannelConnection>().WithMany().HasForeignKey(x => new { x.TenantId, x.ConnectionId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<Conversation>().Property(x => x.Recipient).HasMaxLength(24);
        b.Entity<Conversation>().HasIndex(x => new { x.TenantId, x.ConnectionId, x.Recipient }).IsUnique();
        b.Entity<ConnectMessage>().HasOne<Conversation>().WithMany().HasForeignKey(x => new { x.TenantId, x.ConversationId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<ConnectMessage>().HasOne<ChannelConnection>().WithMany().HasForeignKey(x => new { x.TenantId, x.ConnectionId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<ConnectMessage>().Property(x => x.ProviderId).HasMaxLength(250).UseCollation("Latin1_General_100_BIN2");
        b.Entity<DeliveryEvent>().Property(x => x.ProviderId).HasMaxLength(250).UseCollation("Latin1_General_100_BIN2");
        b.Entity<ConnectMessage>().HasIndex(x => new { x.TenantId, x.ConnectionId, x.ProviderId }).IsUnique().HasFilter("[ProviderId] <> ''");
        b.Entity<OutboxOperation>().HasOne<ConnectMessage>().WithMany().HasForeignKey(x => new { x.TenantId, x.MessageId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<OutboxOperation>().Property(x => x.OperationKey).HasMaxLength(100);
        b.Entity<OutboxOperation>().HasIndex(x => new { x.TenantId, x.ConversationId, x.OperationKey }).IsUnique();
        b.Entity<DeliveryEvent>().HasOne<ChannelConnection>().WithMany().HasForeignKey(x => new { x.TenantId, x.ConnectionId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<DeliveryEvent>().Property(x => x.EventKey).HasMaxLength(64);
        b.Entity<DeliveryEvent>().HasIndex(x => new { x.TenantId, x.ConnectionId, x.EventKey }).IsUnique();
        b.Entity<WebhookReceipt>().Property(x => x.AppKey).HasMaxLength(100);
        b.Entity<WebhookReceipt>().Property(x => x.ProviderEventId).HasMaxLength(200).UseCollation("Latin1_General_100_BIN2");
        b.Entity<WebhookReceipt>().HasIndex(x => new { x.AppKey, x.ProviderEventId }).IsUnique().HasFilter("[ProviderEventId] <> ''");
        b.Entity<WebhookReceipt>().Property(x => x.BodyHash).HasMaxLength(64);
        b.Entity<WebhookReceipt>().HasIndex(x => new { x.AppKey, x.BodyHash }).IsUnique();
        b.Entity<CommercialDocument>().HasOne<Contact>().WithMany().HasForeignKey(x => new { x.TenantId, x.ContactId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<CommercialDocument>().HasOne<ContactTask>().WithMany().HasForeignKey(x => new { x.TenantId, x.TaskId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<DocumentVersion>().HasOne<CommercialDocument>().WithMany().HasForeignKey(x => new { x.TenantId, x.DocumentId }).OnDelete(DeleteBehavior.Restrict);
        b.Entity<DocumentVersion>().HasIndex(x => new { x.TenantId, x.DocumentId, x.Number }).IsUnique();
        b.Entity<DocumentVersion>().Property(x => x.OperationKey).HasMaxLength(100);
        b.Entity<DocumentVersion>().HasIndex(x => new { x.TenantId, x.DocumentId, x.OperationKey }).IsUnique();
        b.Entity<CommercialDocument>().Property(x => x.CreationKey).HasMaxLength(100);
        b.Entity<CommercialDocument>().HasIndex(x => new { x.TenantId, x.ContactId, x.CreationKey }).IsUnique();
    }
    public override Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        foreach (var entry in ChangeTracker.Entries<TenantRow>().Where(x => x.State is EntityState.Added or EntityState.Modified or EntityState.Deleted))
        {
            if (!scope.System && (scope.TenantId == Guid.Empty || entry.Entity.TenantId != scope.TenantId))
                throw new ApiFault(403, "tenant_write_denied", "Contexto da operação inválido.");
            if (entry.State == EntityState.Modified) entry.Entity.Version++;
        }
        return base.SaveChangesAsync(ct);
    }
    public async Task<Microsoft.EntityFrameworkCore.Storage.IDbContextTransaction> Lock(string key, CancellationToken ct = default)
    {
        var tx = await Database.BeginTransactionAsync(IsolationLevel.ReadCommitted, ct);
        try
        {
            var resource = key.StartsWith("global:", StringComparison.Ordinal) ? "ebt:" + key : $"ebt:{scope.TenantId}:{key}";
            await Database.ExecuteSqlInterpolatedAsync($"DECLARE @r int; EXEC @r = sp_getapplock @Resource={resource}, @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=15000; IF @r < 0 THROW 51001, 'Operation busy', 1;", ct);
            return tx;
        }
        catch { await tx.DisposeAsync(); throw; }
    }
    public void Record(AccessScope access, string action, Guid? resource, string trace) => Audit.Add(new AuditEntry
        { TenantId = access.TenantId, ActorId = access.UserId == Guid.Empty ? null : access.UserId, Action = action, ResourceId = resource, TraceId = trace });
    public IQueryable<Contact> VisibleContacts(AccessScope access) => Contacts.Where(x => access.IsAdmin || x.Portfolio == access.Portfolio);
    public async Task<long> GlobalDocumentBytes()
    {
        var previous = scope.System;
        try { scope.System = true; return await DocumentVersions.IgnoreQueryFilters().SumAsync(x => (long)x.Content.Length); }
        finally { scope.System = previous; }
    }
    public async Task<Contact> Contact(Guid id, AccessScope access, CancellationToken ct = default) =>
        await VisibleContacts(access).SingleOrDefaultAsync(x => x.Id == id, ct) ?? throw ApiFault.NotFound();
    public async Task<Membership> Owner(Guid id, AccessScope access, string portfolio, CancellationToken ct = default) =>
        await Memberships.SingleOrDefaultAsync(x => x.UserId == id && x.Active && (x.Role == "admin" || x.Role == "operator") && (x.Role == "admin" || x.Portfolio == portfolio), ct)
        ?? throw new ApiFault(400, "invalid_owner", "Selecione um responsável ativo nesta carteira.");
}
