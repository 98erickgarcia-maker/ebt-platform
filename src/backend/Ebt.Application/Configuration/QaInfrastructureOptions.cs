namespace Ebt.Application.Configuration;

public sealed class QaInfrastructureOptions
{
    public const string SectionName = "Ebt:Qa";

    public bool Enabled { get; init; }
    public string EnvironmentName { get; init; } = string.Empty;
    public string DatabaseFile { get; init; } = string.Empty;
    public string StorageRoot { get; init; } = string.Empty;
}
