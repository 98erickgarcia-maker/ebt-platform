using Ebt.Application.Configuration;
using Ebt.Application.Foundation;
using Ebt.Application.Security;
using Ebt.Domain.Foundation;
using Microsoft.Extensions.Options;

namespace Ebt.Api;

public static class FoundationRecordEndpoints
{
    public static IEndpointRouteBuilder MapFoundationRecordEndpoints(
        this IEndpointRouteBuilder endpoints)
    {
        var group = endpoints
            .MapGroup("/api/foundation/records")
            .RequireAuthorization();

        group.MapGet("/", ListAsync);
        group.MapPost("/", SaveAsync);
        group.MapGet("/{id:guid}", GetAsync);
        group.MapGet("/{id:guid}/attachment", DownloadAsync);

        return endpoints;
    }

    private static async Task<IResult> ListAsync(
        IServiceProvider services,
        IEbtTenantContext tenantContext,
        IOptions<EbtPlatformOptions> platformOptions,
        IOptions<QaPersistenceOptions> persistenceOptions,
        CancellationToken cancellationToken)
    {
        var identity = tenantContext.Current;
        var access = Authorize(identity, EbtPermission.FoundationRecordRead);
        if (access is not null)
            return access;

        if (!IsEnabled(platformOptions.Value, persistenceOptions.Value))
            return Results.NotFound();

        var service = services.GetRequiredService<FoundationRecordService>();
        var items = await service.ListAsync(identity!.TenantKey!, cancellationToken);
        return Results.Ok(items.Select(ToResponse));
    }

    private static async Task<IResult> SaveAsync(
        CreateFoundationRecordRequest request,
        IServiceProvider services,
        IEbtTenantContext tenantContext,
        IOptions<EbtPlatformOptions> platformOptions,
        IOptions<QaPersistenceOptions> persistenceOptions,
        HttpContext context,
        CancellationToken cancellationToken)
    {
        var identity = tenantContext.Current;
        var access = Authorize(identity, EbtPermission.FoundationRecordWrite);
        if (access is not null)
            return access;

        if (!IsEnabled(platformOptions.Value, persistenceOptions.Value))
            return Results.NotFound();

        var service = services.GetRequiredService<FoundationRecordService>();
        byte[]? attachment = null;

        if (!string.IsNullOrWhiteSpace(request.AttachmentBase64))
        {
            try
            {
                attachment = Convert.FromBase64String(request.AttachmentBase64);
            }
            catch (FormatException)
            {
                return InvalidRequest(context, "Anexo inválido.");
            }

            if (attachment.LongLength > 2 * 1024 * 1024)
                return InvalidRequest(context, "Anexo excede o limite da demonstração QA.");
        }

        try
        {
            var record = await service.SaveAsync(
                new FoundationRecordDraft(
                    identity!.TenantKey!,
                    request.Title,
                    request.AttachmentFileName,
                    request.AttachmentContentType,
                    attachment),
                cancellationToken);

            return Results.Created(
                $"/api/foundation/records/{record.Id}",
                ToResponse(record));
        }
        catch (ArgumentException error)
        {
            return InvalidRequest(context, error.Message);
        }
    }

    private static async Task<IResult> GetAsync(
        Guid id,
        IServiceProvider services,
        IEbtTenantContext tenantContext,
        IOptions<EbtPlatformOptions> platformOptions,
        IOptions<QaPersistenceOptions> persistenceOptions,
        CancellationToken cancellationToken)
    {
        var identity = tenantContext.Current;
        var access = Authorize(identity, EbtPermission.FoundationRecordRead);
        if (access is not null)
            return access;

        if (!IsEnabled(platformOptions.Value, persistenceOptions.Value))
            return Results.NotFound();

        var service = services.GetRequiredService<FoundationRecordService>();
        var record = await service.GetAsync(id, identity!.TenantKey!, cancellationToken);
        return record is null
            ? Results.NotFound()
            : Results.Ok(ToResponse(record));
    }

    private static async Task<IResult> DownloadAsync(
        Guid id,
        IServiceProvider services,
        IEbtTenantContext tenantContext,
        IOptions<EbtPlatformOptions> platformOptions,
        IOptions<QaPersistenceOptions> persistenceOptions,
        CancellationToken cancellationToken)
    {
        var identity = tenantContext.Current;
        var access = Authorize(identity, EbtPermission.FoundationAttachmentDownload);
        if (access is not null)
            return access;

        if (!IsEnabled(platformOptions.Value, persistenceOptions.Value))
            return Results.NotFound();

        var service = services.GetRequiredService<FoundationRecordService>();
        var download = await service.DownloadAsync(id, identity!.TenantKey!, cancellationToken);
        return download is null
            ? Results.NotFound()
            : Results.File(
                download.Content,
                download.ContentType,
                download.FileName,
                enableRangeProcessing: false);
    }

    private static IResult? Authorize(
        EbtIdentityProfile? identity,
        EbtPermission permission)
    {
        if (identity is null)
            return Results.Unauthorized();

        if (identity.TenantId is null
            || string.IsNullOrWhiteSpace(identity.TenantKey)
            || !EbtAccessMatrix.Allows(identity.Role, permission))
            return Results.Forbid();

        return null;
    }

    private static bool IsEnabled(
        EbtPlatformOptions platform,
        QaPersistenceOptions persistence) =>
        platform.SyntheticDataEnabled && persistence.Enabled;

    private static IResult InvalidRequest(HttpContext context, string detail) =>
        Results.Problem(
            statusCode: StatusCodes.Status400BadRequest,
            title: "Requisição inválida.",
            detail: detail,
            extensions: new Dictionary<string, object?>
            {
                ["traceId"] = SafeDiagnostics.GetTraceId(context)
            });

    private static FoundationRecordResponse ToResponse(FoundationStoredRecord record) =>
        new(
            record.Id,
            record.TenantKey,
            record.Title,
            record.CreatedAtUtc,
            record.Attachment is null
                ? null
                : new FoundationAttachmentResponse(
                    record.Attachment.FileName,
                    record.Attachment.ContentType,
                    record.Attachment.Length));
}

public sealed record CreateFoundationRecordRequest(
    string? TenantKey,
    string Title,
    string? AttachmentFileName,
    string? AttachmentContentType,
    string? AttachmentBase64);

public sealed record FoundationAttachmentResponse(
    string FileName,
    string ContentType,
    long Length);

public sealed record FoundationRecordResponse(
    Guid Id,
    string TenantKey,
    string Title,
    DateTimeOffset CreatedAtUtc,
    FoundationAttachmentResponse? Attachment);
