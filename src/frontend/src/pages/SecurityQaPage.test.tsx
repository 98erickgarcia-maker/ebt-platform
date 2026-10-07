import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, it, vi } from 'vitest'
import { sessionBoundary } from '../api/sessionBoundary'
import { SecurityQaPage } from './SecurityQaPage'

afterEach(() => { sessionBoundary.invalidate(); vi.unstubAllGlobals() })

it('limpa a carteira no logout e ignora lista antiga após entrar na outra empresa', async () => {
  const user = userEvent.setup()
  let identity: string | null = null
  let oldResponse!: (response: Response) => void
  const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), { status, headers: { 'content-type': 'application/json' } })
  vi.stubGlobal('fetch', vi.fn().mockImplementation((path: string, init?: RequestInit) => {
    if (path === '/api/auth/qa-login') {
      identity = (JSON.parse(String(init?.body)) as { email: string }).email.includes('nexo') ? 'nexo' : 'orbe'
      return Promise.resolve(new Response(null, { status: 204 }))
    }
    if (path === '/api/auth/logout') { identity = null; return Promise.resolve(new Response(null, { status: 204 })) }
    if (path === '/api/auth/me') return Promise.resolve(identity ? json({
      userId: `user-${identity}`, tenantId: `tenant-${identity}`, tenantKey: identity,
      role: 'Administrator', displayName: `QA ${identity}`, email: `${identity}@demo.invalid`,
    }) : json({}, 401))
    if (path === '/api/foundation/records/' && identity === 'orbe') return new Promise(resolve => { oldResponse = resolve })
    if (path === '/api/foundation/records/' && identity === 'nexo') return Promise.resolve(json([{ id: 'nexo-record', title: 'Carteira Nexo', tenantKey: 'nexo' }]))
    return Promise.resolve(json({}, 401))
  }))
  render(<SecurityQaPage />)
  await waitFor(() => expect(screen.getByText('Sem carteira autenticada.')).toBeVisible())
  await user.type(screen.getByLabelText('Código QA'), 'synthetic-code')
  await user.click(screen.getByRole('button', { name: 'Entrar / trocar perfil' }))
  await waitFor(() => expect(oldResponse).toBeTypeOf('function'))
  await user.click(screen.getByRole('button', { name: 'Sair e limpar sessão' }))
  await waitFor(() => expect(screen.getByText('Sem carteira autenticada.')).toBeVisible())
  expect(screen.queryByRole('region', { name: 'Registros privados autorizados' })).not.toBeInTheDocument()
  await user.selectOptions(screen.getByLabelText('Perfil sintético'), 'admin.nexo@demo.invalid')
  await user.type(screen.getByLabelText('Código QA'), 'synthetic-code')
  await user.click(screen.getByRole('button', { name: 'Entrar / trocar perfil' }))
  await screen.findByText('Carteira Nexo · nexo')
  await act(async () => { oldResponse(json([{ id: 'orbe-record', title: 'Carteira anterior', tenantKey: 'orbe' }])); await Promise.resolve() })
  expect(screen.queryByText(/Carteira anterior/)).not.toBeInTheDocument()
  expect(screen.getByText('Carteira Nexo · nexo')).toBeVisible()
})
