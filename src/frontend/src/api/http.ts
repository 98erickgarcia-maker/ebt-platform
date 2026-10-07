import { sessionBoundary } from './sessionBoundary'

export type ApiErrorKind = 'unauthorized' | 'http' | 'invalid-response' | 'network'

type ProblemPayload = {
  title?: string
  detail?: string
  traceId?: string
}

export class ApiError extends Error {
  readonly status: number
  readonly traceId: string | null
  readonly kind: ApiErrorKind

  constructor(
    message: string,
    status: number,
    traceId: string | null,
    kind: ApiErrorKind,
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.traceId = traceId
    this.kind = kind
  }
}

async function toApiError(response: Response): Promise<ApiError> {
  let payload: ProblemPayload | null = null

  try {
    if ((response.headers.get('content-type') ?? '').includes('json')) {
      payload = await response.clone().json() as ProblemPayload
    }
  } catch {
    payload = null
  }

  const traceId =
    payload?.traceId
    ?? response.headers.get('x-trace-id')
    ?? null

  if (response.status === 401) {
    return new ApiError(
      'Sua sessão expirou ou não está autorizada.',
      response.status,
      traceId,
      'unauthorized',
    )
  }

  return new ApiError(
    payload?.detail || payload?.title || 'A operação não pôde ser concluída.',
    response.status,
    traceId,
    'http',
  )
}

async function execute<T>(input: RequestInfo | URL, init: RequestInit | undefined, read: (response: Response) => Promise<T>): Promise<T> {
  const request = sessionBoundary.request(init?.signal ?? (input instanceof Request ? input.signal : undefined))
  try {
    let response: Response
    try { response = await fetch(input, { ...init, signal: request.signal, cache: 'no-store', credentials: 'same-origin' }) }
    catch {
      request.assertCurrent()
      throw new ApiError('Não foi possível conectar ao serviço.', 0, null, 'network')
    }
    request.assertCurrent()
    if (!response.ok) {
      const error = await toApiError(response)
      request.assertCurrent() // an old 401 must not erase a newer identity
      if (response.status === 401) sessionBoundary.invalidate()
      throw error
    }
    const value = await read(response)
    request.assertCurrent() // includes bodies that finished after logout/profile change
    return value
  } finally { request.release() }
}

export async function requestJson<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<T> {
  return execute(input, init, async response => {
  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('application/json')) {
    throw new ApiError(
      'O serviço retornou uma resposta inválida.',
      response.status,
      response.headers.get('x-trace-id'),
      'invalid-response',
    )
  }

  return await response.json() as T
  })
}

export async function downloadFile(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Blob> {
  return execute(input, init, async response => {
  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType || contentType.includes('json') || contentType.includes('problem')) {
    throw new ApiError(
      'O serviço não retornou um arquivo válido.',
      response.status,
      response.headers.get('x-trace-id'),
      'invalid-response',
    )
  }

  const blob = await response.blob()
  if (blob.size === 0) {
    throw new ApiError(
      'O arquivo retornado está vazio.',
      response.status,
      response.headers.get('x-trace-id'),
      'invalid-response',
    )
  }

  return blob
  })
}
