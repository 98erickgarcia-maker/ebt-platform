namespace Ebt.Platform.Api;

public abstract class TenantRow
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid TenantId { get; set; }
    public long Version { get; set; } = 1;
}
public sealed class Tenant
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = "";
    public string Product { get; set; } = "connect";
    public bool Active { get; set; } = true;
}
public sealed class PlatformUser
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Email { get; set; } = "";
    public string Name { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public string Stamp { get; set; } = Guid.NewGuid().ToString("N");
    public bool Active { get; set; } = true;
    public int FailedLogins { get; set; }
    public DateTimeOffset? LockedUntil { get; set; }
}
public sealed class Membership : TenantRow
{
    public Guid UserId { get; set; }
    public string Role { get; set; } = "reader";
    public string Portfolio { get; set; } = "principal";
    public bool Active { get; set; } = true;
}
public sealed class UserSession
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public Guid TenantId { get; set; }
    public DateTimeOffset ExpiresAt { get; set; }
    public bool Revoked { get; set; }
}
public sealed class Invitation : TenantRow
{
    public string Email { get; set; } = "";
    public string Role { get; set; } = "reader";
    public string Portfolio { get; set; } = "principal";
    public string TokenHash { get; set; } = "";
    public DateTimeOffset ExpiresAt { get; set; }
    public DateTimeOffset? UsedAt { get; set; }
}
public sealed class ApiCredential : TenantRow
{
    public Guid UserId { get; set; }
    public string Name { get; set; } = "";
    public string TokenHash { get; set; } = "";
    public DateTimeOffset ExpiresAt { get; set; }
    public bool Active { get; set; } = true;
}
public sealed class Organization : TenantRow
{
    public string Name { get; set; } = "";
    public string ExternalKey { get; set; } = "";
    public string Portfolio { get; set; } = "principal";
}
public sealed class Contact : TenantRow
{
    public string CreationHash { get; set; } = "";
    public string Name { get; set; } = "";
    public string ExternalKey { get; set; } = "";
    public string Email { get; set; } = "";
    public string Phone { get; set; } = "";
    public string Stage { get; set; } = "novo";
    public string Portfolio { get; set; } = "principal";
    public Guid OwnerId { get; set; }
    public Guid? OrganizationId { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}
public sealed class Interaction : TenantRow
{
    public Guid ContactId { get; set; }
    public Guid ActorId { get; set; }
    public string Kind { get; set; } = "note";
    public string Content { get; set; } = "";
    public DateTimeOffset OccurredAt { get; set; }
    public DateTimeOffset RecordedAt { get; set; } = DateTimeOffset.UtcNow;
    public string OperationKey { get; set; } = "";
    public string PayloadHash { get; set; } = "";
}
public sealed class ContactCreation : TenantRow
{
    public Guid ContactId { get; set; }
    public string OperationKey { get; set; } = "";
    public string PayloadHash { get; set; } = "";
}
public sealed class ContactTask : TenantRow
{
    public string CloseKey { get; set; } = "";
    public string CloseHash { get; set; } = "";
    public Guid ContactId { get; set; }
    public Guid OwnerId { get; set; }
    public string Title { get; set; } = "";
    public DateTimeOffset DueAt { get; set; }
    public string State { get; set; } = "open";
    public string Result { get; set; } = "";
    public DateTimeOffset? ClosedAt { get; set; }
    public string OperationKey { get; set; } = "";
    public string PayloadHash { get; set; } = "";
}
public sealed class ImportBatch : TenantRow
{
    public Guid UserId { get; set; }
    public string Portfolio { get; set; } = "";
    public string Content { get; set; } = "";
    public string PayloadHash { get; set; } = "";
    public string State { get; set; } = "preview";
    public string OperationKey { get; set; } = "";
    public string ResultJson { get; set; } = "[]";
    public DateTimeOffset ExpiresAt { get; set; }
}
public sealed class ChannelConnection : TenantRow
{
    public string Name { get; set; } = "";
    public string Provider { get; set; } = "qa";
    public string AppKey { get; set; } = "";
    public string AccountId { get; set; } = "";
    public string PhoneNumberId { get; set; } = "";
    public string SecretRef { get; set; } = "";
    public string Portfolio { get; set; } = "principal";
    public Guid OperatorId { get; set; }
    public bool Active { get; set; } = true;
}
public sealed class Conversation : TenantRow
{
    public Guid ContactId { get; set; }
    public Guid ConnectionId { get; set; }
    public string Recipient { get; set; } = "";
    public string State { get; set; } = "open";
    public DateTimeOffset? LastInboundAt { get; set; }
}
public sealed class ConnectMessage : TenantRow
{
    public Guid ConnectionId { get; set; }
    public Guid ConversationId { get; set; }
    public string Direction { get; set; } = "incoming";
    public string Content { get; set; } = "";
    public string Status { get; set; } = "received";
    public string ProviderId { get; set; } = "";
    public Guid? ReplyToMessageId { get; set; }
    public Guid? ActorId { get; set; }
    public string FailureCode { get; set; } = "";
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}
public sealed class OutboxOperation : TenantRow
{
    public Guid MessageId { get; set; }
    public Guid ConversationId { get; set; }
    public Guid ActorId { get; set; }
    public string OperationKey { get; set; } = "";
    public string PayloadHash { get; set; } = "";
    public string State { get; set; } = "pending";
    public int Attempts { get; set; }
    public DateTimeOffset DueAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? LeaseUntil { get; set; }
    public string Fence { get; set; } = "";
}
// Raw envelopes encrypted with the application's protected persistent key ring.
public sealed class WebhookReceipt
{
    public string ProviderEventId { get; set; } = "";
    public Guid Id { get; set; } = Guid.NewGuid();
    public string AppKey { get; set; } = "";
    public string BodyHash { get; set; } = "";
    public string ProtectedBody { get; set; } = "";
    public string State { get; set; } = "pending";
    public string Diagnostic { get; set; } = "";
    public DateTimeOffset ReceivedAt { get; set; } = DateTimeOffset.UtcNow;
}
public sealed class DeliveryEvent : TenantRow
{
    public Guid ConnectionId { get; set; }
    public string ProviderId { get; set; } = "";
    public string Status { get; set; } = "";
    public DateTimeOffset OccurredAt { get; set; }
    public string EventKey { get; set; } = "";
}
public sealed class CommercialDocument : TenantRow
{
    public string CreationKey { get; set; } = "";
    public string CreationHash { get; set; } = "";
    public Guid ContactId { get; set; }
    public Guid? TaskId { get; set; }
    public string Title { get; set; } = "";
    public int CurrentVersion { get; set; }
    public string ReviewState { get; set; } = "pending";
}
// Bounded SQL BLOB storage: content and metadata/version are one atomic commit.
public sealed class DocumentVersion : TenantRow
{
    public string ReviewState { get; set; } = "pending";
    public string ReviewReason { get; set; } = "";
    public Guid? ReviewedBy { get; set; }
    public DateTimeOffset? ReviewedAt { get; set; }
    public string ScanState { get; set; } = "not_scanned";
    public string OperationKey { get; set; } = "";
    public string PayloadHash { get; set; } = "";
    public Guid DocumentId { get; set; }
    public int Number { get; set; }
    public byte[] Content { get; set; } = [];
    public string Sha256 { get; set; } = "";
    public string FileName { get; set; } = "";
    public string MediaType { get; set; } = "";
    public Guid ActorId { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}
public sealed class AuditEntry : TenantRow
{
    public Guid? ActorId { get; set; }
    public string Action { get; set; } = "";
    public Guid? ResourceId { get; set; }
    public string TraceId { get; set; } = "";
    public DateTimeOffset At { get; set; } = DateTimeOffset.UtcNow;
}
