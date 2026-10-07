using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Ebt.Application.Foundation;
using Ebt.Domain.Foundation;

namespace Ebt.Infrastructure.Persistence;

public sealed class AzureBlobFoundationBinaryStore(
    BlobContainerClient container) : IFoundationBinaryStore
{
    public async Task<FoundationAttachmentMetadata> UploadAsync(
        string blobName,
        string fileName,
        string contentType,
        byte[] content,
        CancellationToken cancellationToken = default)
    {
        var client = container.GetBlobClient(blobName);

        await using var stream = new MemoryStream(content, writable: false);
        await client.UploadAsync(
            stream,
            new BlobUploadOptions
            {
                HttpHeaders = new BlobHttpHeaders { ContentType = contentType }
            },
            cancellationToken);

        return new FoundationAttachmentMetadata(
            blobName,
            fileName,
            contentType,
            content.LongLength);
    }

    public async Task<byte[]?> DownloadAsync(
        string blobName,
        CancellationToken cancellationToken = default)
    {
        var client = container.GetBlobClient(blobName);

        if (!(await client.ExistsAsync(cancellationToken)).Value)
            return null;

        var response = await client.DownloadContentAsync(cancellationToken);
        return response.Value.Content.ToArray();
    }

    public async Task DeleteIfExistsAsync(
        string blobName,
        CancellationToken cancellationToken = default)
    {
        await container
            .GetBlobClient(blobName)
            .DeleteIfExistsAsync(cancellationToken: cancellationToken);
    }

    public async Task<bool> CanConnectAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            return (await container.ExistsAsync(cancellationToken)).Value;
        }
        catch
        {
            return false;
        }
    }

    public async Task EnsureContainerAsync(CancellationToken cancellationToken = default)
    {
        await container.CreateIfNotExistsAsync(
            PublicAccessType.None,
            cancellationToken: cancellationToken);
    }
}
