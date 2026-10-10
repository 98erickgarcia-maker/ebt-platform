import { useCallback, useEffect, useState, useRef } from "react";
import { api, ApiError } from "./api";

type FlowRow = { id: string; number: number; year: number; subject: string; state: "open" | "in_review" | "complete"; version: number; portfolio: string; createdAt: string };
type FlowList = { items: FlowRow[] };
const steps: Record<FlowRow["state"], string> = { open: "Aberto", in_review: "Em análise", complete: "Concluído" };

export function FlowPanel({ writable, identity }: { writable: boolean; identity: string }) {
  const [rows, setRows] = useState<FlowRow[]>([]);
  const [subject, setSubject] = useState("");
  const [result, setResult] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const draft = useRef<{subject: string; key: string} | null>(null);
  const [history, setHistory] = useState<Record<string, {id:string; action:string; result:string; occurredAt:string}[]>>({});
  const [serial, setSerial] = useState(0);
  const load = useCallback(async () => {
    try { setError(""); setRows((await api<FlowList>("/api/flow/v1/protocols")).items); }
    catch(e) { if (!(e instanceof ApiError && e.code === "context_changed")) setError((e as Error).message); }
  }, []);
  useEffect(() => {
    let active = true;
    // This component remounts on a different identity. No response from the old identity is displayed.
    api<FlowList>("/api/flow/v1/protocols").then(x => { if (active) { setRows(x.items); setError(""); } })
      .catch(e => { if (active && !(e instanceof ApiError && e.code === "context_changed")) setError((e as Error).message); });
    return () => { active = false; };
  }, [identity, serial]);
  async function create() {
    if(!subject.trim() || busy) return;
    setBusy(true);setError("");setNotice("");
    const content = subject.trim();
    if (!draft.current || draft.current.subject !== content) draft.current = {subject:content,key:crypto.randomUUID()};
    const key = draft.current.key;
    try {
      await api("/api/flow/v1/protocols", "POST", {subject}, {"Idempotency-Key": key});
      draft.current = null; setSubject(""); setNotice("Protocolo aberto."); await load();
    } catch(e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  async function advance(row: FlowRow) {
    if(busy) return;
    const action = row.state === "open" ? "start" : "complete";
    if(action === "complete" && !result[row.id]?.trim()) { setError("Informe o resultado antes de concluir."); return; }
    setBusy(true); setError("");setNotice("");
    try {
      await api("/api/flow/v1/protocols/" + row.id + "/transition", "POST",
        {action, result: action === "complete" ? result[row.id] : null}, {"If-Match": '"' + row.version + '"'});
      setNotice("Movimento registrado."); await load();
    } catch(e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  async function viewHistory(id:string) {
    setError("");
    try { const data = await api<{items:{id:string; action:string; result:string; occurredAt:string}[]}>("/api/flow/v1/protocols/"+id+"/history"); setHistory(old=>({...old,[id]:data.items})); }
    catch(e) { if (!(e instanceof ApiError && e.code === "context_changed")) setError((e as Error).message); }
  }
  return <section aria-label="EBT Flow" className="flow-workspace">
    <div className="flow-intro">
      <div><span className="eyebrow">EBT FLOW · PROCESSOS CONECTADOS</span>
        <h2>Fluxos com controle e rastreabilidade.</h2>
        <p>Abra protocolos, acompanhe análise e registre conclusões. Cada movimento pertence à empresa selecionada.</p></div>
      <span className="flow-status">Recorte inicial · fluxo fixo</span>
    </div>
    {error && <div role="alert" className="alert error">{error} <button onClick={() => setSerial(x=>x+1)}>Tentar novamente</button></div>}
    {notice && <p role="status" className="alert success">{notice}</p>}
    {writable && <div className="flow-create">
      <label htmlFor="flow-subject">Assunto do protocolo</label>
      <div><input id="flow-subject" maxLength={180} value={subject} onChange={e=>setSubject(e.target.value)} placeholder="Ex.: Revisar solicitação comercial" />
      <button disabled={busy || !subject.trim()} className="primary" onClick={() => void create()}>Abrir protocolo</button></div>
    </div>}
    <div className="flow-list">
      <h3>Protocolos recentes</h3>
      {rows.length===0 ? <p>Nenhum protocolo registrado para sua empresa e carteira.</p> :
      rows.map(row=><article key={row.id} className="flow-record">
        <div className="flow-record-header"><span className="eyebrow">#{row.year}/{String(row.number).padStart(4,"0")}</span><span className="badge">{steps[row.state]}</span></div>
        <h4>{row.subject}</h4><p>Aberto em {new Date(row.createdAt).toLocaleDateString("pt-BR")}</p>
        <button className="text-button" onClick={()=>void viewHistory(row.id)}>Ver histórico do protocolo {row.number}</button>
        {history[row.id] && <ol aria-label={"Histórico do protocolo " + row.number}>{history[row.id].map(item=><li key={item.id}>{({created:"Aberto",start:"Análise iniciada",complete:"Concluído"} as Record<string,string>)[item.action]} · {new Date(item.occurredAt).toLocaleString("pt-BR")}{item.result && <p>{item.result}</p>}</li>)}</ol>}
        {writable && row.state !== "complete" && <div className="flow-actions">
          {row.state === "in_review" && <label>Resultado da análise<textarea aria-label={"Resultado do protocolo " + row.number} maxLength={1000} value={result[row.id]??""} onChange={e=>setResult(old=>({...old,[row.id]:e.target.value}))} /></label>}
          <button disabled={busy || row.state === "in_review" && !result[row.id]?.trim()} className="secondary" onClick={()=>void advance(row)}>
            {row.state === "open"?"Iniciar análise":"Concluir protocolo"}
          </button>
        </div>}
      </article>)}
    </div>
  </section>;
}
