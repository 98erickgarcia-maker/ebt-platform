using Ebt.Application.Configuration;

namespace Ebt.Infrastructure.Foundation;

public static class QaInfrastructureGuard
{
    private const string InvalidTargetMessage =
        "Destino de QA inválido. Nenhum recurso foi inicializado.";

    public static void Validate(QaInfrastructureOptions options, string hostEnvironmentName)
    {
        ArgumentNullException.ThrowIfNull(options);

        if (!options.Enabled)
            return;

        if (string.Equals(hostEnvironmentName, "Production", StringComparison.OrdinalIgnoreCase)
            || !string.Equals(options.EnvironmentName, "QA", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException(InvalidTargetMessage);

        if (string.IsNullOrWhiteSpace(options.DatabaseFile)
            || string.IsNullOrWhiteSpace(options.StorageRoot))
            throw new InvalidOperationException(InvalidTargetMessage);

        var databasePath = Path.GetFullPath(options.DatabaseFile);
        var storagePath = Path.GetFullPath(options.StorageRoot);
        var combined = $"{databasePath}|{storagePath}";

        if (!databasePath.EndsWith(".qa.db", StringComparison.OrdinalIgnoreCase)
            || !combined.Contains("ebt-qa", StringComparison.OrdinalIgnoreCase)
            || combined.Contains("production", StringComparison.OrdinalIgnoreCase)
            || combined.Contains($"{Path.DirectorySeparatorChar}prod{Path.DirectorySeparatorChar}", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException(InvalidTargetMessage);
    }
}
