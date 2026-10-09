import { useEffect, useState } from 'react';
import { api } from './api';

type Catalog = {
  platform: string; product: string; tenantId: string;
  modules: { key: string; name: string; access: 'read' | 'write' | 'admin' }[];
};
const accessNames = { read: 'Consulta', write: 'Operação', admin: 'Administração' };

export function PlatformCapabilitiesPanel() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setCatalog(null); setError('');
    api<Catalog>('/api/platform/v1/capabilities')
      .then(data => { if (active) setCatalog(data); })
      .catch(problem => { if (active) setError((problem as Error).message); });
    return () => { active = false; };
  }, [attempt]);
  return <section className="card">
    <header><h2>Capacidades desta plataforma</h2></header>
    <p>O Connect é o espaço de relacionamento da EBT Platform. Estes são os módulos disponíveis para seu acesso nesta empresa.</p>
    {error ? <div role="alert"><p>{error}</p><button className="secondary" onClick={() => setAttempt(attempt + 1)}>Tentar novamente</button></div>
      : !catalog ? <p role="status">Consultando módulos…</p>
      : catalog.modules.length === 0 ? <p>Nenhum módulo disponível para este acesso.</p>
      : <table><caption>{catalog.platform} / {catalog.product}</caption><thead><tr><th>Módulo</th><th>Acesso</th></tr></thead><tbody>
        {catalog.modules.map(module => <tr key={module.key}><td>{module.name}</td><td>{accessNames[module.access]}</td></tr>)}
      </tbody></table>}
  </section>;
}
