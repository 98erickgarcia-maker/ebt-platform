using System.Text.RegularExpressions;

namespace Ebt.Application.Configuration;

public static partial class QaTargetGuard
{
    private const string UnsafeTargetMessage = "Destino de persistência não autorizado para QA.";
    private const string MissingPrivateConfigurationMessage =
        "Configuração privada de QA obrigatória não foi fornecida.";

    [GeneratedRegex("^EbtQa_[A-Za-z0-9_]+$", RegexOptions.CultureInvariant)]
    private static partial Regex DatabasePattern();

    [GeneratedRegex("^ebt-qa-[a-z0-9-]+$", RegexOptions.CultureInvariant)]
    private static partial Regex ContainerPattern();

    public static void ValidateTargets(QaPersistenceOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);

        if (!options.Enabled)
            return;

        if (!DatabasePattern().IsMatch(options.DatabaseName)
            || options.DatabaseName.Contains("prod", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException(UnsafeTargetMessage);

        if (options.BlobContainerName.Length is < 3 or > 63
            || !ContainerPattern().IsMatch(options.BlobContainerName)
            || options.BlobContainerName.Contains("prod", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException(UnsafeTargetMessage);
    }

    public static void ValidatePrivateConfiguration(
        QaPersistenceOptions options,
        Func<string, string?> readValue)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(readValue);

        if (!options.Enabled)
            return;

        ValidateTargets(options);

        if (string.IsNullOrWhiteSpace(options.SqlPasswordEnvironmentVariable)
            || string.IsNullOrWhiteSpace(options.BlobConnectionEnvironmentVariable)
            || string.IsNullOrWhiteSpace(readValue(options.SqlPasswordEnvironmentVariable))
            || string.IsNullOrWhiteSpace(readValue(options.BlobConnectionEnvironmentVariable)))
            throw new InvalidOperationException(MissingPrivateConfigurationMessage);
    }
}
