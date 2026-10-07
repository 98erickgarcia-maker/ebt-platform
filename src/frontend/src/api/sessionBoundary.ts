export type SessionIdentity = {
  userId: string
  tenantId: string | null
  tenantKey: string | null
  role: string
  displayName: string
  email: string
}

export class SessionChangedError extends Error {
  constructor() { super('A sessÃ£o mudou; a resposta anterior foi descartada.'); this.name = 'SessionChangedError' }
}

let generation = 0
let identity: SessionIdentity | null = null
const listeners = new Set<() => void>()
const requests = new Set<AbortController>()

export const sessionBoundary = {
  getSnapshot: () => generation,
  getIdentity: () => identity,
  subscribe(listener: () => void) { listeners.add(listener); return () => { listeners.delete(listener) } },
  invalidate() {
    identity = null
    generation++
    for (const request of requests) request.abort()
    requests.clear()
    for (const listener of listeners) listener()
  },
  replace(next: SessionIdentity | null) {
    const key = (value: SessionIdentity | null) => value
      ? JSON.stringify([value.tenantId, value.tenantKey, value.userId, value.role]) : null
    if (key(next) === key(identity)) return
    identity = next
    generation++
    for (const request of requests) request.abort()
    requests.clear()
    for (const listener of listeners) listener()
  },
  request(externalSignal?: AbortSignal | null) {
    const current = generation
    const controller = new AbortController()
    const abort = () => controller.abort()
    externalSignal?.addEventListener('abort', abort, { once: true })
    if (externalSignal?.aborted) controller.abort()
    requests.add(controller)
    return {
      signal: controller.signal,
      assertCurrent() { if (current !== generation) throw new SessionChangedError() },
      release() { requests.delete(controller); externalSignal?.removeEventListener('abort', abort) },
    }
  },
}
