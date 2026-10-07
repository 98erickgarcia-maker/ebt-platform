using Ebt.Application.Foundation;
using Ebt.Domain.Foundation;

namespace Ebt.Infrastructure.Foundation;

public sealed class SyntheticConsumerCatalog : IEbtConsumerCatalog
{
    private static readonly IReadOnlyList<ConsumerProfile> Consumers =
    [
        new(
            Guid.Parse("11111111-1111-4111-8111-111111111111"),
            "orbe",
            "Orbe Industrial Demo",
            "ebt-orange",
            [
                new(Guid.Parse("11111111-aaaa-4111-8111-111111111111"), "Camila Teste", "Administrator", true),
                new(Guid.Parse("11111111-bbbb-4111-8111-111111111111"), "Rafael QA", "Seller", true),
                new(Guid.Parse("11111111-cccc-4111-8111-111111111111"), "Leitor A", "ReadOnly", true),
            ]),
        new(
            Guid.Parse("22222222-2222-4222-8222-222222222222"),
            "nexo",
            "Nexo Serviços Demo",
            "ebt-orange",
            [
                new(Guid.Parse("22222222-aaaa-4222-8222-222222222222"), "Marina Teste", "Administrator", true),
                new(Guid.Parse("22222222-bbbb-4222-8222-222222222222"), "Diego QA", "Seller", true),
                new(Guid.Parse("22222222-cccc-4222-8222-222222222222"), "Leitor B", "ReadOnly", true),
            ])
    ];

    public IReadOnlyList<ConsumerProfile> GetAll() => Consumers;

    public ConsumerProfile? Find(string key) =>
        Consumers.FirstOrDefault(item => string.Equals(item.Key, key, StringComparison.OrdinalIgnoreCase));
}
