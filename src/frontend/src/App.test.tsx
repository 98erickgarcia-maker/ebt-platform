import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('fundação visual EBT', () => {
  it('renderiza o EBT Connect sem marca de produto-fonte', () => {
    render(<MemoryRouter initialEntries={['/dashboard']}><App /></MemoryRouter>)
    expect(screen.getByRole('heading', { name: 'Bom dia, EBT!' })).toBeVisible()
    expect(screen.getAllByLabelText('EBT Connect').length).toBeGreaterThan(0)
    expect(screen.queryByText(/CASST/i)).not.toBeInTheDocument()
  })

  it('mantém todas as rotas-base da referência visual', () => {
    render(<MemoryRouter initialEntries={['/empresas']}><App /></MemoryRouter>)
    expect(screen.getByRole('heading', { name: 'Empresas' })).toBeVisible()
    expect(screen.getByRole('link', { name: /Contatos/ })).toHaveAttribute('href', '/contatos')
    expect(screen.getByRole('link', { name: /Pipeline/ })).toHaveAttribute('href', '/pipeline')
    expect(screen.getByRole('link', { name: /Agenda/ })).toHaveAttribute('href', '/agenda')
    expect(screen.getByRole('link', { name: /Relatórios/ })).toHaveAttribute('href', '/relatorios')
  })
})
