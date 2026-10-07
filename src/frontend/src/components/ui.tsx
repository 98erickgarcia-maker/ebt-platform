import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

export function PageHeader({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <header className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action && <div className="page-header__action">{action}</div>}
    </header>
  )
}

export function StatusBadge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'orange' | 'green' | 'red' | 'blue' | 'violet' }) {
  return <span className={`status-badge status-badge--${tone}`}>{children}</span>
}

export function KpiCard({ label, value, trend, to, icon }: { label: string; value: string; trend: string; to: string; icon: ReactNode }) {
  return (
    <Link className="kpi-card" to={to}>
      <span className="kpi-card__icon">{icon}</span>
      <span>
        <small>{label}</small>
        <strong>{value}</strong>
        <em>{trend}</em>
      </span>
    </Link>
  )
}
