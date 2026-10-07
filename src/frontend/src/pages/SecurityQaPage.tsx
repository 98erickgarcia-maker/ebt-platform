import { useEffect, useState, useSyncExternalStore } from 'react'
import { requestJson } from '../api/http'
import { refreshSession, signInQa, signOut } from '../api/session'
import { sessionBoundary, SessionChangedError } from '../api/sessionBoundary'

type RecordRow = { id: string; title: string; tenantKey: string }

function PrivateRecords() {
  const [records, setRecords] = useState<RecordRow[]>([])
  const [message, setMessage] = useState('Carregando registros autorizados…')
  const [title, setTitle] = useState('')
  const [saving, setSaving] = useState(false)
  useEffect(() => {
    let active = true
    const controller = new AbortController()
    requestJson<RecordRow[]>('/api/foundation/records/', { signal: controller.signal })
      .then(rows => { if (active) { setRecords(rows); setMessage(rows.length ? '' : 'Nenhum registro nesta carteira.') } })
      .catch(error => { if (active && !(error instanceof SessionChangedError)) setMessage(error.message) })
    return () => { active = false; controller.abort() }
  }, [])

  async function create() {
    const generation = sessionBoundary.getSnapshot()
    setSaving(true)
    try {
      await requestJson<RecordRow>('/api/foundation/records/', {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ title }),
      })
      if (generation !== sessionBoundary.getSnapshot()) throw new SessionChangedError()
      const rows = await requestJson<RecordRow[]>('/api/foundation/records/')
      setRecords(rows); setTitle(''); setMessage('Registro salvo e relido do servidor.')
    } catch (error) {
      if (!(error instanceof SessionChangedError)) setMessage(error instanceof Error ? error.message : 'Falha ao salvar.')
    } finally { setSaving(false) }
  }

  const canWrite = ['Administrator', 'Operator'].includes(sessionBoundary.getIdentity()?.role ?? '')
  return <section className="panel" aria-label="Registros privados autorizados">
    <h2>Registros da sessão</h2>
    {message && <p role="status">{message}</p>}
    <ul>{records.map(record => <li key={record.id}>{record.title} · {record.tenantKey}</li>)}</ul>
    {canWrite && <form onSubmit={event => { event.preventDefault(); void create() }}>
      <label>Título sintético<input value={title} onChange={event => setTitle(event.target.value)} maxLength={200} required /></label>
      <button className="primary-button" disabled={saving || !title.trim()}>Salvar registro de QA</button>
    </form>}
  </section>
}

export function SecurityQaPage() {
  const generation = useSyncExternalStore(sessionBoundary.subscribe, sessionBoundary.getSnapshot)
  const identity = sessionBoundary.getIdentity()
  const [email, setEmail] = useState('admin.orbe@demo.invalid')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  useEffect(() => {
    let active = true
    refreshSession().catch(error => { if (active && !(error instanceof SessionChangedError)) setMessage(error.message) })
    return () => { active = false }
  }, [])
  async function login() {
    setBusy(true); setMessage('')
    try { await signInQa(email, code); setCode('') }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Falha de acesso.') }
    finally { setBusy(false) }
  }
  async function logout() {
    setBusy(true); setMessage('')
    try { await signOut() }
    catch { setMessage('Estado local limpo; não foi possível confirmar o logout no servidor. Tente novamente.') }
    finally { setBusy(false) }
  }
  return <section className="page-stack">
    <h1>Sessão e registros de QA</h1>
    <p>Dados sintéticos persistidos. O acesso por código funciona somente em QA/Development. As demais telas de demonstração continuam com massa ilustrativa.</p>
    <form className="panel" onSubmit={event => { event.preventDefault(); void login() }}>
      <label>Perfil sintético<select value={email} onChange={event => setEmail(event.target.value)} disabled={busy}>
        {['admin.orbe', 'operador.orbe', 'consulta.orbe', 'admin.nexo', 'operador.nexo', 'consulta.nexo', 'suporte'].map(user =>
          <option key={user} value={`${user}@demo.invalid`}>{user}@demo.invalid</option>)}
      </select></label>
      <label>Código QA<input type="password" value={code} onChange={event => setCode(event.target.value)} autoComplete="off" required disabled={busy} /></label>
      <button className="primary-button" disabled={busy}>Entrar / trocar perfil</button>
      <button type="button" onClick={() => void logout()} disabled={busy}>Sair e limpar sessão</button>
      {message && <p role="alert">{message}</p>}
    </form>
    {identity && <p aria-label="Identidade confirmada">{identity.displayName} · {identity.tenantKey ?? 'sem empresa'} · {identity.role}</p>}
    {identity?.tenantKey ? <PrivateRecords key={generation} /> : <p>Sem carteira autenticada.</p>}
  </section>
}
