import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowUpRight,
  BriefcaseBusiness,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  GripVertical,
  Mail,
  MapPin,
  MoreVertical,
  Phone,
  Plus,
  Target,
  Users,
} from 'lucide-react'
import { EbtBrand } from '../components/EbtBrand'
import { KpiCard, PageHeader, StatusBadge } from '../components/ui'
import { agendaEvents, companies, contacts, leads, pipeline, timeline, type CompanyStatus } from '../data/synthetic'

function companyTone(status: CompanyStatus): 'orange' | 'red' | 'green' | 'violet' | 'blue' | 'neutral' {
  if (status === 'Em negociação') return 'orange'
  if (status === 'Alta prioridade') return 'red'
  if (status === 'Follow-up') return 'green'
  if (status === 'Proposta') return 'violet'
  if (status === 'Lead') return 'blue'
  return 'neutral'
}

function leadTone(status: string): 'orange' | 'green' | 'red' | 'blue' | 'neutral' {
  if (status === 'Qualificado') return 'green'
  if (status === 'Follow-up') return 'red'
  if (status === 'Em contato') return 'orange'
  if (status === 'Novo') return 'blue'
  return 'neutral'
}

export function LoginPage() {
  return (
    <main className="login-page">
      <section className="login-story">
        <EbtBrand />
        <div className="login-story__content">
          <p className="eyebrow">EBT Connect</p>
          <h1>Relacionamentos que geram <span>resultados.</span></h1>
          <p>Organize empresas, contatos, prospecção e próximas ações em um só lugar.</p>
          <ul>
            <li><Target size={17} />Mais oportunidades</li>
            <li><BriefcaseBusiness size={17} />Processos organizados</li>
            <li><ArrowUpRight size={17} />Visibilidade em tempo real</li>
            <li><CheckCircle2 size={17} />Resultados previsíveis</li>
          </ul>
        </div>
        <small>EBT Enterprise · fundação sintética da EBT Platform.</small>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <p className="eyebrow">Bem-vindo de volta</p>
          <h2>Acesse sua conta</h2>
          <p>Autenticação real entra no pacote de segurança. Este acesso abre somente a demonstração sintética.</p>
          <label>E-mail<input type="email" value="demo@ebt.invalid" readOnly /></label>
          <label>Senha<input type="password" value="demonstracao" readOnly /></label>
          <Link className="primary-button" to="/dashboard">Entrar no ambiente demo <ChevronRight size={17} /></Link>
          <div className="login-note">Nenhuma credencial real é armazenada nesta fundação.</div>
        </div>
      </section>
    </main>
  )
}

