using Ebt.Api;
using Ebt.Application.Configuration;
using Ebt.Infrastructure.Foundation;

namespace Ebt.Foundation.Tests;

public sealed class FoundationTests
{
    [Fact]
    public void Synthetic_consumers_are_distinct_and_reproducible()
    {
        var catalog = new SyntheticConsumerCatalog();
        var consumers = catalog.GetAll();

        Assert.Equal(2, consumers.Count);
        Assert.NotEqual(consumers[0].TenantId, consumers[1].TenantId);
        Assert.NotEqual(consumers[0].Key, consumers[1].Key);
        Assert.All(consumers, consumer => Assert.Equal("ebt-orange", consumer.BrandKey));
        Assert.All(consumers, consumer => Assert.All(consumer.Users, user => Assert.True(user.IsActive)));
    }

    [Fact]
    public void Missing_required_private_configuration_fails_with_safe_message()
    {
        var options = new EbtPlatformOptions
        {
            ProductName = "EBT Connect",
            PlatformName = "EBT Platform",
            EnvironmentName = "Production",
            DefaultConsumerKey = "orbe",
            RequirePrivateConfiguration = true,
            RequiredPrivateConfigurationKeys = ["EBT_DATA_CONNECTION"]
        };

        var error = Assert.Throws<InvalidOperationException>(() =>
            PrivateConfigurationGuard.Validate(options, _ => null));

        Assert.Equal("Configuração privada obrigatória não foi fornecida.", error.Message);
        Assert.DoesNotContain("EBT_DATA_CONNECTION", error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void Development_configuration_does_not_read_production_secret()
    {
        var reads = 0;
        var options = new EbtPlatformOptions
        {
            ProductName = "EBT Connect",
            PlatformName = "EBT Platform",
            EnvironmentName = "Development",
            DefaultConsumerKey = "orbe",
            RequirePrivateConfiguration = false,
            RequiredPrivateConfigurationKeys = []
        };

        PrivateConfigurationGuard.Validate(options, _ =>
        {
            reads++;
            return "should-not-be-read";
        });

        Assert.Equal(0, reads);
    }

    [Theory]
    [InlineData("Production", "ebt-qa-safe")]
    [InlineData("EbtQa_safe", "production")]
    [InlineData("CustomerDb", "ebt-qa-safe")]
    public void Qa_target_guard_rejects_non_qa_destinations(
        string databaseName,
        string containerName)
    {
        var options = new QaPersistenceOptions
        {
            Enabled = true,
            DatabaseName = databaseName,
            BlobContainerName = containerName
        };

        var error = Assert.Throws<InvalidOperationException>(() =>
            QaTargetGuard.ValidateTargets(options));

        Assert.Equal("Destino de persistência não autorizado para QA.", error.Message);
    }

    [Fact]
    public void Qa_private_configuration_failure_does_not_expose_variable_names()
    {
        var options = new QaPersistenceOptions
        {
            Enabled = true,
            DatabaseName = "EbtQa_Test",
            BlobContainerName = "ebt-qa-test",
            SqlPasswordEnvironmentVariable = "PRIVATE_SQL_NAME",
            BlobConnectionEnvironmentVariable = "PRIVATE_BLOB_NAME"
        };

        var error = Assert.Throws<InvalidOperationException>(() =>
            QaTargetGuard.ValidatePrivateConfiguration(options, _ => null));

        Assert.Equal(
            "Configuração privada de QA obrigatória não foi fornecida.",
            error.Message);
        Assert.DoesNotContain("PRIVATE_SQL_NAME", error.Message, StringComparison.Ordinal);
        Assert.DoesNotContain("PRIVATE_BLOB_NAME", error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void Trace_id_has_only_technical_identifier_content()
    {
        var traceId = SafeDiagnostics.CreateTraceId();

        Assert.Matches("^[a-f0-9]{32}$", traceId);
        Assert.DoesNotContain("orbe", traceId, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("@", traceId, StringComparison.Ordinal);
    }
}
