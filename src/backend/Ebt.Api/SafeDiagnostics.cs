using System.Diagnostics;

namespace Ebt.Api;

public static class SafeDiagnostics
{
    public const string TraceItemKey = "ebt-trace-id";

    public static string CreateTraceId() =>
        Activity.Current?.TraceId.ToString() is { Length: > 0 } trace
            ? trace
            : Guid.NewGuid().ToString("N");

    public static string GetTraceId(HttpContext context) =>
        context.Items.TryGetValue(TraceItemKey, out var value)
            && value is string traceId
            && !string.IsNullOrWhiteSpace(traceId)
                ? traceId
                : CreateTraceId();
}
