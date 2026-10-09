namespace Ebt.Platform.Api;

public static class DocumentSafety
{
    public static bool CanRelease(bool development, string scanState) => scanState == "clean" || development && scanState == "not_scanned";

    public static void RequireRelease(bool development, string scanState)
    {
        if (!CanRelease(development, scanState))
            throw new ApiFault(503, "document_scanner_unavailable", "Esta versão precisa de verificação de segurança antes de ser liberada.");
    }
}
