namespace Ebt.Application.Configuration;

public sealed class EbtPlatformOptions
{
    public const string SectionName = "Ebt";

    public string ProductName { get; init; } = string.Empty;
    public string PlatformName { get; init; } = string.Empty;
    public string EnvironmentName { get; init; } = string.Empty;
    public string DefaultConsumerKey { get; init; } = string.Empty;
    public bool SyntheticDataEnabled { get; init; }
    public bool RequirePrivateConfiguration { get; init; }
    public string[] RequiredPrivateConfigurationKeys { get; init; } = [];
}
