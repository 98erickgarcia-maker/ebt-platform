using Ebt.Application.Security;

namespace Ebt.Infrastructure.Security;

public sealed class SyntheticIdentityCatalog : IEbtIdentityCatalog
{
    private static readonly EbtIdentityProfile[] Profiles =
    [
        new(
            Guid.Parse("11111111-aaaa-4111-8111-111111111111"),
            Guid.Parse("11111111-1111-4111-8111-111111111111"),
            "orbe",
            "admin.orbe@demo.invalid",
            "Camila Teste",
            EbtRole.Administrator,
            true),
        new(
            Guid.Parse("11111111-bbbb-4111-8111-111111111111"),
            Guid.Parse("11111111-1111-4111-8111-111111111111"),
            "orbe",
            "operador.orbe@demo.invalid",
            "Rafael QA",
            EbtRole.Operator,
            true),
        new(
            Guid.Parse("11111111-cccc-4111-8111-111111111111"),
            Guid.Parse("11111111-1111-4111-8111-111111111111"),
            "orbe",
            "consulta.orbe@demo.invalid",
            "Leitor A",
            EbtRole.ReadOnly,
            true),
        new(
            Guid.Parse("22222222-aaaa-4222-8222-222222222222"),
            Guid.Parse("22222222-2222-4222-8222-222222222222"),
            "nexo",
            "admin.nexo@demo.invalid",
            "Marina Teste",
            EbtRole.Administrator,
            true),
        new(
            Guid.Parse("22222222-bbbb-4222-8222-222222222222"),
            Guid.Parse("22222222-2222-4222-8222-222222222222"),
            "nexo",
            "operador.nexo@demo.invalid",
            "Diego QA",
            EbtRole.Operator,
            true),
        new(
            Guid.Parse("22222222-cccc-4222-8222-222222222222"),
            Guid.Parse("22222222-2222-4222-8222-222222222222"),
            "nexo",
            "consulta.nexo@demo.invalid",
            "Leitor B",
            EbtRole.ReadOnly,
            true),
        new(
            Guid.Parse("99999999-aaaa-4999-8999-999999999999"),
            null,
            null,
            "suporte@demo.invalid",
            "Suporte Técnico Demo",
            EbtRole.TechnicalSupport,
            true)
    ];

    public EbtIdentityProfile? FindByEmail(string email)
    {
        var normalized = email?.Trim();
        if (string.IsNullOrWhiteSpace(normalized))
            return null;

        return Profiles.FirstOrDefault(profile =>
            string.Equals(profile.Email, normalized, StringComparison.OrdinalIgnoreCase));
    }

    public EbtIdentityProfile? FindByUserId(Guid userId) =>
        Profiles.FirstOrDefault(profile => profile.UserId == userId);
}
