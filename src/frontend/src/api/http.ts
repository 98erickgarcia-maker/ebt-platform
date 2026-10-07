export type ApiErrorKind = 'unauthorized' | 'http' | 'invalid-response' | 'network'

type ProblemPayload = {
  title?: string
  detail?: string
  traceId?: string
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly traceId: string | null,
    public readonly kind: ApiErrorKind,
  ) {
    super(message)
    this.name = 'ApiError'
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

async function execute(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, init)
  } catch {
    throw new ApiError(
      'Não foi possível conectar ao serviço.',
      0,
      null,
      'network',
    )
  }
}

export async function requestJson<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<T> {
  const response = await execute(input, init)

  if (!response.ok) {
    throw await toApiError(response)
  }

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
}

export async function downloadFile(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Blob> {
  const response = await execute(input, init)

  if (!response.ok) {
    throw await toApiError(response)
  }

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
}
