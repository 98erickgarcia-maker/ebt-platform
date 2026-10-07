using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Ebt.Application.Configuration;
using Ebt.Infrastructure.Foundation;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;

namespace Ebt.Foundation.Tests;

public sealed class QaIntegrationTests
{
    [Fact]
    public void Qa_guard_refuses_production_host()
    {
        var root = Path.Combine(Path.GetTempPath(), "ebt-qa-guard");
        var options = new QaInfrastructureOptions
        {
            Enabled = true,
            EnvironmentName = "QA",
            DatabaseFile = Path.Combine(root, "foundation.qa.db"),
            StorageRoot = Path.Combine(root, "blobs")
        };

        var error = Assert.Throws<InvalidOperationException>(() =>
            QaInfrastructureGuard.Validate(options, "Production"));

        Assert.Equal("Destino de QA inválido. Nenhum recurso foi inicializado.", error.Message);
        Assert.DoesNotContain(root, error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public async Task Qa_app_persists_and_reloads_metadata_and_binary_in_separate_targets()
    {
        var root = Path.Combine(Path.GetTempPath(), $"ebt-qa-{Guid.NewGuid():N}");
        var databaseFile = Path.Combine(root, "foundation.qa.db");
        var storageRoot = Path.Combine(root, "blobs");

        try
        {
            await using var factory = new WebApplicationFactory<Program>()
                .WithWebHostBuilder(builder =>
                {
                    builder.UseEnvironment("QA");
                    builder.ConfigureAppConfiguration((_, configuration) =>
                    {
                        configuration.AddInMemoryCollection(new Dictionary<string, string?>
                        {
                            ["Ebt:EnvironmentName"] = "QA",
                            ["Ebt:SyntheticDataEnabled"] = "true",
                            ["Ebt:Qa:Enabled"] = "true",
                            ["Ebt:Qa:EnvironmentName"] = "QA",
                            ["Ebt:Qa:DatabaseFile"] = databaseFile,
                            ["Ebt:Qa:StorageRoot"] = storageRoot
                        });
                    });
                });

            using var client = factory.CreateClient();

            var health = await client.GetAsync("/health");
            Assert.Equal(HttpStatusCode.OK, health.StatusCode);
            var healthBody = await health.Content.ReadAsStringAsync();
            Assert.Contains("\"qaDatabase\":\"healthy\"", healthBody, StringComparison.Ordinal);
            Assert.Contains("\"qaStorage\":\"healthy\"", healthBody, StringComparison.Ordinal);
            Assert.DoesNotContain(databaseFile, healthBody, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(storageRoot, healthBody, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("demo.invalid", healthBody, StringComparison.OrdinalIgnoreCase);
            Assert.True(health.Headers.TryGetValues("X-Trace-Id", out var traceHeaders));
            Assert.False(string.IsNullOrWhiteSpace(traceHeaders.Single()));

            var create = await client.PostAsJsonAsync("/api/foundation/qa/probes", new
            {
                consumerKey = "orbe",
                fileName = "g1-probe.txt",
                content = "persistencia-g1-ebt"
            });

            Assert.Equal(HttpStatusCode.Created, create.StatusCode);
            using var createdJson = JsonDocument.Parse(await create.Content.ReadAsStringAsync());
            var id = createdJson.RootElement.GetProperty("id").GetGuid();
            var hash = createdJson.RootElement.GetProperty("sha256").GetString();

            Assert.NotEqual(Guid.Empty, id);
            Assert.False(string.IsNullOrWhiteSpace(hash));

            var read = await client.GetAsync($"/api/foundation/qa/probes/{id}");
            Assert.Equal(HttpStatusCode.OK, read.StatusCode);

            using var readJson = JsonDocument.Parse(await read.Content.ReadAsStringAsync());
            var contentBase64 = readJson.RootElement.GetProperty("contentBase64").GetString();
            var content = Encoding.UTF8.GetString(Convert.FromBase64String(contentBase64!));

            Assert.Equal("persistencia-g1-ebt", content);
            Assert.Equal(hash, readJson.RootElement.GetProperty("sha256").GetString());

            Assert.True(File.Exists(databaseFile));
            Assert.True(Directory.Exists(storageRoot));
            Assert.Single(Directory.GetFiles(storageRoot, "*.bin"));
            Assert.NotEqual(
                Path.GetFullPath(databaseFile),
                Path.GetFullPath(Directory.GetFiles(storageRoot, "*.bin").Single()));
        }
        finally
        {
            if (Directory.Exists(root))
                Directory.Delete(root, recursive: true);
        }
    }
}
