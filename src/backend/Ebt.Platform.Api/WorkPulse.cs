namespace Ebt.Platform.Api;

// Signals only after a durable commit; periodic polling recovers missed signals/restarts.
public sealed class WorkPulse
{
    readonly SemaphoreSlim pending = new(0, 1);
    public void Notify() { try { pending.Release(); } catch (SemaphoreFullException) { } }
    public Task<bool> Wait(CancellationToken ct) => pending.WaitAsync(TimeSpan.FromSeconds(15), ct);
}
