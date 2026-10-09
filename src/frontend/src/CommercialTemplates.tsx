import { useEffect, useRef, useState } from "react";
import { api, route, type Contact } from "./api";
type Template = {
  id: string;
  name: string;
  channel: string;
  purpose: string;
  version: number;
  active: boolean;
};
type Preview = {
  id: string;
  version: number;
  channel: string;
  subject: string;
  body: string;
};
export function CommercialTemplates({
  contact,
  writable,
}: {
  contact: Contact;
  writable: boolean;
}) {
  const [templates, setTemplates] = useState<Template[]>([]),
    [choice, setChoice] = useState("");
  const [reload, setReload] = useState(0);
  const [preview, setPreview] = useState<Preview | null>(null),
    [subject, setSubject] = useState(""),
    [body, setBody] = useState("");
  const [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false);
  const alive = useRef(true),
    sequence = useRef(0),
    operation = useRef<{ payload: string; key: string } | null>(null);
  useEffect(() => {
    alive.current = true;
    let current = true;
    setError("");
    api<Template[]>(route + "/mail/templates")
      .then((x) => {
        if (current) setTemplates(x.filter((t) => t.active));
      })
      .catch((e) => {
        if (current) setError(e.message);
      });
    return () => {
      current = false;
      alive.current = false;
      sequence.current++;
    };
  }, [reload]);
  async function choose(id: string) {
    setChoice(id);
    setPreview(null);
    setNotice("");
    setError("");
    const seq = ++sequence.current;
    if (!id) return;
    setBusy(true);
    try {
      const p = await api<Preview>(
        route + "/mail/templates/" + id + "/preview?contactId=" + contact.id,
      );
      if (alive.current && seq === sequence.current) {
        setPreview(p);
        setBody(p.body);
        setSubject(p.subject);
      }
    } catch (e) {
      if (alive.current && seq === sequence.current)
        setError((e as Error).message);
    } finally {
      if (alive.current && seq === sequence.current) setBusy(false);
    }
  }
  async function saveDraft() {
    if (!preview || busy) return;
    setBusy(true);
    setError("");
    const payload = {
      contactId: contact.id,
      templateId: preview.id,
      templateVersion: preview.version,
      subject,
      body,
    };
    const signature = JSON.stringify(payload);
    if (operation.current?.payload !== signature)
      operation.current = { payload: signature, key: crypto.randomUUID() };
    try {
      await api(route + "/mail/drafts", "POST", payload, {
        "Idempotency-Key": operation.current.key,
      });
      if (alive.current) {
        setNotice(
          "Rascunho preparado. Acesse E-mail para revisar e aprovar esta versão.",
        );
      }
    } catch (e) {
      if (alive.current) setError((e as Error).message);
    } finally {
      if (alive.current) setBusy(false);
    }
  }
  if (!writable) return null;
  return (
    <section
      className="card commercial-templates"
      aria-label="Contato com templates"
    >
      <header>
        <h2>Contato rápido</h2>
        <span className="muted">Contexto e texto no mesmo lugar</span>
      </header>
      <div className="contact-shortcuts">
        {contact.phone && (
          <a className="secondary" href={"tel:+" + contact.phone}>
            Ligar · +{contact.phone}
          </a>
        )}
        {contact.email && (
          <a className="secondary" href={"mailto:" + contact.email}>
            Abrir e-mail · {contact.email}
          </a>
        )}
      </div>
      <label htmlFor="commercial-template">Template comercial</label>
      <select
        id="commercial-template"
        value={choice}
        disabled={busy}
        onChange={(e) => void choose(e.target.value)}
      >
        <option value="">Selecione um modelo</option>
        {templates.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name} ·{" "}
            {t.channel === "email"
              ? "E-mail"
              : t.channel === "whatsapp"
                ? "WhatsApp"
                : "Ligação"}{" "}
            · v{t.version}
          </option>
        ))}
      </select>
      {!templates.length && !error && (
        <p className="muted">
          Crie seus modelos em E-mail → Modelos. Eles ficam disponíveis aqui
          para primeiro contato, retorno, proposta e cliente ativo.
        </p>
      )}
      {busy && <p role="status">Preparando texto…</p>}
      {error && (
        <p className="alert error" role="alert">
          {error}{" "}
          <button
            type="button"
            className="secondary"
            onClick={() =>
              choice ? void choose(choice) : setReload((n) => n + 1)
            }
          >
            Tentar novamente
          </button>
        </p>
      )}
      {preview && (
        <div className="quick-template-preview">
          {preview.channel === "email" && (
            <>
              <label htmlFor="commercial-subject">Assunto do contato</label>
              <input
                id="commercial-subject"
                maxLength={200}
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </>
          )}
          <label htmlFor="commercial-message">Texto personalizado</label>
          <textarea
            id="commercial-message"
            rows={5}
            maxLength={12000}
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
          <small>
            Modelo v{preview.version}. Confira o texto e adapte à necessidade
            real do contato.
          </small>
          <div className="contact-shortcuts">
            {preview.channel === "email" && (
              <button
                className="primary"
                disabled={
                  busy || !contact.email || !subject.trim() || !body.trim()
                }
                onClick={() => void saveDraft()}
              >
                Preparar e-mail com este modelo
              </button>
            )}
            {preview.channel === "whatsapp" && contact.phone && body.trim() && (
              <a
                className="primary"
                href={
                  "https://wa.me/" +
                  contact.phone +
                  "?text=" +
                  encodeURIComponent(body)
                }
                target="_blank"
                rel="noreferrer"
              >
                Abrir WhatsApp com o texto
              </a>
            )}
            <button
              className="secondary"
              disabled={!body.trim()}
              onClick={() =>
                void navigator.clipboard
                  .writeText(body)
                  .then(() => {
                    if (alive.current) setNotice("Texto copiado.");
                  })
                  .catch(() => {
                    if (alive.current)
                      setError(
                        "Não foi possível copiar. Selecione o texto acima.",
                      );
                  })
              }
            >
              Copiar texto
            </button>
          </div>
          {preview.channel !== "email" && (
            <p className="muted">
              Abrir o aplicativo ou copiar o roteiro não registra envio.
              Registre apenas o contato que você realizou.
            </p>
          )}
        </div>
      )}
      {notice && <p role="status">{notice}</p>}
    </section>
  );
}
