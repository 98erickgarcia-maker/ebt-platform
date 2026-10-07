using Ebt.Domain.Foundation;

namespace Ebt.Application.Foundation;

public interface IEbtConsumerCatalog
{
    IReadOnlyList<ConsumerProfile> GetAll();
    ConsumerProfile? Find(string key);
}
