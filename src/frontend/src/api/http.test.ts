import { describe, expect, it, vi } from 'vitest'
import { ApiError, downloadFile, requestJson } from './http'

describe('cliente HTTP EBT', () => {
  it('trata 401 sem transformar falha em sucesso', async () => {
    const fetcher = vi.fn(async () => new Response(
      JSON.stringify({ detail: 'internal detail that must not leak' }),
      {
        status: 401,
        headers: {
          'content-type': 'application/json',
          'x-trace-id': 'trace-401',
        },
      },
    ))

    await expect(requestJson('/private', undefined, fetcher)).rejects.toMatchObject({
      name: 'ApiError',
      status: 401,
      traceId: 'trace-401',
    })

    await expect(requestJson('/private', undefined, fetcher)).rejects.not.toThrow(
      /internal detail/i,
    )
  })

  it('mantém erro HTTP como erro confirmado', async () => {
    const fetcher = vi.fn(async () => new Response('falha', {
      status: 500,
      headers: { 'x-trace-id': 'trace-500' },
    }))

    await expect(requestJson('/save', { method: 'POST' }, fetcher)).rejects.toEqual(
      expect.objectContaining<ApiError>({
        status: 500,
        traceId: 'trace-500',
      }),
    )
  })

  it('recusa download com payload de erro disfarçado de sucesso', async () => {
    const fetcher = vi.fn(async () => new Response(
      JSON.stringify({ error: 'not-a-file' }),
      {
        status: 200,
        headers: {
          'content-type': 'application/json',
          'x-trace-id': 'trace-download',
        },
      },
    ))

    await expect(downloadFile('/download', undefined, fetcher)).rejects.toMatchObject({
      status: 200,
      traceId: 'trace-download',
      message: 'O download recebido é inválido.',
    })
  })

  it('retorna JSON somente após resposta confirmada', async () => {
    const fetcher = vi.fn(async () => new Response(
      JSON.stringify({ ok: true }),
      {
        status: 200,
        headers: { 'content-type': 'application/json' },
      },
    ))

    await expect(requestJson<{ ok: boolean }>('/ok', undefined, fetcher)).resolves.toEqual({ ok: true })
  })
})
