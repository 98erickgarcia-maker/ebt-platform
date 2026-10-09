import { useEffect, useState } from "react";
import { api, ApiError } from "./api";

type Catalog = { tenantId: string; applications: { code: string; name: string; description: string; state: string; available: boolean }[] };

export function PlatformApplications({ onOpenConnect, onOpenFlow }: { onOpenConnect: () => void; onOpenFlow: () => void }) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setCatalog(null); setError("");
    api<Catalog>("/api/platform/v1/applications").then(value => { if (active) setCatalog(value); })
      .catch(e => { if (active && !(e instanceof ApiError && e.code === "context_changed")) setError((e as Error).message); });
    return () => { active = false; };
  }, [attempt]);
  if (error) return <div className="alert error" role="alert"><span>{error}</span><button className="secondary" onClick={() => setAttempt(x => x + 1)}>Tentar novamente</button></div>;
  if (!catalog) return <p role="status">Carregando aplicativos...</p>;
  return <section aria-label="Aplicativos da EBT Platform">
    <div className="platform-intro"><span className="eyebrow">EBT ENTERPRISE</span><h2>Uma plataforma. Seus aplicativos.</h2><p>O Connect organiza o trabalho de hoje. Os demais aplicativos fazem parte da evolução da EBT Platform.</p></div>
    <div className="application-grid">{catalog.applications.map(item => <article className="application-card" key={item.code} data-application={item.code}>
      <span className={"badge " + (item.available ? "badge-approved" : "")}>{item.available ? "Disponível" : item.state === "disabled" ? "Indisponível" : "Planejado"}</span>
      <h3>{item.name}</h3><p>{item.description}</p>
      {item.available ? <button className="primary" onClick={item.code === "flow" ? onOpenFlow : onOpenConnect}>Acessar {item.code === "flow" ? "Flow" : "Connect"}</button> : <p className="small">Em planejamento</p>}
    </article>)}</div>
  </section>;
}
