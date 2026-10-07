import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import {
  Bell,
  BriefcaseBusiness,
  CalendarDays,
  ChartNoAxesCombined,
  House,
  LayoutGrid,
  Menu,
  Search,
  Settings,
  Target,
  UserRound,
  Users,
  X,
} from 'lucide-react'
import { EbtBrand } from './EbtBrand'

function navClass({ isActive }: { isActive: boolean }) {
  return isActive ? 'nav-link nav-link--active' : 'nav-link'
}

export function EbtShell() {
  const [open, setOpen] = useState(false)

  return (
    <div className="app-shell">
      {open && <button className="sidebar-backdrop" aria-label="Fechar menu" onClick={() => setOpen(false)} />}
      <aside className={open ? 'sidebar sidebar--open' : 'sidebar'}>
        <div className="sidebar__brand">
          <EbtBrand />
          <button className="sidebar__close" type="button" aria-label="Fechar menu" onClick={() => setOpen(false)}><X size={18} /></button>
        </div>
        <nav aria-label="Navegação principal">
          <section className="nav-group">
            <h2>Relacionamento</h2>
            <NavLink className={navClass} to="/dashboard" onClick={() => setOpen(false)}><House /><span>Dashboard</span></NavLink>
            <NavLink className={navClass} to="/empresas" onClick={() => setOpen(false)}><BriefcaseBusiness /><span>Empresas</span></NavLink>
            <NavLink className={navClass} to="/contatos" onClick={() => setOpen(false)}><Users /><span>Contatos</span></NavLink>
            <NavLink className={navClass} to="/prospeccao" onClick={() => setOpen(false)}><Target /><span>Prospecção</span></NavLink>
            <NavLink className={navClass} to="/pipeline" onClick={() => setOpen(false)}><LayoutGrid /><span>Pipeline</span></NavLink>
            <NavLink className={navClass} to="/agenda" onClick={() => setOpen(false)}><CalendarDays /><span>Agenda</span></NavLink>
          </section>
          <section className="nav-group">
            <h2>Inteligência</h2>
            <NavLink className={navClass} to="/relatorios" onClick={() => setOpen(false)}><ChartNoAxesCombined /><span>Relatórios</span></NavLink>
          </section>
          <section className="nav-group">
            <h2>Configuração</h2>
            <button className="nav-link nav-link--disabled" type="button" disabled><Settings /><span>Configurações</span></button>
          </section>
        </nav>
        <footer className="sidebar__account">
          <span className="avatar"><UserRound size={17} /></span>
          <span><strong>Operador Demo</strong><small>Ambiente sintético</small></span>
        </footer>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <button className="topbar__menu" type="button" aria-label="Abrir menu" onClick={() => setOpen(true)}><Menu size={20} /></button>
          <button className="global-search" type="button" disabled title="A busca global será habilitada quando o contrato de busca estiver implementado">
            <Search size={17} />
            <span>Buscar empresas, contatos ou ações...</span>
            <kbd>Ctrl K</kbd>
          </button>
          <div className="topbar__actions">
            <button type="button" className="icon-button" disabled aria-label="Notificações em preparação"><Bell size={18} /></button>
            <div className="topbar__user"><span className="avatar">EB</span><span><strong>EBT Demo</strong><small>Connect</small></span></div>
          </div>
        </header>
        <main className="page-content"><Outlet /></main>
      </div>
    </div>
  )
}
