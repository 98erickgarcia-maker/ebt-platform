import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  api,
  date,
  download,
  route,
  type Contact,
  type Document,
  type Me,
} from "./api";
type Template = {
  id: string;
  name: string;
  subject: string;
  body: string;
  active: boolean;
  version: number;
  channel: string;
  purpose: string;
};
type Draft = {
  id: string;
  contactId: string;
  recipient: string;
  subject: string;
  body: string;
  state: string;
  origin: string;
  version: number;
  documentId: string | null;
  documentNumber: number | null;
  diagnostic: string;
  createdAt: string;
};
type Status = {
  configured: boolean;
  sender: string;
  paused: boolean;
  intervalSeconds: number;
  dailyCap: number;
  version: number;
  used: number;
  day: string;
  counts: { state: string; count: number }[];
};
type Revision = {
  id: string;
  subject: string;
  body: string;
  state: string;
  reason: string;
  at: string;
};
type Suppression = {
  id: string;
  value: string;
  reason: string;
  active: boolean;
};
const states: Record<string, string> = {
  draft: "Rascunho",
  approved: "Aprovado",
  queued: "Na fila",
  processing: "Em processamento",
  accepted: "Aceito pela Microsoft",
  unknown: "Envio incerto",
  failed: "Falha",
  cancelled: "Cancelado",
  reconciled: "Conferido manualmente",
};
const reasons: Record<string, string> = {
  created: "Rascunho criado",
  approved: "Versão aprovada",
  approve: "Versão aprovada",
  queue: "Enfileirado para envio",
  cancel: "Cancelamento registrado",
  reconcile: "Conferência registrada",
  reserved: "Envio reservado",
  edited_approval_invalidated: "Texto editado; aprovação anterior invalidada",
  graph_accepted_not_delivery: "Solicitação aceita pela Microsoft",
  graph_throttled: "Microsoft limitou o envio; fila pausada",
  graph_uncertain: "Resultado incerto; confira antes de reenviar",
  graph_authentication_failed: "Conexão Microsoft precisa ser revisada",
  graph_rejected: "Microsoft recusou a solicitação",
  worker_restart_uncertain:
    "Envio interrompido; resultado precisa de conferência",
  mail_access_or_recipient_changed:
    "Destinatário ou permissão mudou; revise a mensagem",
  mail_attachment_changed: "Anexo alterado; revise a versão",
  document_not_scanned: "Arquivo ainda aguarda inspeção",
};
const p = route + "/mail";
const initial = {
  name: "Apresentação EBT",
  subject: "EBT Enterprise | Organização da operação",
  body: "Olá, {nome}.\n\nA EBT Enterprise desenvolve sites, CRMs e sistemas sob medida para organizar o relacionamento, documentos e acompanhamento da operação.\n\nPodemos agendar uma conversa de 15 minutos para entender a rotina da {empresa}? Qual dia e horário funciona melhor?\n\nEquipe Comercial EBT Enterprise",
  active: true,
  channel: "email",
  purpose: "prospection",
};
export function MailPanel({
  me,
  onContact,
}: {
  me: Me;
  onContact: (id: string) => void;
}) {
  const [tab, setTab] = useState("drafts"),
    [status, setStatus] = useState<Status | null>(null),
    [templates, setTemplates] = useState<Template[]>([]),
    [rows, setRows] = useState<Draft[]>([]),
    [total, setTotal] = useState(0),
    [page, setPage] = useState(1),
    [state, setState] = useState(""),
    [search, setSearch] = useState(""),
    [reload, setReload] = useState(0);
  const [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [contacts, setContacts] = useState<Contact[]>([]),
    [contactSearch, setContactSearch] = useState(""),
    [contactPage, setContactPage] = useState(1),
    [contactTotal, setContactTotal] = useState(0),
    [chosen, setChosen] = useState<string[]>([]),
    [batchTemplate, setBatchTemplate] = useState("");
  const [editing, setEditing] = useState<Draft | null>(null),
    [compose, setCompose] = useState(false),
    [contactId, setContactId] = useState(""),
    [subject, setSubject] = useState(""),
    [body, setBody] = useState(""),
    [documentId, setDocumentId] = useState(""),
    [documents, setDocuments] = useState<Document[]>([]);
  const [template, setTemplate] = useState<typeof initial>({ ...initial }),
    [templateId, setTemplateId] = useState(""),
    [templateVersion, setTemplateVersion] = useState(0);
  const [selected, setSelected] = useState<Draft | null>(null),
    [revisions, setRevisions] = useState<Revision[]>([]),
    [historyTotal, setHistoryTotal] = useState(0),
    [historyPage, setHistoryPage] = useState(1),
    [reason, setReason] = useState("");
  const [suppression, setSuppression] = useState<Suppression[]>([]),
    [blocked, setBlocked] = useState(""),
    [blockReason, setBlockReason] = useState(""),
    [interval, setInterval] = useState(3),
    [cap, setCap] = useState(100);
  const [composeTemplate, setComposeTemplate] = useState(""),
    [appliedTemplate, setAppliedTemplate] = useState<{
      id: string;
      version: number;
    } | null>(null);
  const sequence = useRef(0),
    keys = useRef(new Map<string, string>()),
    alive = useRef(true);
  const writable = me.role !== "reader",
    admin = me.role === "admin";
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      sequence.current++;
    };
  }, []);
  useEffect(() => {
    let current = true;
    const seq = ++sequence.current;
    setLoading(true);
    setError("");
    Promise.all([
      api<Status>(p + "/status"),
      api<Template[]>(p + "/templates"),
      api<{ items: Draft[]; total: number }>(
        p +
          "/drafts?" +
          new URLSearchParams({ page: String(page), state, search }),
      ),
    ])
      .then(([s, t, d]) => {
        if (!current || seq !== sequence.current) return;
        setStatus(s);
        setTemplates(t);
        setRows(d.items);
        setTotal(d.total);
        setInterval(s.intervalSeconds);
        setCap(s.dailyCap);
      })
      .catch((e) => {
        if (current) setError(e.message);
      })
      .finally(() => {
        if (current) setLoading(false);
      });
    return () => {
      current = false;
    };
  }, [page, state, search, reload]);
  useEffect(() => {
    if (!compose && tab !== "batch") return;
    let current = true;
    api<{ items: Contact[]; total: number }>(
      route +
        "/contacts?" +
        new URLSearchParams({
          search: contactSearch,
          page: String(contactPage),
          limit: "25",
        }),
    )
      .then((x) => {
        if (current) {
          setContacts(x.items);
          setContactTotal(x.total);
        }
      })
      .catch((e) => {
        if (current) setError(e.message);
      });
    return () => {
      current = false;
    };
  }, [compose, tab, contactSearch, contactPage]);
  useEffect(() => {
    setDocuments([]);
    if (!contactId) return;
    let current = true;
    api<Document[]>(route + "/documents?contactId=" + contactId)
      .then((x) => {
        if (current) setDocuments(x);
      })
      .catch((e) => {
        if (current) setError(e.message);
      });
    return () => {
      current = false;
    };
  }, [contactId]);
  useEffect(() => {
    if (!selected) return;
    let current = true;
    setRevisions([]);
    api<{ items: Revision[]; total: number }>(
      p + "/drafts/" + selected.id + "/history?page=" + historyPage,
    )
      .then((x) => {
        if (current) {
          setRevisions(x.items);
          setHistoryTotal(x.total);
        }
      })
      .catch((e) => {
        if (current) setError(e.message);
      });
    return () => {
      current = false;
    };
  }, [selected, historyPage, reload]);
  useEffect(() => {
    if (tab !== "settings" || !admin) return;
    let current = true;
    api<Suppression[]>(p + "/suppression")
      .then((x) => {
        if (current) setSuppression(x);
      })
      .catch((e) => {
        if (current) setError(e.message);
      });
    return () => {
      current = false;
    };
  }, [tab, admin, reload]);
  async function run(work: () => Promise<void>, message: string) {
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await work();
      if (alive.current) {
        setNotice(message);
        setReload((x) => x + 1);
      }
    } catch (e) {
      if (alive.current) setError((e as Error).message);
    } finally {
      if (alive.current) setBusy(false);
    }
  }
  async function mutate<T>(
    path: string,
    method: string,
    payload: unknown,
    version?: number,
  ): Promise<T> {
    const signature = JSON.stringify([path, method, payload, version]);
    let key = keys.current.get(signature);
    if (!key) {
      key = crypto.randomUUID();
      keys.current.set(signature, key);
    }
    const result = await api<T>(path, method, payload, {
      "Idempotency-Key": key,
      ...(version === undefined ? {} : { "If-Match": `"${version}"` }),
    });
    keys.current.delete(signature);
    return result;
  }
  function begin(row?: Draft) {
    setComposeTemplate("");
    setAppliedTemplate(null);
    setEditing(row ?? null);
    setContactId(row?.contactId ?? "");
    setSubject(row?.subject ?? "");
    setBody(row?.body ?? "");
    setDocumentId(row?.documentId ?? "");
    setCompose(true);
    setSelected(null);
  }
  function submitDraft(e: FormEvent) {
    e.preventDefault();
    void run(async () => {
      const payload = {
        contactId,
        subject,
        body,
        documentId: documentId || null,
        ...(appliedTemplate
          ? {
              templateId: appliedTemplate.id,
              templateVersion: appliedTemplate.version,
            }
          : {}),
      };
      await mutate(
        editing ? p + "/drafts/" + editing.id : p + "/drafts",
        editing ? "PUT" : "POST",
        payload,
        editing?.version,
      );
      if (alive.current) {
        setCompose(false);
        setEditing(null);
      }
    }, "Rascunho salvo. A versão atual precisa de revisão antes do envio.");
  }
  function action(row: Draft, name: string) {
    void run(async () => {
      const result = await mutate<Draft>(
        p + "/drafts/" + row.id + "/action",
        "POST",
        { action: name, reason: name === "reconcile" ? reason : null },
        row.version,
      );
      if (alive.current && selected?.id === row.id) setSelected(result);
    }, "Estado da mensagem atualizado.");
  }
  const pagination = (
    index: number,
    count: number,
    change: (x: number) => void,
  ) => (
    <div className="pagination">
      <button
        type="button"
        className="secondary"
        disabled={busy || loading || index <= 1}
        onClick={() => change(index - 1)}
      >
        Anterior
      </button>
      <span>
        Página {index} de {Math.max(1, Math.ceil(count / 25))} · {count}{" "}
        registros
      </span>
      <button
        type="button"
        className="secondary"
        disabled={busy || loading || index * 25 >= count}
        onClick={() => change(index + 1)}
      >
        Próxima
      </button>
    </div>
  );
  return (
    <section className="mail-panel" aria-label="E-mail do Connect">
      {error && (
        <div className="alert error" role="alert">
          {error}{" "}
          <button className="secondary" onClick={() => setReload((x) => x + 1)}>
            Atualizar dados
          </button>
        </div>
      )}
      {notice && (
        <div className="alert" role="status">
          {notice}
        </div>
      )}
      <div className="panel mail-status">
        <strong>
          {status?.configured
            ? `Microsoft · ${status.sender}`
            : "Microsoft: conexão pendente"}
        </strong>
        <p>
          Preparar, aprovar e enviar são estados separados. Aceite da Microsoft
          não comprova entrega ou leitura.
        </p>
        <span>
          Fila {status?.paused === false ? "ativa" : "pausada"} ·{" "}
          {status?.used ?? 0}/{status?.dailyCap ?? 100} reservas hoje ·
          intervalo {status?.intervalSeconds ?? 3}s
        </span>
      </div>
      <div className="mail-tabs" role="group" aria-label="Seções de e-mail">
        {[
          ["drafts", "Mensagens"],
          ["templates", "Modelos"],
          ["batch", "Preparar lote"],
          ...(admin ? [["settings", "Controle de envio"]] : []),
        ].map(([id, title]) => (
          <button
            key={id}
            className={tab === id ? "primary" : "secondary"}
            aria-pressed={tab === id}
            onClick={() => {
              setTab(id);
              setCompose(false);
              setSelected(null);
            }}
          >
            {title}
          </button>
        ))}
      </div>
      {loading && <p role="status">Carregando e-mails…</p>}
      {tab === "drafts" && (
        <>
          <div className="mail-tools">
            <label>
              Buscar mensagens
              <input
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                placeholder="Assunto ou destinatário"
              />
            </label>
            <label>
              Estado
              <select
                value={state}
                onChange={(e) => {
                  setState(e.target.value);
                  setPage(1);
                }}
              >
                <option value="">Todos os estados</option>
                {Object.entries(states).map(([id, title]) => (
                  <option key={id} value={id}>
                    {title}
                  </option>
                ))}
              </select>
            </label>
            {writable && (
              <button className="primary" onClick={() => begin()}>
                Nova mensagem
              </button>
            )}
          </div>
          <div className="mail-kpis">
            {status?.counts.map((x) => (
              <button
                className="secondary"
                key={x.state}
                onClick={() => {
                  setState(x.state);
                  setPage(1);
                }}
              >
                {states[x.state] ?? x.state}: {x.count}
              </button>
            ))}
          </div>
          {compose && (
            <form className="panel mail-form" onSubmit={submitDraft}>
              <h2>{editing ? "Revisar mensagem" : "Nova mensagem"}</h2>
              <label>
                Buscar contato
                <input
                  value={contactSearch}
                  onChange={(e) => {
                    setContactSearch(e.target.value);
                    setContactPage(1);
                  }}
                />
              </label>
              <label>
                Contato
                <select
                  required
                  disabled={!!editing}
                  value={contactId}
                  onChange={(e) => {
                    setContactId(e.target.value);
                    setDocumentId("");
                    setAppliedTemplate(null);
                  }}
                >
                  <option value="">Selecione um contato</option>
                  {editing && !contacts.some((x) => x.id === contactId) && (
                    <option value={contactId}>{editing.recipient}</option>
                  )}
                  {contacts.map((x) => (
                    <option key={x.id} value={x.id} disabled={!x.email}>
                      {x.name} · {x.email || "sem e-mail"}
                    </option>
                  ))}
                </select>
              </label>
              {pagination(contactPage, contactTotal, setContactPage)}
              <div className="mail-template-choice">
                <label>
                  Modelo para este e-mail
                  <select
                    value={composeTemplate}
                    onChange={(e) => setComposeTemplate(e.target.value)}
                  >
                    <option value="">Escolha um modelo</option>
                    {templates
                      .filter((t) => t.active && t.channel === "email")
                      .map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name} · v{t.version}
                        </option>
                      ))}
                  </select>
                </label>
                <button
                  type="button"
                  className="secondary"
                  disabled={busy || !contactId || !composeTemplate}
                  onClick={() =>
                    void run(async () => {
                      const preview = await api<{
                        id: string;
                        version: number;
                        subject: string;
                        body: string;
                      }>(
                        p +
                          "/templates/" +
                          composeTemplate +
                          "/preview?contactId=" +
                          contactId,
                      );
                      if (alive.current) {
                        setSubject(preview.subject);
                        setBody(preview.body);
                        setAppliedTemplate({
                          id: preview.id,
                          version: preview.version,
                        });
                      }
                    }, "Modelo aplicado. Confira o texto personalizado antes de salvar.")
                  }
                >
                  Aplicar modelo
                </button>
                {appliedTemplate && (
                  <small>
                    Modelo v{appliedTemplate.version}. O texto abaixo pode ser
                    ajustado antes da aprovação.
                  </small>
                )}
              </div>
              <label htmlFor="mail-subject">Assunto</label>
              <input
                id="mail-subject"
                required
                maxLength={200}
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
              <label htmlFor="mail-body">Mensagem</label>
              <textarea
                id="mail-body"
                required
                maxLength={12000}
                rows={9}
                value={body}
                onChange={(e) => setBody(e.target.value)}
              />
              <label>
                Anexo comercial
                <select
                  value={documentId}
                  onChange={(e) => setDocumentId(e.target.value)}
                >
                  <option value="">Sem anexo</option>
                  {documents
                    .filter((x) => x.reviewState === "approved")
                    .map((x) => (
                      <option key={x.id} value={x.id}>
                        {x.title} · versão {x.currentVersion}
                      </option>
                    ))}
                </select>
              </label>
              <small>
                A versão aprovada e a inspeção do arquivo serão conferidas no
                servidor.
              </small>
              <div className="mail-tools">
                <button className="primary" disabled={busy}>
                  Salvar rascunho
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setCompose(false)}
                >
                  Fechar
                </button>
              </div>
            </form>
          )}
          {selected && (
            <article className="panel mail-detail">
              <div className="mail-tools">
                <h2>{selected.subject}</h2>
                <button className="secondary" onClick={() => setSelected(null)}>
                  Fechar detalhe
                </button>
              </div>
              <p>
                {selected.recipient} · {states[selected.state]} · versão{" "}
                {selected.version}
              </p>
              <small>
                Origem: {selected.origin} · {date(selected.createdAt)}
                {selected.documentNumber
                  ? ` · anexo v${selected.documentNumber}`
                  : ""}
              </small>
              <pre>{selected.body}</pre>
              <button
                className="secondary"
                onClick={() => onContact(selected.contactId)}
              >
                Abrir relacionamento
              </button>
              {selected.state === "unknown" && admin && (
                <div className="mail-form">
                  <label>
                    Evidência de conferência dos Itens Enviados
                    <textarea
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      maxLength={1000}
                    />
                  </label>
                  <button
                    className="secondary"
                    disabled={busy || !reason.trim()}
                    onClick={() => action(selected, "reconcile")}
                  >
                    Registrar conferência
                  </button>
                </div>
              )}
              <h3>Histórico preservado</h3>
              {revisions.map((x) => (
                <details key={x.id}>
                  <summary>
                    {date(x.at)} · {states[x.state]} ·{" "}
                    {reasons[x.reason] ?? x.reason}
                  </summary>
                  <strong>{x.subject}</strong>
                  <pre>{x.body}</pre>
                </details>
              ))}
              {pagination(historyPage, historyTotal, setHistoryPage)}
            </article>
          )}
          {!loading && rows.length === 0 && (
            <div className="panel">
              <h2>Nenhuma mensagem neste filtro</h2>
              <p>
                Prepare um rascunho ou um lote a partir dos relacionamentos já
                cadastrados.
              </p>
            </div>
          )}
          <div className="mail-list">
            {rows.map((row) => (
              <article className="panel" key={row.id}>
                <button
                  className="text-button"
                  onClick={() => {
                    setSelected(row);
                    setHistoryPage(1);
                    setCompose(false);
                  }}
                >
                  <strong>{row.subject}</strong>
                </button>
                <p>
                  {row.recipient} ·{" "}
                  <span className="tag">{states[row.state]}</span>
                </p>
                <small>
                  {date(row.createdAt)} · versão {row.version}
                </small>
                <div className="mail-tools">
                  <button
                    className="secondary"
                    disabled={busy}
                    onClick={() =>
                      void run(async () => {
                        await download(p + "/drafts/" + row.id + "/eml");
                      }, "Rascunho exportado; envio manual e anexos devem ser conferidos no seu e-mail.")
                    }
                  >
                    Baixar .eml (sem anexo)
                  </button>
                  {writable &&
                    ["draft", "approved", "failed"].includes(row.state) && (
                      <button
                        className="secondary"
                        disabled={busy}
                        onClick={() => begin(row)}
                      >
                        Editar
                      </button>
                    )}
                  {admin && ["draft", "failed"].includes(row.state) && (
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() => action(row, "approve")}
                    >
                      Aprovar versão {row.version}
                    </button>
                  )}
                  {writable && row.state === "approved" && (
                    <button
                      className="primary"
                      disabled={busy || !status?.configured}
                      title={
                        !status?.configured
                          ? "Configure Microsoft Graph no servidor"
                          : ""
                      }
                      onClick={() => action(row, "queue")}
                    >
                      Solicitar envio real
                    </button>
                  )}
                  {writable &&
                    ["draft", "approved", "queued", "failed"].includes(
                      row.state,
                    ) && (
                      <button
                        className="secondary"
                        disabled={busy}
                        onClick={() => action(row, "cancel")}
                      >
                        Cancelar
                      </button>
                    )}
                </div>
                {row.diagnostic && (
                  <small>
                    Diagnóstico:{" "}
                    {reasons[row.diagnostic] ??
                      "Confira o resultado no histórico da mensagem."}
                  </small>
                )}
              </article>
            ))}
          </div>
          {pagination(page, total, setPage)}
        </>
      )}
      {tab === "templates" && (
        <div className="mail-columns">
          <section className="panel">
            <h2>Modelos preservados</h2>
            <p>
              Personalização local, sem depender de créditos de IA. Use{" "}
              {"{nome}"}, {"{empresa}"} e {"{email}"}.
            </p>
            {templates.length === 0 && <p>Nenhum modelo cadastrado.</p>}
            {templates.map((x) => (
              <button
                className="secondary mail-template"
                key={x.id}
                onClick={() => {
                  setTemplate({
                    name: x.name,
                    subject: x.subject,
                    body: x.body,
                    active: x.active,
                    channel: x.channel,
                    purpose: x.purpose,
                  });
                  setTemplateId(x.id);
                  setTemplateVersion(x.version);
                }}
              >
                {x.name} · v{x.version} · {x.active ? "ativo" : "inativo"}
              </button>
            ))}
          </section>
          {writable && (
            <form
              className="panel mail-form"
              onSubmit={(e) => {
                e.preventDefault();
                void run(async () => {
                  await mutate(
                    templateId
                      ? p + "/templates/" + templateId
                      : p + "/templates",
                    templateId ? "PUT" : "POST",
                    template,
                    templateId ? templateVersion : undefined,
                  );
                  if (alive.current) {
                    setTemplateId("");
                    setTemplate({ ...initial });
                  }
                }, "Modelo salvo. Mensagens já preparadas mantêm o texto anterior.");
              }}
            >
              <h2>{templateId ? "Editar modelo" : "Criar modelo"}</h2>
              <div className="form-grid">
                <label>
                  Canal do modelo
                  <select
                    value={template.channel}
                    onChange={(e) =>
                      setTemplate({ ...template, channel: e.target.value })
                    }
                  >
                    <option value="email">E-mail</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="phone">Roteiro de ligação</option>
                  </select>
                </label>
                <label>
                  Objetivo do modelo
                  <select
                    value={template.purpose}
                    onChange={(e) =>
                      setTemplate({ ...template, purpose: e.target.value })
                    }
                  >
                    <option value="prospection">Primeiro contato</option>
                    <option value="followup">Retorno</option>
                    <option value="proposal">Acompanhamento de proposta</option>
                    <option value="relationship">Cliente ativo</option>
                  </select>
                </label>
              </div>
              <label>
                Nome
                <input
                  required
                  value={template.name}
                  maxLength={100}
                  onChange={(e) =>
                    setTemplate({ ...template, name: e.target.value })
                  }
                />
              </label>
              <label>
                Assunto
                <input
                  required
                  value={template.subject}
                  maxLength={200}
                  onChange={(e) =>
                    setTemplate({ ...template, subject: e.target.value })
                  }
                />
              </label>
              <label>
                Mensagem
                <textarea
                  rows={10}
                  required
                  value={template.body}
                  maxLength={12000}
                  onChange={(e) =>
                    setTemplate({ ...template, body: e.target.value })
                  }
                />
              </label>
              <label className="mail-check">
                <input
                  type="checkbox"
                  checked={template.active}
                  onChange={(e) =>
                    setTemplate({ ...template, active: e.target.checked })
                  }
                />
                Modelo ativo
              </label>
              <div className="mail-tools">
                <button className="primary" disabled={busy}>
                  Salvar modelo
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => {
                    setTemplateId("");
                    setTemplate({ ...initial });
                  }}
                >
                  Novo modelo
                </button>
              </div>
            </form>
          )}
        </div>
      )}
      {tab === "batch" && (
        <section className="panel mail-form">
          <h2>Preparar lote com revisão individual</h2>
          <p>
            Os contatos conservam seu ID. O lote cria rascunhos; cada versão
            deve ser aprovada antes de entrar na fila.
          </p>
          <label>
            Buscar relacionamentos
            <input
              value={contactSearch}
              onChange={(e) => {
                setContactSearch(e.target.value);
                setContactPage(1);
              }}
            />
          </label>
          <label>
            Modelo
            <select
              value={batchTemplate}
              onChange={(e) => setBatchTemplate(e.target.value)}
            >
              <option value="">Selecione</option>
              {templates
                .filter((x) => x.active && x.channel === "email")
                .map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.name} · v{x.version}
                  </option>
                ))}
            </select>
          </label>
          {contacts.map((x) => (
            <label className="mail-check" key={x.id}>
              <input
                type="checkbox"
                disabled={
                  !writable ||
                  !x.email ||
                  busy ||
                  (chosen.length >= 100 && !chosen.includes(x.id))
                }
                checked={chosen.includes(x.id)}
                onChange={(e) =>
                  setChosen(
                    e.target.checked
                      ? [...chosen, x.id]
                      : chosen.filter((id) => id !== x.id),
                  )
                }
              />
              <span>
                {x.name}
                <small>{x.email || "Cadastre um e-mail"}</small>
              </span>
            </label>
          ))}
          {pagination(contactPage, contactTotal, setContactPage)}
          <div className="mail-tools">
            <span>{chosen.length}/100 contatos selecionados</span>
            <button className="secondary" onClick={() => setChosen([])}>
              Limpar seleção
            </button>
            <button
              className="primary"
              disabled={
                !writable || busy || !batchTemplate || chosen.length === 0
              }
              onClick={() =>
                void run(async () => {
                  await mutate(p + "/batch", "POST", {
                    templateId: batchTemplate,
                    contactIds: chosen,
                  });
                  if (alive.current) {
                    setChosen([]);
                    setTab("drafts");
                    setPage(1);
                    setState("");
                  }
                }, "Lote preparado. Nenhum e-mail enviado.")
              }
            >
              Preparar rascunhos
            </button>
          </div>
        </section>
      )}
      {tab === "settings" && admin && (
        <div className="mail-columns">
          <section className="panel mail-form">
            <h2>Controle da fila</h2>
            <p>
              A fila inicia pausada. O limite conta reservas e envios incertos,
              evitando exceder a cota após reinício. Credenciais ficam somente
              no servidor.
            </p>
            <label>
              Intervalo entre envios (segundos)
              <input
                type="number"
                min={1}
                max={60}
                value={interval}
                onChange={(e) => setInterval(Number(e.target.value))}
              />
            </label>
            <label>
              Limite diário
              <input
                type="number"
                min={1}
                max={2000}
                value={cap}
                onChange={(e) => setCap(Number(e.target.value))}
              />
            </label>
            <div className="mail-tools">
              <button
                className="secondary"
                disabled={busy || !status}
                onClick={() =>
                  void run(async () => {
                    await mutate(
                      p + "/settings",
                      "PUT",
                      {
                        intervalSeconds: interval,
                        dailyCap: cap,
                        paused: true,
                      },
                      status?.version,
                    );
                  }, "Fila pausada e limites salvos.")
                }
              >
                Salvar e pausar
              </button>
              <button
                className="primary"
                disabled={busy || !status?.configured}
                onClick={() =>
                  void run(async () => {
                    await mutate(
                      p + "/settings",
                      "PUT",
                      {
                        intervalSeconds: interval,
                        dailyCap: cap,
                        paused: false,
                      },
                      status?.version,
                    );
                  }, "Fila ativa para mensagens aprovadas e solicitadas.")
                }
              >
                Retomar fila real
              </button>
            </div>
          </section>
          <section className="panel mail-form">
            <h2>Não enviar para</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void run(async () => {
                  await mutate(p + "/suppression", "POST", {
                    value: blocked,
                    reason: blockReason,
                    active: true,
                  });
                  if (alive.current) {
                    setBlocked("");
                    setBlockReason("");
                  }
                }, "Bloqueio salvo. Conferido novamente antes de cada envio.");
              }}
            >
              <label>
                E-mail ou domínio
                <input
                  required
                  value={blocked}
                  onChange={(e) => setBlocked(e.target.value)}
                  maxLength={254}
                />
              </label>
              <label>
                Motivo
                <textarea
                  required
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  maxLength={1000}
                />
              </label>
              <button className="secondary" disabled={busy}>
                Bloquear destinatário
              </button>
            </form>
            {suppression.map((x) => (
              <div key={x.id}>
                <strong>
                  {x.value} · {x.active ? "bloqueado" : "liberado"}
                </strong>
                <p>{reasons[x.reason] ?? x.reason}</p>
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      await mutate(p + "/suppression", "POST", {
                        value: x.value,
                        reason: x.reason,
                        active: !x.active,
                      });
                    }, "Bloqueio atualizado com auditoria.")
                  }
                >
                  {x.active ? "Liberar" : "Bloquear"}
                </button>
              </div>
            ))}
          </section>
        </div>
      )}
    </section>
  );
}
