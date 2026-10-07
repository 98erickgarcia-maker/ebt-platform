export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly traceId?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

type Fetcher = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>

function traceIdOf(response: Response) {
  return response.headers.get('x-trace-id') ?? undefined
}

function errorFor(response: Response) {
  const traceId = traceIdOf(response)

  if (response.status === 401) {
    return new ApiError('Sua sessão expirou. Entre novamente para continuar.', 401, traceId)
  }

  if (response.status === 403) {
    return new ApiError('Você não tem permissão para concluir esta ação.', 403, traceId)
  }

  if (response.status === 404) {
    return new ApiError('O recurso solicitado não foi encontrado.', 404, traceId)
  }

  return new ApiError('Não foi possível concluir a solicitação.', response.status, traceId)
}

export async function requestJson<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
  fetcher: Fetcher = fetch,
): Promise<T> {
  const response = await fetcher(input, init)

  if (!response.ok) {
    throw errorFor(response)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.toLowerCase().includes('application/json')) {
    throw new ApiError('A resposta recebida não possui o formato esperado.', response.status, traceIdOf(response))
  }

  return response.json() as Promise<T>
}

export async function downloadFile(
  input: RequestInfo | URL,
  init?: RequestInit,
  fetcher: Fetcher = fetch,
): Promise<Blob> {
  const response = await fetcher(input, init)

  if (!response.ok) {
    throw errorFor(response)
  }

  const contentType = (response.headers.get('content-type') ?? '').toLowerCase()
  if (
    !contentType
    || contentType.includes('application/json')
    || contentType.includes('text/html')
  ) {
    throw new ApiError('O download recebido é inválido.', response.status, traceIdOf(response))
  }

  const blob = await response.blob()
  if (blob.size === 0) {
    throw new ApiError('O download recebido está vazio.', response.status, traceIdOf(response))
  }

  return blob
}
