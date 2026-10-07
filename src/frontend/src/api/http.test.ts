import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, downloadFile, requestJson } from './http'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('cliente HTTP EBT', () => {
  it('trata 401 como expiração sem declarar sucesso', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: 'Não autorizado.', traceId: 'trace-401' }),
      {
        status: 401,
        headers: { 'content-type': 'application/problem+json' },
      },
    )))

    await expect(requestJson('/api/private')).rejects.toMatchObject({
      name: 'ApiError',
      status: 401,
      kind: 'unauthorized',
      traceId: 'trace-401',
    })
  })

  it('mantém o payload do chamador intacto quando a chamada falha', async () => {
    const payload = { title: 'Valor digitado', notes: 'Não perder este texto' }
    const snapshot = structuredClone(payload)

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ title: 'Falha controlada', traceId: 'trace-500' }),
      {
        status: 500,
        headers: { 'content-type': 'application/problem+json' },
      },
    )))

    await expect(requestJson('/api/fail', {
      method: 'POST',
      body: JSON.stringify(payload),
    })).rejects.toBeInstanceOf(ApiError)

    expect(payload).toEqual(snapshot)
  })

  it('rejeita download que retorna JSON em vez de arquivo', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: 'Arquivo indisponível.' }),
      {
        status: 200,
        headers: {
          'content-type': 'application/json',
          'x-trace-id': 'trace-download',
        },
      },
    )))

    await expect(downloadFile('/api/file')).rejects.toMatchObject({
      status: 200,
      kind: 'invalid-response',
      traceId: 'trace-download',
    })
  })

  it('retorna arquivo somente após resposta confirmada e não vazia', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      new Blob(['EBT QA'], { type: 'text/plain' }),
      {
        status: 200,
        headers: { 'content-type': 'text/plain' },
      },
    )))

    const file = await downloadFile('/api/file')
    expect(file.size).toBeGreaterThan(0)
    expect(file.type).toBe('text/plain')
  })
})