export function DashboardPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Bom dia, EBT!" description="Aqui está o que precisa da sua atenção no ambiente sintético." />
      <div className="kpi-grid">
        <KpiCard label="Empresas" value={String(companies.length)} trend="+12% referência" to="/empresas" icon={<BriefcaseBusiness size={18} />} />
        <KpiCard label="Contatos" value={String(contacts.length)} trend="+8% referência" to="/contatos" icon={<Users size={18} />} />
        <KpiCard label="Leads" value={String(leads.length)} trend="+20% referência" to="/prospeccao" icon={<Target size={18} />} />
        <KpiCard label="Pipeline" value="R$ 1,55 mi" trend="+15% referência" to="/pipeline" icon={<BriefcaseBusiness size={18} />} />
      </div>

      <div className="dashboard-grid">
        <article className="panel">
          <header className="panel__header"><div><span className="eyebrow">Hoje</span><h2>Próximas ações</h2></div><Link to="/agenda">Ver agenda <ChevronRight size={15} /></Link></header>
          <div className="action-list">
            {agendaEvents.slice(0, 4).map((event) => (
              <div className="action-row" key={event.id}>
                <time>{event.time.split(' - ')[0]}</time>
                <span className={`event-dot event-dot--${event.tone}`} />
                <div><strong>{event.title}</strong><small>{event.company}</small></div>
                <StatusBadge tone={event.state === 'Atrasado' ? 'red' : event.state === 'Concluído' ? 'green' : 'orange'}>{event.state}</StatusBadge>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <header className="panel__header"><div><span className="eyebrow">Funil</span><h2>Pipeline de vendas</h2></div><Link to="/pipeline">Abrir <ChevronRight size={15} /></Link></header>
          <div className="funnel-bars">
            {[
              ['Lead', 100, '184'],
              ['Contato', 72, '76'],
              ['Proposta', 46, '32'],
              ['Negociação', 28, '18'],
              ['Fechada', 18, '11'],
            ].map(([label, size, value]) => (
              <div className="funnel-bar" key={label}>
                <span><strong>{value}</strong><small>{label}</small></span>
                <div><i style={{ width: `${size}%` }} /></div>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  )
}

export function CompaniesPage() {
  const [search, setSearch] = useState('')
  const filtered = useMemo(
    () => companies.filter((company) => company.name.toLocaleLowerCase('pt-BR').includes(search.trim().toLocaleLowerCase('pt-BR'))),
    [search],
  )

  return (
    <section className="page-stack">
      <PageHeader
        title="Empresas"
        description="Gerencie empresas e organizações do relacionamento."
        action={<button type="button" className="primary-button" disabled title="Criação entra no pacote funcional do CRM"><Plus size={17} />Nova empresa</button>}
      />
      <div className="filter-bar">
        <label className="search-field">Buscar empresa<input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Nome da empresa..." /></label>
        <button type="button" disabled>Segmento</button>
        <button type="button" disabled>Status</button>
        <button type="button" disabled>Cidade</button>
      </div>
      <div className="table-card">
        <table>
          <thead><tr><th>Empresa</th><th>Segmento</th><th>Cidade</th><th>Status</th><th>Última interação</th><th>Próxima ação</th><th><span className="sr-only">Ações</span></th></tr></thead>
          <tbody>
            {filtered.map((company) => (
              <tr key={company.id}>
                <td><Link className="company-link" to={`/empresas/${company.id}`}><span className="company-mark">{company.name.slice(0, 1)}</span><strong>{company.name}</strong></Link></td>
                <td>{company.segment}</td>
                <td>{company.city}</td>
                <td><StatusBadge tone={companyTone(company.status)}>{company.status}</StatusBadge></td>
                <td>{company.lastInteraction}</td>
                <td><span className="next-action-dot" />{company.nextAction}</td>
                <td><button className="row-action" type="button" disabled aria-label={`Ações de ${company.name}`}><MoreVertical size={16} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div className="empty-state">Nenhuma empresa sintética corresponde à busca.</div>}
      </div>
    </section>
  )
}

export function CompanyDetailPage() {
  const { companyId } = useParams()
  const company = companies.find((item) => item.id === companyId) ?? companies[0]

  return (
    <section className="page-stack">
      <div className="detail-heading">
        <div className="company-identity"><span className="company-mark company-mark--large">{company.name.slice(0, 1)}</span><div><p className="eyebrow">Empresa</p><h1>{company.name}</h1><p><MapPin size={13} />{company.city} · {company.segment}</p></div></div>
        <StatusBadge tone={companyTone(company.status)}>{company.status}</StatusBadge>
      </div>
      <nav className="tabs" aria-label="Seções da empresa"><button className="active" type="button">Visão geral</button><button type="button" disabled>Contatos</button><button type="button" disabled>Oportunidades</button><button type="button" disabled>Interações</button><button type="button" disabled>Documentos</button><button type="button" disabled>Notas</button></nav>

      <div className="company-detail-grid">
        <div className="company-detail-main">
          <article className="panel detail-card">
            <header><h2>Informações</h2></header>
            <dl className="detail-list">
              <div><dt>Nome</dt><dd>{company.name}</dd></div>
              <div><dt>Segmento</dt><dd>{company.segment}</dd></div>
              <div><dt>Cidade</dt><dd>{company.city}</dd></div>
              <div><dt>Ambiente</dt><dd>Sintético · sem dado real</dd></div>
            </dl>
          </article>
          <article className="panel detail-card next-action-card">
            <header><h2>Próxima ação</h2><Clock3 size={18} /></header>
            <strong>Reunião de apresentação</strong>
            <p>08/10/2026 às 14:00 · responsável sintético</p>
            <button type="button" className="primary-button" disabled>Iniciar reunião</button>
          </article>
          <article className="panel detail-card">
            <header><h2>Status e prioridade</h2></header>
            <div className="status-row"><div><small>Status</small><StatusBadge tone={companyTone(company.status)}>{company.status}</StatusBadge></div><div><small>Prioridade</small><StatusBadge tone="red">Alta</StatusBadge></div></div>
          </article>
          <article className="panel detail-card detail-card--wide">
            <header><h2>Resumo</h2></header>
            <p>Registro fictício criado exclusivamente para validar layout, navegação e isolamento futuro da EBT Platform.</p>
          </article>
        </div>
        <aside className="panel timeline-card">
          <header className="panel__header"><div><span className="eyebrow">Relacionamento</span><h2>Linha do tempo</h2></div></header>
          <ol className="timeline">
            {timeline.map((item) => (
              <li key={item.id}><span className="timeline__dot" /><div><time>{item.time}</time><strong>{item.title}</strong><p>{item.type} · {item.detail}</p></div></li>
            ))}
          </ol>
        </aside>
      </div>
    </section>
  )
}

export function ContactsPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Contatos" description="Todos os contatos do ambiente sintético." action={<button className="primary-button" type="button" disabled><Plus size={17} />Novo contato</button>} />
      <div className="filter-bar"><label className="search-field">Busca<input placeholder="Buscar contatos..." disabled /></label><button type="button" disabled>Empresa</button><button type="button" disabled>Cargo</button><button type="button" disabled>Status</button></div>
      <div className="table-card">
        <table>
          <thead><tr><th>Contato</th><th>Empresa</th><th>Cargo</th><th>Telefone</th><th>Status</th><th>Última interação</th></tr></thead>
          <tbody>{contacts.map((contact) => <tr key={contact.id}><td><span className="person-cell"><span className="avatar">{contact.name.split(' ').map((part) => part[0]).join('').slice(0, 2)}</span><span><strong>{contact.name}</strong><small>{contact.email}</small></span></span></td><td>{contact.company}</td><td>{contact.role}</td><td>{contact.phone}</td><td><StatusBadge tone={contact.status === 'Ativo' ? 'green' : contact.status === 'Follow-up' ? 'red' : 'blue'}>{contact.status}</StatusBadge></td><td>{contact.lastInteraction}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  )
}

export function ProspectingPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Prospecção" description="Leads e oportunidades de entrada no relacionamento." action={<button className="primary-button" type="button" disabled><Plus size={17} />Novo lead</button>} />
      <div className="filter-bar"><label className="search-field">Busca<input placeholder="Buscar leads..." disabled /></label><button type="button" disabled>Origem</button><button type="button" disabled>Interesse</button><button type="button" disabled>Status</button></div>
      <div className="table-card">
        <table>
          <thead><tr><th>Empresa</th><th>Contato</th><th>Origem</th><th>Score</th><th>Interesse</th><th>Status</th><th>Data</th></tr></thead>
          <tbody>{leads.map((lead) => <tr key={lead.id}><td><strong>{lead.company}</strong></td><td>{lead.contact}</td><td>{lead.origin}</td><td><strong className="score">{lead.score}</strong></td><td><StatusBadge tone={lead.interest === 'Alto' ? 'green' : lead.interest === 'Médio' ? 'orange' : 'neutral'}>{lead.interest}</StatusBadge></td><td><StatusBadge tone={leadTone(lead.status)}>{lead.status}</StatusBadge></td><td>{lead.date}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  )
}

export function PipelinePage() {
  return (
    <section className="page-stack page-stack--wide">
      <PageHeader title="Pipeline de vendas" description="Até cinco etapas fixas no primeiro recorte funcional." action={<button className="primary-button" type="button" disabled><Plus size={17} />Nova oportunidade</button>} />
      <div className="filter-bar filter-bar--compact"><button type="button" disabled>Funil comercial</button><button type="button" disabled>Todos os segmentos</button><button type="button" disabled>Todos os responsáveis</button></div>
      <div className="kanban">
        {pipeline.map((column) => (
          <section className="kanban-column" key={column.stage}>
            <header><div><strong>{column.stage}</strong><small>{column.total} · {column.cards.length}</small></div><GripVertical size={16} /></header>
            <div className="kanban-cards">
              {column.cards.map((card) => (
                <article className="kanban-card" key={card.id}>
                  <div><strong>{card.company}</strong><StatusBadge tone={card.priority === 'Alta' ? 'red' : card.priority === 'Média' ? 'orange' : 'blue'}>{card.priority}</StatusBadge></div>
                  <p>{card.value}</p>
                  <small>Card sintético · histórico entra com a regra funcional</small>
                </article>
              ))}
            </div>
            <button type="button" className="add-card" disabled><Plus size={14} />Adicionar</button>
          </section>
        ))}
      </div>
    </section>
  )
}

export function AgendaPage() {
  const days = ['Seg 07', 'Ter 08', 'Qua 09', 'Qui 10', 'Sex 11']
  return (
    <section className="page-stack page-stack--wide">
      <PageHeader title="Agenda" description="Compromissos e próximas ações com estados explícitos." action={<button className="primary-button" type="button" disabled><Plus size={17} />Novo compromisso</button>} />
      <div className="calendar-toolbar"><button type="button" disabled>Hoje</button><strong>Outubro 2026</strong><div><button type="button" disabled>Dia</button><button type="button" className="active" disabled>Semana</button><button type="button" disabled>Mês</button></div></div>
      <div className="calendar-card">
        <div className="calendar-head"><span /><>{days.map((day) => <strong key={day}>{day}</strong>)}</></div>
        <div className="calendar-body">
          <div className="calendar-times">{['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00'].map((time) => <span key={time}>{time}</span>)}</div>
          <div className="calendar-grid">
            {days.map((day) => <div className="calendar-day" key={day} />)}
            {agendaEvents.map((event) => (
              <article className={`calendar-event calendar-event--${event.tone}`} key={event.id} style={{ gridColumn: event.day, gridRow: `${Math.round(event.start * 2) + 1} / span ${Math.max(2, Math.round(event.duration * 2))}` }}>
                <strong>{event.title}</strong><span>{event.company}</span><small>{event.time}</small>
              </article>
            ))}
          </div>
        </div>
      </div>
      <div className="calendar-legend"><span><i className="legend-dot legend-dot--orange" />Próximo</span><span><i className="legend-dot legend-dot--green" />Concluído</span><span><i className="legend-dot legend-dot--red" />Atrasado</span></div>
    </section>
  )
}

export function ReportsPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Relatórios" description="Leitura gerencial demonstrativa; os números só serão oficiais quando vierem dos contratos transacionais." />
      <div className="tabs tabs--reports"><button className="active" type="button">Visão geral</button><button type="button" disabled>Vendas</button><button type="button" disabled>Prospecção</button><button type="button" disabled>Atividades</button></div>
      <div className="kpi-grid">
        <div className="metric-card"><FileText size={18} /><span><small>Novos leads</small><strong>48</strong><em>+12%</em></span></div>
        <div className="metric-card"><CalendarDays size={18} /><span><small>Reuniões</small><strong>23</strong><em>+8%</em></span></div>
        <div className="metric-card"><Mail size={18} /><span><small>Propostas</small><strong>12</strong><em>+20%</em></span></div>
        <div className="metric-card"><Phone size={18} /><span><small>Interações</small><strong>184</strong><em>+15%</em></span></div>
      </div>
      <div className="reports-grid">
        <article className="panel chart-card"><header><h2>Leads por segmento</h2></header><div className="donut-wrap"><div className="donut"><span><strong>48</strong><small>Leads</small></span></div><ul><li><i className="c1" />Indústria <strong>28%</strong></li><li><i className="c2" />Serviços <strong>22%</strong></li><li><i className="c3" />Tecnologia <strong>20%</strong></li><li><i className="c4" />Logística <strong>18%</strong></li><li><i className="c5" />Outros <strong>12%</strong></li></ul></div></article>
        <article className="panel chart-card"><header><h2>Evolução de relacionamento</h2></header><div className="line-chart"><span className="line-chart__line" /><span className="line-chart__point p1" /><span className="line-chart__point p2" /><span className="line-chart__point p3" /><span className="line-chart__point p4" /><footer><span>Jul</span><span>Ago</span><span>Set</span><span>Out</span></footer></div></article>
      </div>
      <div className="foundation-warning"><AlertTriangle size={17} /><span>Dados desta tela são sintéticos e servem apenas para validar a fundação visual.</span></div>
    </section>
  )
}
