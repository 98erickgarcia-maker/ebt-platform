import { ApiError } from './http'
import { sessionBoundary, SessionChangedError, type SessionIdentity } from './sessionBoundary'

let authQueue: Promise<unknown> = Promise.resolve()
let latestOperation = 0

async function authFetch(path: string, init?: RequestInit) {
  // Do not abort cookie mutations: wait for one operation to finish before the next.
  const response = await fetch(path, { ...init, credentials: 'same-origin', cache: 'no-store' })
  if (!response.ok && response.status !== 401) throw new ApiError(
    'A operação de sessão não pôde ser concluída.', response.status, response.headers.get('x-trace-id'), 'http')
  return response
}

function authOperation(task: () => Promise<SessionIdentity | null>): Promise<SessionIdentity | null> {
  const operation = ++latestOperation
  sessionBoundary.invalidate() // clear private state immediately, including queued logout
  const result = authQueue.then(async () => {
    const identity = await task()
    if (operation !== latestOperation) throw new SessionChangedError()
    sessionBoundary.replace(identity)
    return identity
  })
  authQueue = result.catch(() => undefined)
  return result
}

async function me(): Promise<SessionIdentity | null> {
  const response = await authFetch('/api/auth/me')
  if (response.status === 401) return null
  const identity = await response.json() as SessionIdentity
  if (!identity || typeof identity.userId !== 'string' || typeof identity.role !== 'string'
    || !(identity.tenantId === null || typeof identity.tenantId === 'string')
    || !(identity.tenantKey === null || typeof identity.tenantKey === 'string'))
    throw new Error('Resposta de identidade inválida.')
  return identity
}

export function refreshSession() { return authOperation(me) }

export function signInQa(email: string, code: string) {
  return authOperation(async () => {
    const response = await authFetch('/api/auth/qa-login', {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ email, code }),
    })
    if (response.status === 401) throw new ApiError('Acesso QA não autorizado.', 401, null, 'unauthorized')
    const identity = await me()
    if (!identity) throw new ApiError('Sessão não confirmada pelo servidor.', 401, null, 'unauthorized')
    return identity
  })
}

export function signOut() {
  return authOperation(async () => { await authFetch('/api/auth/logout', { method: 'POST' }); return null })
}
