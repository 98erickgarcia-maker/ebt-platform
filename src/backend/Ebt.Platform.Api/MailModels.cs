namespace Ebt.Platform.Api;

public sealed class MailTemplate : TenantRow
{
    public string Channel { get; set; } = "email";
    public string Purpose { get; set; } = "prospection";
    public string Name { get; set; } = "";
    public string Subject { get; set; } = "";
    public string Body { get; set; } = "";
    public string Portfolio { get; set; } = "principal";
    public string CreationKey { get; set; } = "";
    public string CreationHash { get; set; } = "";
    public bool Active { get; set; } = true;
}
public sealed class MailDraft : TenantRow
{
    public Guid ContactId { get; set; }
    public Guid ActorId { get; set; }
    public string Recipient { get; set; } = "";
    public string Subject { get; set; } = "";
    public string Body { get; set; } = "";
    public string Origin { get; set; } = "manual";
    public string State { get; set; } = "draft";
    public Guid? ApprovedBy { get; set; }
    public DateTimeOffset? ApprovedAt { get; set; }
    public Guid? DocumentId { get; set; }
    public int? DocumentNumber { get; set; }
    public string CreationKey { get; set; } = "";
    public string CreationHash { get; set; } = "";
    public string Diagnostic { get; set; } = "";
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? AttemptedAt { get; set; }
}
// Every content/state change is retained as an immutable application snapshot.
public sealed class MailRevision : TenantRow
{
    public string OperationKey { get; set; } = "";
    public string PayloadHash { get; set; } = "";
    public Guid DraftId { get; set; }
    public Guid ActorId { get; set; }
    public string Subject { get; set; } = "";
    public string Body { get; set; } = "";
    public string Recipient { get; set; } = "";
    public string State { get; set; } = "";
    public string Reason { get; set; } = "";
    public DateTimeOffset At { get; set; } = DateTimeOffset.UtcNow;
}
public sealed class MailSuppression : TenantRow
{
    public string Value { get; set; } = "";
    public string Reason { get; set; } = "";
    public Guid ActorId { get; set; }
    public bool Active { get; set; } = true;
}
public sealed class MailSettings : TenantRow
{
    public int IntervalSeconds { get; set; } = 3;
    public int DailyCap { get; set; } = 100;
    public bool Paused { get; set; } = true;
    public DateTimeOffset? NextSendAt { get; set; }
}
public sealed class MailQuota : TenantRow
{
    public string Day { get; set; } = "";
    public int Used { get; set; }
}
public sealed record MailTemplateCommand(string Name, string Subject, string Body, bool Active = true, string Channel = "email", string Purpose = "prospection");
public sealed record MailDraftCommand(Guid ContactId, string Subject, string Body, Guid? DocumentId = null, Guid? TemplateId = null, long? TemplateVersion = null);
public sealed record MailBatchCommand(Guid TemplateId, Guid[] ContactIds);
public sealed record MailActionCommand(string Action, string? Reason = null);
public sealed record MailSettingsCommand(int IntervalSeconds, int DailyCap, bool Paused);
public sealed record MailSuppressionCommand(string Value, string Reason, bool Active = true);
