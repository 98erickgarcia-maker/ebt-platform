namespace Ebt.Application.Configuration;

public static class PrivateConfigurationGuard
{
    private const string MissingPrivateConfigurationMessage =
        "Configuração privada obrigatória não foi fornecida.";

    public static void Validate(EbtPlatformOptions options, Func<string, string?> readValue)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(readValue);

        if (!options.RequirePrivateConfiguration)
            return;

        if (options.RequiredPrivateConfigurationKeys.Length == 0)
            throw new InvalidOperationException(MissingPrivateConfigurationMessage);

        foreach (var key in options.RequiredPrivateConfigurationKeys)
        {
            if (string.IsNullOrWhiteSpace(key) || string.IsNullOrWhiteSpace(readValue(key)))
                throw new InvalidOperationException(MissingPrivateConfigurationMessage);
        }
    }
}
