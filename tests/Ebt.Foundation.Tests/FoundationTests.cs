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
}
