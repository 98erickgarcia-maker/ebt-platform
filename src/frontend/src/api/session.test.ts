import { afterEach, describe, expect, it, vi } from 'vitest'
import { downloadFile, requestJson } from './http'
import { refreshSession, signInQa, signOut } from './session'
import { sessionBoundary, type SessionIdentity } from './sessionBoundary'

const orbe: SessionIdentity = { userId: 'user-a', tenantId: 'tenant-a', tenantKey: 'orbe', role: 'Administrator', displayName: 'QA A', email: 'a@demo.invalid' }
const nexo: SessionIdentity = { ...orbe, userId: 'user-b', tenantId: 'tenant-b', tenantKey: 'nexo' }
const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), { status, headers: { 'content-type': 'application/json' } })

afterEach(() => { sessionBoundary.invalidate(); vi.unstubAllGlobals() })

describe('isolamento de geração de sessão', () => {
  it.each([nexo, { ...orbe, role: 'Operator' }, { ...orbe, userId: 'another-user' }])('descarta resposta anterior após trocar tenant, perfil ou usuário', async next => {
    sessionBoundary.replace(orbe)
    let complete!: (response: Response) => void
    const fetchMock = vi.fn().mockImplementation(() => new Promise<Response>(resolve => { complete = resolve }))
    vi.stubGlobal('fetch', fetchMock)
    const previous = requestJson('/api/foundation/records/')
    const assertion = expect(previous).rejects.toMatchObject({ name: 'SessionChangedError' })
    sessionBoundary.replace(next)
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true)
    complete(json([{ title: 'Dados anteriores' }])) // intentionally ignore AbortSignal, as a late response might
    await assertion
    expect(sessionBoundary.getIdentity()).toEqual(next)
  })

  it('descarta corpo que termina depois do logout', async () => {
    sessionBoundary.replace(orbe)
    let complete!: (value: unknown) => void
    const response = json({})
    vi.spyOn(response, 'json').mockImplementation(() => new Promise(resolve => { complete = resolve }))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response))
    const pending = requestJson('/api/foundation/records/')
    const assertion = expect(pending).rejects.toMatchObject({ name: 'SessionChangedError' })
    await vi.waitFor(() => expect(complete).toBeTypeOf('function'))
    sessionBoundary.invalidate()
    complete({ title: 'Anterior' })
    await assertion
    expect(sessionBoundary.getIdentity()).toBeNull()
  })

  it('um 401 antigo não apaga a identidade nova', async () => {
    sessionBoundary.replace(orbe)
    let complete!: (response: Response) => void
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => new Promise(resolve => { complete = resolve })))
    const pending = requestJson('/api/foundation/records/')
    const assertion = expect(pending).rejects.toMatchObject({ name: 'SessionChangedError' })
    sessionBoundary.replace(nexo)
    complete(json({}, 401))
    await assertion
    expect(sessionBoundary.getIdentity()).toEqual(nexo)
  })

  it('401 atual limpa a identidade', async () => {
    sessionBoundary.replace(orbe)
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(json({}, 401)))
    await expect(requestJson('/api/foundation/records/')).rejects.toMatchObject({ kind: 'unauthorized' })
    expect(sessionBoundary.getIdentity()).toBeNull()
  })

  it('download antigo também é descartado', async () => {
    let complete!: (response: Response) => void
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => new Promise(resolve => { complete = resolve })))
    const pending = downloadFile('/api/foundation/records/file')
    const assertion = expect(pending).rejects.toMatchObject({ name: 'SessionChangedError' })
    sessionBoundary.invalidate()
    complete(new Response('EBT QA', { headers: { 'content-type': 'text/plain' } }))
    await assertion
  })

  it('confirma identidade no servidor depois de login e limpa antes de logout', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(json(orbe))
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
    vi.stubGlobal('fetch', fetchMock)
    await signInQa('admin.orbe@demo.invalid', 'synthetic-code')
    expect(sessionBoundary.getIdentity()).toEqual(orbe)
    const logout = signOut()
    expect(sessionBoundary.getIdentity()).toBeNull()
    await logout
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual(['/api/auth/qa-login', '/api/auth/me', '/api/auth/logout'])
  })

  it('serializa mudança de cookie e logout sem publicar identidade ultrapassada', async () => {
    let complete!: (response: Response) => void
    const fetchMock = vi.fn()
      .mockImplementationOnce(() => new Promise<Response>(resolve => { complete = resolve }))
      .mockResolvedValueOnce(json(orbe))
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
    vi.stubGlobal('fetch', fetchMock)
    const login = signInQa('admin.orbe@demo.invalid', 'synthetic-code')
    const assertion = expect(login).rejects.toMatchObject({ name: 'SessionChangedError' })
    await vi.waitFor(() => expect(complete).toBeTypeOf('function'))
    const logout = signOut()
    expect(fetchMock).toHaveBeenCalledTimes(1)
    complete(new Response(null, { status: 204 }))
    await assertion
    await logout
    expect(sessionBoundary.getIdentity()).toBeNull()
    expect(fetchMock.mock.calls.at(-1)?.[0]).toBe('/api/auth/logout')
  })

  it('refresh anônimo não cria identidade', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(json({}, 401)))
    await refreshSession()
    expect(sessionBoundary.getIdentity()).toBeNull()
  })

  it('refresh automático não descarta logout enfileirado', async () => {
    sessionBoundary.replace(orbe)
    let complete!: (response: Response) => void
    const fetchMock = vi.fn()
      .mockImplementationOnce(() => new Promise<Response>(resolve => { complete = resolve }))
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(json({}, 401))
    vi.stubGlobal('fetch', fetchMock)
    const initial = refreshSession()
    const stale = expect(initial).rejects.toMatchObject({ name: 'SessionChangedError' })
    await vi.waitFor(() => expect(complete).toBeTypeOf('function'))
    const logout = signOut()
    const superseded = expect(logout).rejects.toMatchObject({ name: 'SessionChangedError' })
    const refresh = refreshSession()
    complete(json(orbe))
    await stale
    await superseded
    await refresh
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual(['/api/auth/me', '/api/auth/logout', '/api/auth/me'])
    expect(sessionBoundary.getIdentity()).toBeNull()
  })
})
