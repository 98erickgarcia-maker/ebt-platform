namespace Ebt.Foundation.Tests;

public sealed class QaFactAttribute : FactAttribute
{
    public QaFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("EBT_QA_E2E") != "1")
            Skip = "Requer fixture explícita SQL Server/Azurite de QA (EBT_QA_E2E=1).";
    }
}
