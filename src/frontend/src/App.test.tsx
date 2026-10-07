import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import App from './App'

function renderRoute(path: string) {
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>)
}

describe('fundação visual EBT', () => {
  it('renderiza o EBT Connect sem marca de produto-fonte', () => {
    renderRoute('/dashboard')
    expect(screen.getByRole('heading', { name: 'Bom dia, EBT!' })).toBeVisible()
    expect(screen.getAllByLabelText('EBT Connect').length).toBeGreaterThan(0)
    expect(screen.queryByText(/CASST/i)).not.toBeInTheDocument()
  })

  it.each([
    ['/login', /Relacionamentos que geram resultados/i],
    ['/dashboard', 'Bom dia, EBT!'],
    ['/empresas', 'Empresas'],
    ['/empresas/orbe', 'Orbe Industrial'],
    ['/contatos', 'Contatos'],
    ['/prospeccao', 'Prospecção'],
    ['/pipeline', 'Pipeline de vendas'],
    ['/agenda', 'Agenda'],
    ['/relatorios', 'Relatórios'],
  ])('monta a rota base %s com identidade EBT', (path, heading) => {
    renderRoute(path)
    expect(screen.getByRole('heading', { name: heading })).toBeVisible()
    expect(screen.queryByText(/CASST/i)).not.toBeInTheDocument()
  })

  it('mantém as principais rotas no mesmo shell', () => {
    renderRoute('/empresas')
    expect(screen.getByRole('link', { name: /Contatos/ })).toHaveAttribute('href', '/contatos')
    expect(screen.getByRole('link', { name: /Pipeline/ })).toHaveAttribute('href', '/pipeline')
    expect(screen.getByRole('link', { name: /Agenda/ })).toHaveAttribute('href', '/agenda')
    expect(screen.getByRole('link', { name: /Relatórios/ })).toHaveAttribute('href', '/relatorios')
  })
})
