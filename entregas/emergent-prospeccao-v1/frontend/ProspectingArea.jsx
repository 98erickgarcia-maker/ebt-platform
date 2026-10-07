import React, { useEffect, useRef, useState } from "react";
import "./prospecting.css";

const tabs = [
  "Painel",
  "Contatos",
  "Prospecção automática",
  "Templates",
  "Conexões",
  "Custos",
];
const statuses = {
  review: "Para revisar",
  qualified: "Qualificado",
  customer: "Cliente",
  discarded: "Descartado",
  suppressed: "Não contatar",
  scheduled: "Agendado",
  draft_created: "Rascunho no Outlook",
  accepted: "Aceito pelo provedor",
  sent_confirmed: "Envio confirmado pelo Outlook",
  needs_connection: "Conectar Outlook",
  needs_review: "Revisar novamente",
  unknown: "Resultado não confirmado",
  cancelled: "Cancelado",
  limit_reached: "Limite atingido",
  rejected: "Recusado",
};
const date = (v) =>
  v
    ? new Date(v.endsWith?.("Z") ? v : v + "Z").toLocaleString("pt-BR")
    : "Não informada";
const localDate = (d = new Date()) =>
  new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
const currency = (v) =>
  Number(v).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export default function ProspectingArea() {
  const [tab, setTab] = useState("Painel"),
    [summary, setSummary] = useState(null),
    [contacts, setContacts] = useState([]),
    [templates, setTemplates] = useState([]),
    [recipes, setRecipes] = useState([]),
    [messages, setMessages] = useState([]),
    [outlook, setOutlook] = useState({}),
    [wa, setWa] = useState({}),
    [waEvents, setWaEvents] = useState([]);
  const [search, setSearch] = useState(""),
    [filter, setFilter] = useState(""),
    [page, setPage] = useState(0),
    [selectedId, setSelectedId] = useState(""),
    [contact, setContact] = useState(null),
    [history, setHistory] = useState([]),
    [preview, setPreview] = useState(null),
    [loading, setLoading] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [dirty, setDirty] = useState(false);
  const [sender, setSender] = useState(""),
    [templateId, setTemplateId] = useState("presentation"),
    [due, setDue] = useState(localDate()),
    [editor, setEditor] = useState(null);
  const [recipe, setRecipe] = useState({
    name: "",
    uf: "",
    city: "",
    cnae: "",
    batch_size: 25,
    interval_hours: 24,
  });
  const [source, setSource] = useState({
      name: "Base empresarial",
      url: "",
      date: new Date().toISOString().slice(0, 10),
    }),
    [cost, setCost] = useState({
      current: "",
      hosting: "",
      llm: "",
      volume: 1000,
      waMessages: 0,
      waRate: "",
    });
  const [waForm, setWaForm] = useState({
    name: "",
    language: "pt_BR",
    parameters: "",
    opt_in_evidence: "",
    confirmation_phone: "",
  });
  const detailGeneration = useRef(0),
    selectedRef = useRef(""),
    detailAbort = useRef(null),
    listGeneration = useRef(0);

  async function api(path, method = "GET", body, signal) {
    const response = await fetch("/api/prospecting" + path, {
      method,
      credentials: "include",
      signal,
      headers: {
        "Content-Type": "application/json",
        ...(method === "GET" ? {} : { "X-EBT-Action": "prospecting" }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await response
      .json()
      .catch(() => ({ detail: "Resposta inválida do servidor." }));
    if (!response.ok)
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : `Não foi possível concluir (${response.status}). Confira os campos.`,
      );
    return data;
  }
  async function refresh() {
    const [s, t, r, m, o, w] = await Promise.all([
      api("/summary"),
      api("/templates"),
      api("/recipes"),
      api("/messages"),
      api("/outlook/status"),
      api("/whatsapp/status"),
    ]);
    setSummary(s);
    setTemplates(t.items);
    setRecipes(r.items);
    setMessages(m.items);
    setOutlook(o);
    setWa(w);
  }
  function clearDetail() {
    detailAbort.current?.abort();
    detailGeneration.current++;
    selectedRef.current = "";
    setSelectedId("");
    setContact(null);
    setHistory([]);
    setPreview(null);
    setDirty(false);
    setLoading(false);
  }
  async function reloadContacts() {
    const gen = ++listGeneration.current;
    const result = await api(
      `/contacts?search=${encodeURIComponent(search)}&status=${filter}&skip=${page * 50}`,
    );
    if (gen === listGeneration.current) setContacts(result.items);
  }
  useEffect(() => {
    refresh().catch((e) => setError(e.message));
    const timer = setInterval(() => refresh().catch(() => {}), 30000);
    return () => {
      clearInterval(timer);
      detailAbort.current?.abort();
    };
  }, []);
  useEffect(() => {
    clearDetail();
    reloadContacts().catch((e) => setError(e.message));
  }, [search, filter, page]);
  useEffect(() => {
    if (tab === "Conexões")
      api("/whatsapp/events")
        .then((r) => setWaEvents(r.items))
        .catch((e) => setError(e.message));
  }, [tab]);
  async function openContact(id) {
    detailAbort.current?.abort();
    const abort = new AbortController();
    detailAbort.current = abort;
    const gen = ++detailGeneration.current;
    selectedRef.current = id;
    setSelectedId(id);
    setContact(null);
    setHistory([]);
    setPreview(null);
    setDirty(false);
    setLoading(true);
    setError("");
    try {
      const [c, h] = await Promise.all([
        api("/contacts/" + id, "GET", undefined, abort.signal),
        api("/contacts/" + id + "/history", "GET", undefined, abort.signal),
      ]);
      if (gen === detailGeneration.current && selectedRef.current === id) {
        setContact(c);
        setHistory(h.items);
      }
    } catch (e) {
      if (e.name !== "AbortError" && gen === detailGeneration.current)
        setError(e.message);
    } finally {
      if (gen === detailGeneration.current) setLoading(false);
    }
  }
  async function action(fn, success = "Atualizado.") {
    setError("");
    setNotice("");
    setBusy(true);
    try {
      await fn();
      setNotice(success);
      await refresh();
      await reloadContacts();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  function changeContact(key, value) {
    setDirty(true);
    setContact((c) => ({ ...c, [key]: value }));
    setPreview(null);
  }
  async function saveContact() {
    const id = contact.id,
      gen = detailGeneration.current;
    const keys = [
      "version",
      "contact_name",
      "contact_role",
      "email",
      "email_quality",
      "phone",
      "website",
      "linkedin",
      "notes",
      "next_action",
      "next_action_at",
      "status",
    ];
    const data = Object.fromEntries(
      keys.filter((k) => contact[k] !== undefined).map((k) => [k, contact[k]]),
    );
    await api("/contacts/" + id, "PATCH", data);
    if (gen === detailGeneration.current && selectedRef.current === id)
      await openContact(id);
  }
  async function prepare() {
    const id = contact.id,
      gen = detailGeneration.current;
    const p = await api("/contacts/" + id + "/preview", "POST", {
      template_id: templateId,
      sender,
    });
    if (gen === detailGeneration.current && selectedRef.current === id)
      setPreview(p);
  }
  async function schedule(mode) {
    const p = preview;
    if (!p || p.contact_id !== contact?.id)
      throw new Error("Prepare a prévia do contato atual.");
    await api("/contacts/" + p.contact_id + "/schedule", "POST", {
      template_id: templateId,
      sender,
      digest: p.digest,
      due_at: new Date(due).toISOString(),
      mode,
    });
    setPreview(null);
  }
  async function openManualWhatsApp(target) {
    const p = preview,
      gen = detailGeneration.current;
    try {
      if (
        !p ||
        p.channel !== "whatsapp" ||
        p.contact_id !== selectedRef.current
      )
        throw new Error("Prepare o template do contato atual.");
      const result = await api(
        "/contacts/" + p.contact_id + "/whatsapp-manual",
        "POST",
        {
          template_id: templateId,
          sender,
          digest: p.digest,
        },
      );
      if (
        gen !== detailGeneration.current ||
        selectedRef.current !== p.contact_id
      )
        throw new Error("Contato alterado. Abra o template novamente.");
      target.location.href = result.url;
      const resultHistory = await api("/contacts/" + p.contact_id + "/history");
      if (
        gen === detailGeneration.current &&
        selectedRef.current === p.contact_id
      )
        setHistory(resultHistory.items);
    } catch (e) {
      target.close();
      throw e;
    }
  }
  async function importFile(file) {
    if (!file) return;
    if (file.size > 5_000_000) throw new Error("Arquivo deve ter até 5MB.");
    const rows = JSON.parse(await file.text());
    if (!Array.isArray(rows) || rows.length > 1000)
      throw new Error("Use um JSON com até 1.000 empresas por arquivo.");
    const result = await api("/catalog/import", "POST", { source, rows });
    if (result.rejected_count)
      throw new Error(
        `${result.accepted} registros importados; ${result.rejected_count} recusados. ${result.rejected[0]?.reason || ""}`,
      );
    setNotice(
      `${result.accepted} registros importados. As automações vão selecionar os contatos.`,
    );
  }
  const visibleContact =
    contact && contact.id === selectedId && !loading ? contact : null;
  const canAct = Boolean(visibleContact) && !busy && !loading;
  const newCost =
    Number(cost.hosting || 0) +
    Number(cost.llm || 0) +
    Number(cost.waMessages || 0) * Number(cost.waRate || 0);
  const knownBaseline = cost.current !== "" && cost.hosting !== "";
  return (
    <div className="ep-shell">
      <aside className="ep-nav">
        <div className="ep-brand">
          <span>EBT</span>
          <div>
            CONNECT<small>Relacionamento e prospecção</small>
          </div>
        </div>
        <div className="ep-nav-label">ESPAÇO COMERCIAL</div>
        <nav aria-label="Área de prospecção">
          {tabs.map((t) => (
            <button
              aria-label={t}
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => {
                setTab(t);
                setError("");
              }}
            >
              {t}
              <span>›</span>
            </button>
          ))}
        </nav>
        <div className="ep-nav-foot">
          <i /> Base e templates locais
          <small>Automação com custo controlado</small>
        </div>
      </aside>
      <main className="ep-main">
        <header className="ep-top">
          <div>
            <p>EBT ENTERPRISE / COMERCIAL</p>
            <h1>{tab}</h1>
          </div>
          <span className="ep-pill">E-mail + WhatsApp oficial</span>
        </header>
        {error && (
          <div role="alert" className="ep-alert">
            {error}
          </div>
        )}
        {notice && (
          <div role="status" className="ep-notice">
            {notice}
          </div>
        )}
        {tab === "Painel" && (
          <>
            <section className="ep-hero">
              <div>
                <span className="ep-eyebrow">SUA PRÓXIMA OPORTUNIDADE</span>
                <h2>
                  Mais contexto.
                  <br />O contato certo, na hora certa.
                </h2>
                <p>
                  Encontre empresas, revise os dados e prepare sua abordagem por
                  e-mail. Mantenha o próximo passo visível.
                </p>
                <button onClick={() => setTab("Prospecção automática")}>
                  Criar automação de prospecção <span>↗</span>
                </button>
              </div>
              <div className="ep-hero-stat">
                <strong>{summary?.review ?? "—"}</strong>
                <span>contatos para revisar</span>
                <small>
                  A base pública indica a origem.
                  <br />
                  Você confirma a qualidade.
                </small>
              </div>
            </section>
            <section className="ep-metrics">
              {[
                ["Empresas na base", summary?.catalog],
                ["Contatos", summary?.contacts],
                ["Qualificados", summary?.qualified],
                ["Retornos vencidos", summary?.overdue],
              ].map(([label, n]) => (
                <article key={label}>
                  <span>{label}</span>
                  <strong>{n ?? "—"}</strong>
                </article>
              ))}
            </section>
            <div className="ep-two">
              <section className="ep-panel">
                <h2>Próximas ações</h2>
                {contacts
                  .filter((c) => c.next_action)
                  .slice(0, 6)
                  .map((c) => (
                    <button
                      className="ep-task"
                      key={c.id}
                      onClick={() => {
                        setTab("Contatos");
                        openContact(c.id);
                      }}
                    >
                      <strong>{c.company_name}</strong>
                      <span>
                        {c.next_action} · {date(c.next_action_at)}
                      </span>
                    </button>
                  ))}
                {!contacts.some((c) => c.next_action) && (
                  <p className="ep-muted">
                    Abra um contato e defina o próximo passo.
                  </p>
                )}
              </section>
              <section className="ep-panel">
                <h2>Automação que cabe no orçamento</h2>
                <p>
                  Busca e templates usam a base local. Nenhuma chamada de IA é
                  necessária para prospectar.
                </p>
                <div className="ep-budget">
                  <strong>{summary?.budget.remaining ?? "—"}</strong>
                  <span>registros restantes neste mês</span>
                </div>
                <button
                  className="ep-secondary"
                  onClick={() => setTab("Custos")}
                >
                  Comparar custos
                </button>
              </section>
            </div>
          </>
        )}
        {tab === "Contatos" && (
          <>
            <div className="ep-toolbar">
              <input
                aria-label="Buscar contatos"
                placeholder="Buscar empresa, nome, CNPJ ou e-mail"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(0);
                }}
              />
              <select
                aria-label="Situação do contato"
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value);
                  setPage(0);
                }}
              >
                <option value="">Todas as situações</option>
                {Object.entries(statuses)
                  .slice(0, 6)
                  .map(([v, n]) => (
                    <option value={v} key={v}>
                      {n}
                    </option>
                  ))}
              </select>
              <a
                className="ep-secondary"
                href="/api/prospecting/contacts/export.csv"
              >
                Exportar 1.000 contatos
              </a>
            </div>
            <div className="ep-contacts">
              <section
                className="ep-contact-list"
                aria-label="Lista de contatos"
              >
                {contacts.map((c) => (
                  <button
                    aria-pressed={c.id === selectedId}
                    key={c.id}
                    className={
                      "ep-contact-row " +
                      (c.id === selectedId ? "selected" : "")
                    }
                    onClick={() => openContact(c.id)}
                  >
                    <span className="ep-avatar">
                      {c.company_name.slice(0, 2).toUpperCase()}
                    </span>
                    <span>
                      <strong>{c.company_name}</strong>
                      <small>
                        {c.city} · {c.uf} · {statuses[c.status]}
                      </small>
                      <small>
                        {c.contact_name || "Responsável a confirmar"}
                      </small>
                    </span>
                    <b>{c.score}</b>
                  </button>
                ))}
                {!contacts.length && (
                  <p className="ep-muted">
                    Sem contatos neste filtro. Importe a base e crie uma
                    automação.
                  </p>
                )}
                <div className="ep-pagination">
                  <button
                    disabled={!page}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    Anterior
                  </button>
                  <span>Página {page + 1}</span>
                  <button
                    disabled={contacts.length < 50}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Próxima
                  </button>
                </div>
              </section>
              <section className="ep-panel ep-detail" aria-busy={loading}>
                {loading ? (
                  <p>Carregando o contato selecionado…</p>
                ) : !visibleContact ? (
                  <div className="ep-empty">
                    <h2>Selecione um contato</h2>
                    <p>
                      Veja a origem, prepare sua mensagem e registre a próxima
                      ação.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="ep-detail-title">
                      <div>
                        <small>CNPJ {contact.cnpj}</small>
                        <h2>{contact.company_name}</h2>
                        <p>
                          {contact.city} / {contact.uf} · CNAE{" "}
                          {contact.cnae || "a confirmar"}
                        </p>
                      </div>
                      <span className="ep-score">
                        {contact.score}
                        <small>pontuação</small>
                      </span>
                    </div>
                    <div className="ep-links">
                      {Object.entries(contact.links || {}).map(([k, url]) => (
                        <a
                          key={k}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {
                            {
                              email: "E-mail direto",
                              phone: "Ligar",
                              whatsapp: "Abrir WhatsApp",
                              website: "Site",
                              linkedin: "LinkedIn",
                              maps: "Mapa",
                            }[k]
                          }{" "}
                          ↗
                        </a>
                      ))}
                    </div>
                    <div className="ep-source">
                      <strong>Origem: {contact.source.name}</strong>
                      <a
                        href={contact.source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Ver fonte ↗
                      </a>
                      <span>
                        Base de {contact.source.date} · E-mail{" "}
                        {contact.email_quality === "verified"
                          ? "verificado pelo responsável"
                          : "não verificado"}
                      </span>
                    </div>
                    <details>
                      <summary>Por que recebeu esta pontuação?</summary>
                      <ul>
                        {contact.score_reasons.map((reason) => (
                          <li key={reason}>{reason}</li>
                        ))}
                      </ul>
                    </details>
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        action(saveContact, "Cadastro salvo.");
                      }}
                    >
                      <div className="ep-grid">
                        <label>
                          Responsável
                          <input
                            value={contact.contact_name || ""}
                            onChange={(e) =>
                              changeContact("contact_name", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          Cargo
                          <input
                            value={contact.contact_role || ""}
                            onChange={(e) =>
                              changeContact("contact_role", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          E-mail
                          <input
                            type="email"
                            value={contact.email || ""}
                            onChange={(e) =>
                              changeContact("email", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          Telefone internacional
                          <input
                            value={contact.phone || ""}
                            onChange={(e) =>
                              changeContact("phone", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          Situação
                          <select
                            value={contact.status}
                            onChange={(e) =>
                              changeContact("status", e.target.value)
                            }
                          >
                            {Object.entries(statuses)
                              .slice(0, 6)
                              .map(([v, n]) => (
                                <option value={v} key={v}>
                                  {n}
                                </option>
                              ))}
                          </select>
                        </label>
                        <label>
                          Qualidade do e-mail
                          <select
                            value={contact.email_quality}
                            onChange={(e) =>
                              changeContact("email_quality", e.target.value)
                            }
                          >
                            <option value="unverified">Não verificado</option>
                            <option value="verified">Verificado por mim</option>
                            <option value="missing">Não informado</option>
                            <option value="invalid">Inválido</option>
                          </select>
                        </label>
                        <label>
                          Site
                          <input
                            value={contact.website || ""}
                            onChange={(e) =>
                              changeContact("website", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          LinkedIn
                          <input
                            value={contact.linkedin || ""}
                            onChange={(e) =>
                              changeContact("linkedin", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          Próxima ação
                          <input
                            value={contact.next_action || ""}
                            onChange={(e) =>
                              changeContact("next_action", e.target.value)
                            }
                          />
                        </label>
                        <label>
                          Data da próxima ação
                          <input
                            type="datetime-local"
                            value={
                              contact.next_action_at
                                ? localDate(
                                    new Date(
                                      contact.next_action_at.endsWith("Z")
                                        ? contact.next_action_at
                                        : contact.next_action_at + "Z",
                                    ),
                                  )
                                : ""
                            }
                            onChange={(e) =>
                              changeContact(
                                "next_action_at",
                                e.target.value
                                  ? new Date(e.target.value).toISOString()
                                  : null,
                              )
                            }
                          />
                        </label>
                      </div>
                      <label>
                        Observações
                        <textarea
                          value={contact.notes || ""}
                          onChange={(e) =>
                            changeContact("notes", e.target.value)
                          }
                        />
                      </label>
                      <button disabled={!canAct}>Salvar contato</button>
                    </form>
                    <section className="ep-composer">
                      <h3>Preparar abordagem</h3>
                      {dirty && (
                        <p className="ep-muted">
                          Salve as alterações do contato antes de preparar a
                          mensagem.
                        </p>
                      )}
                      <div className="ep-grid">
                        <label>
                          Seu nome para assinatura
                          <input
                            value={sender}
                            onChange={(e) => {
                              setSender(e.target.value);
                              setPreview(null);
                            }}
                          />
                        </label>
                        <label>
                          Template
                          <select
                            aria-label="Template"
                            value={templateId}
                            onChange={(e) => {
                              setTemplateId(e.target.value);
                              setPreview(null);
                            }}
                          >
                            {templates.map((t) => (
                              <option value={t.id} key={t.id}>
                                {t.name}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                      <button
                        disabled={!canAct || dirty || !sender.trim()}
                        onClick={() =>
                          action(
                            prepare,
                            "Prévia preparada. Confira o destinatário.",
                          )
                        }
                      >
                        {templates.find((t) => t.id === templateId)?.channel ===
                        "whatsapp"
                          ? "Preparar template WhatsApp"
                          : "Preparar e-mail"}
                      </button>
                      {preview && preview.contact_id === contact.id && (
                        <div className="ep-preview">
                          <strong>
                            Para:{" "}
                            {preview.channel === "whatsapp"
                              ? contact.phone || "Telefone ausente"
                              : preview.recipient || "E-mail ausente"}
                          </strong>
                          <h4>{preview.subject}</h4>
                          <pre>{preview.body}</pre>
                          <div className="ep-links">
                            {preview.channel === "email" &&
                              preview.links.email && (
                                <a href={preview.links.email}>
                                  Abrir no aplicativo de e-mail ↗
                                </a>
                              )}
                            {preview.channel === "whatsapp" &&
                              preview.links.whatsapp && (
                                <button
                                  disabled={!canAct || dirty}
                                  onClick={() => {
                                    const target = window.open(
                                      "about:blank",
                                      "_blank",
                                    );
                                    if (!target) {
                                      setError(
                                        "Permita abrir a conversa em uma nova aba.",
                                      );
                                      return;
                                    }
                                    target.opener = null;
                                    action(
                                      () => openManualWhatsApp(target),
                                      "Template manual aberto. Conclua o envio no WhatsApp.",
                                    );
                                  }}
                                >
                                  Enviar template manual no WhatsApp ↗
                                </button>
                              )}
                          </div>
                          {preview.channel === "whatsapp" && (
                            <small>
                              O clique abre a conversa com o texto pronto. O
                              envio manual é concluído no WhatsApp; o histórico
                              registra a preparação, sem presumir entrega.
                            </small>
                          )}
                          {preview.channel === "email" && (
                            <>
                              <label>
                                Agendar para
                                <input
                                  type="datetime-local"
                                  value={due}
                                  onChange={(e) => setDue(e.target.value)}
                                />
                              </label>
                              <div className="ep-actions">
                                <button
                                  disabled={!canAct || !preview.recipient}
                                  onClick={() =>
                                    action(
                                      () => schedule("draft"),
                                      "Rascunho agendado; acompanhe a fila.",
                                    )
                                  }
                                >
                                  Agendar rascunho no Outlook
                                </button>
                                {outlook.send_enabled && (
                                  <button
                                    className="ep-danger"
                                    disabled={
                                      !canAct ||
                                      contact.status !== "qualified" ||
                                      contact.email_quality !== "verified"
                                    }
                                    onClick={() => {
                                      if (
                                        window.confirm(
                                          `Confirmar envio agendado para ${preview.recipient}?\n${preview.subject}`,
                                        )
                                      )
                                        action(
                                          () => schedule("send"),
                                          "Envio aprovado e agendado.",
                                        );
                                    }}
                                  >
                                    Confirmar envio por e-mail
                                  </button>
                                )}
                              </div>
                              <small>
                                Rascunho não comprova envio. “Aceito” não
                                comprova entrega.
                              </small>
                            </>
                          )}
                        </div>
                      )}
                    </section>
                    {wa.send_enabled && (
                      <details>
                        <summary>Solicitar template oficial WhatsApp</summary>
                        <p>
                          Use o nome de um template aprovado na Meta e a
                          autorização do destinatário.
                        </p>
                        {Object.entries({
                          name: "Nome aprovado do template",
                          parameters: "Parâmetros do corpo, um por linha",
                          opt_in_evidence: "Evidência do opt-in",
                          confirmation_phone:
                            "Digite o telefone para confirmar",
                        }).map(([k, label]) => (
                          <label key={k}>
                            {label}
                            <input
                              value={waForm[k]}
                              onChange={(e) =>
                                setWaForm((f) => ({
                                  ...f,
                                  [k]: e.target.value,
                                }))
                              }
                            />
                          </label>
                        ))}
                        <button
                          disabled={!canAct}
                          onClick={() =>
                            action(
                              () =>
                                api(
                                  "/contacts/" +
                                    contact.id +
                                    "/whatsapp-template",
                                  "POST",
                                  {
                                    ...waForm,
                                    parameters: waForm.parameters
                                      .split("\n")
                                      .filter(Boolean),
                                    operation_id: crypto.randomUUID(),
                                  },
                                ),
                              "Solicitação registrada; veja eventos de entrega.",
                            )
                          }
                        >
                          Confirmar template oficial
                        </button>
                      </details>
                    )}
                    <section className="ep-history">
                      <h3>Fila e histórico</h3>
                      {messages
                        .filter((m) => m.contact_id === contact.id)
                        .map((m) => (
                          <article key={m.id}>
                            <strong>{statuses[m.status] || m.status}</strong>
                            <span>
                              {m.recipient} · {date(m.due_at)}
                            </span>
                            <a
                              href={
                                "/api/prospecting/messages/" +
                                m.id +
                                "/evidence.json"
                              }
                            >
                              Baixar evidência JSON
                            </a>
                            {m.web_link && (
                              <a
                                target="_blank"
                                rel="noopener noreferrer"
                                href={m.web_link}
                              >
                                Abrir no Outlook ↗
                              </a>
                            )}
                            {m.status === "scheduled" && (
                              <button
                                className="ep-secondary"
                                disabled={busy}
                                onClick={() =>
                                  action(() =>
                                    api(
                                      "/messages/" + m.id + "/cancel",
                                      "POST",
                                    ),
                                  )
                                }
                              >
                                Cancelar
                              </button>
                            )}
                            {m.error && <small>{m.error}</small>}
                          </article>
                        ))}
                      {history.map((h) => (
                        <article key={h.id}>
                          <span>{date(h.at)}</span>
                          <p>{h.description}</p>
                        </article>
                      ))}
                      <a
                        href={
                          "/api/prospecting/contacts/" +
                          contact.id +
                          "/history.json"
                        }
                      >
                        Baixar histórico JSON
                      </a>
                    </section>
                    <button
                      className="ep-danger ep-secondary"
                      disabled={!canAct}
                      onClick={() => {
                        const reason = window.prompt(
                          "Motivo para bloquear novos contatos:",
                        );
                        if (reason)
                          action(async () => {
                            await api(
                              "/contacts/" + contact.id + "/suppress",
                              "POST",
                              { reason },
                            );
                            await openContact(contact.id);
                          }, "Contato bloqueado e agendamentos cancelados.");
                      }}
                    >
                      Não contatar / cancelar retornos
                    </button>
                  </>
                )}
              </section>
            </div>
          </>
        )}
        {tab === "Prospecção automática" && (
          <>
            <section className="ep-panel">
              <h2>Encontrar empresas de forma econômica</h2>
              <p>
                Importe uma base empresarial com fonte e data. As automações
                buscam empresas ativas e criam contatos para revisão, sem gerar
                e-mails ou contatos repetidos.
              </p>
              <div className="ep-grid">
                <label>
                  Nome da fonte
                  <input
                    value={source.name}
                    onChange={(e) =>
                      setSource((s) => ({ ...s, name: e.target.value }))
                    }
                  />
                </label>
                <label>
                  URL da fonte
                  <input
                    type="url"
                    placeholder="https://…"
                    value={source.url}
                    onChange={(e) =>
                      setSource((s) => ({ ...s, url: e.target.value }))
                    }
                  />
                </label>
                <label>
                  Data da base
                  <input
                    type="date"
                    value={source.date}
                    onChange={(e) =>
                      setSource((s) => ({ ...s, date: e.target.value }))
                    }
                  />
                </label>
                <label>
                  Importar empresas (JSON, até 1.000)
                  <input
                    type="file"
                    accept=".json"
                    disabled={busy || !source.url}
                    onChange={(e) => {
                      const f = e.target.files[0];
                      action(() => importFile(f), "Importação concluída.");
                      e.target.value = "";
                    }}
                  />
                </label>
              </div>
              <small>
                O pacote inclui exemplo sintético e conversor CSV. Telefone
                público não comprova WhatsApp nem opt-in.
              </small>
            </section>
            <section className="ep-panel">
              <h2>Nova automação</h2>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  action(async () => {
                    await api("/recipes", "POST", recipe);
                    setRecipe((r) => ({ ...r, name: "" }));
                  }, "Automação salva. O worker fará o próximo lote.");
                }}
              >
                <div className="ep-grid">
                  <label>
                    Nome da automação
                    <input
                      required
                      value={recipe.name}
                      onChange={(e) =>
                        setRecipe((r) => ({ ...r, name: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    UF
                    <input
                      maxLength={2}
                      value={recipe.uf}
                      onChange={(e) =>
                        setRecipe((r) => ({
                          ...r,
                          uf: e.target.value.toUpperCase(),
                        }))
                      }
                    />
                  </label>
                  <label>
                    Município
                    <input
                      value={recipe.city}
                      onChange={(e) =>
                        setRecipe((r) => ({ ...r, city: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    CNAE ou prefixo
                    <input
                      maxLength={7}
                      value={recipe.cnae}
                      onChange={(e) =>
                        setRecipe((r) => ({
                          ...r,
                          cnae: e.target.value.replace(/\D/g, ""),
                        }))
                      }
                    />
                  </label>
                  <label>
                    Empresas por lote
                    <input
                      type="number"
                      min={1}
                      max={100}
                      value={recipe.batch_size}
                      onChange={(e) =>
                        setRecipe((r) => ({
                          ...r,
                          batch_size: Number(e.target.value),
                        }))
                      }
                    />
                  </label>
                  <label>
                    Intervalo em horas
                    <input
                      type="number"
                      min={1}
                      max={720}
                      value={recipe.interval_hours}
                      onChange={(e) =>
                        setRecipe((r) => ({
                          ...r,
                          interval_hours: Number(e.target.value),
                        }))
                      }
                    />
                  </label>
                </div>
                <button disabled={busy}>Salvar automação</button>
              </form>
            </section>
            <section className="ep-panel">
              <h2>Automações configuradas</h2>
              {recipes.map((r) => (
                <article className="ep-recipe" key={r.id}>
                  <div>
                    <strong>{r.name}</strong>
                    <p>
                      {r.uf || "Todas as UFs"} ·{" "}
                      {r.city || "Todos os municípios"} · CNAE{" "}
                      {r.cnae || "todos"}
                    </p>
                    <small>
                      {r.enabled ? "Ativa" : "Pausada"} · Próximo lote:{" "}
                      {date(r.next_run)}
                    </small>
                    <p>
                      {r.last_result?.new_contacts ?? 0} novos ·{" "}
                      {r.last_result?.duplicates ?? 0} duplicados
                      {r.last_result?.budget_reached
                        ? " · Orçamento atingido"
                        : ""}
                    </p>
                    {r.last_result?.error && <p>{r.last_result.error}</p>}
                  </div>
                  <div className="ep-actions">
                    <button
                      disabled={busy}
                      onClick={() =>
                        action(
                          () => api("/recipes/" + r.id + "/run", "POST"),
                          "Lote colocado na fila.",
                        )
                      }
                    >
                      Executar próximo lote
                    </button>
                    <button
                      className="ep-secondary"
                      disabled={busy}
                      onClick={() =>
                        action(() => api("/recipes/" + r.id + "/pause", "POST"))
                      }
                    >
                      Pausar
                    </button>
                  </div>
                </article>
              ))}
            </section>
          </>
        )}
        {tab === "Templates" && (
          <div className="ep-two">
            <section className="ep-panel">
              <h2>Biblioteca de mensagens</h2>
              <p>
                Apresentação, retorno, SST e WhatsApp. Variáveis:{" "}
                {
                  "{{company}}, {{first_name}}, {{contact_name}}, {{city}}, {{sender}}"
                }
                .
              </p>
              {templates.map((t) => (
                <button
                  className="ep-template"
                  key={t.id}
                  onClick={() => setEditor({ ...t })}
                >
                  <strong>{t.name}</strong>
                  <small>
                    {t.channel === "email" ? "E-mail" : "WhatsApp manual"} ·
                    versão {t.version}
                  </small>
                </button>
              ))}
            </section>
            <section className="ep-panel">
              {editor ? (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    action(async () => {
                      const t = await api("/templates/" + editor.id, "PUT", {
                        name: editor.name,
                        subject: editor.subject,
                        body: editor.body,
                        version: editor.version,
                      });
                      setEditor(t);
                      setPreview(null);
                    }, "Nova versão do template salva.");
                  }}
                >
                  <h2>Editar template</h2>
                  <label>
                    Nome
                    <input
                      value={editor.name}
                      onChange={(e) =>
                        setEditor((t) => ({ ...t, name: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    Assunto
                    <input
                      value={editor.subject}
                      onChange={(e) =>
                        setEditor((t) => ({ ...t, subject: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    Mensagem
                    <textarea
                      rows={14}
                      value={editor.body}
                      onChange={(e) =>
                        setEditor((t) => ({ ...t, body: e.target.value }))
                      }
                    />
                  </label>
                  <button disabled={busy}>Salvar nova versão</button>
                </form>
              ) : (
                <p>Selecione um template para editar.</p>
              )}
            </section>
          </div>
        )}
        {tab === "Conexões" && (
          <>
            <div className="ep-two">
              <section className="ep-panel">
                <span className="ep-eyebrow">CANAL PRINCIPAL</span>
                <h2>Microsoft Outlook</h2>
                <p>
                  Conecte sua conta para criar rascunhos reais e executar
                  e-mails aprovados e agendados.
                </p>
                <p>
                  <strong>
                    {outlook.email ||
                      (outlook.configured
                        ? "Configuração disponível"
                        : "Configuração Microsoft pendente")}
                  </strong>
                </p>
                <p>
                  Envio:{" "}
                  {outlook.send_enabled
                    ? "habilitado para mensagens aprovadas"
                    : "desativado no servidor"}{" "}
                  · limite {outlook.daily_email_limit || 20}/dia.
                </p>
                {outlook.automatic ? (
                  <p className="ep-muted">
                    Conexão automática com a configuração do disparador.{" "}
                    {outlook.connected
                      ? "Última operação validada pela API."
                      : "A primeira operação será validada pela API."}
                  </p>
                ) : outlook.connected ? (
                  <button
                    className="ep-secondary"
                    onClick={() =>
                      action(
                        () => api("/outlook/disconnect", "POST"),
                        "Conector desconectado no aplicativo.",
                      )
                    }
                  >
                    Desconectar Outlook
                  </button>
                ) : (
                  <button
                    disabled={busy || !outlook.configured}
                    onClick={() =>
                      action(async () => {
                        const result = await api("/outlook/connect", "POST");
                        location.assign(result.url);
                      }, "Autorização Microsoft iniciada.")
                    }
                  >
                    Conectar Outlook
                  </button>
                )}
              </section>
              <section className="ep-panel">
                <span className="ep-eyebrow">APRENDIZADO E INTEGRAÇÃO</span>
                <h2>WhatsApp Business API oficial</h2>
                <p>
                  Conector Cloud API, templates aprovados, webhook assinado e
                  evidências de envio, entrega e leitura.
                </p>
                <p>
                  <strong>
                    {wa.configured
                      ? "Conector configurado"
                      : "Configuração Meta pendente"}
                  </strong>
                </p>
                <p>
                  Envio:{" "}
                  {wa.send_enabled
                    ? "habilitado com confirmação"
                    : "desativado"}{" "}
                  · orçamento {currency(wa.budget_brl || 0)}.
                </p>
                <a
                  className="ep-secondary"
                  href="https://business.whatsapp.com/products/platform-pricing"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Consultar preços oficiais ↗
                </a>
                <p className="ep-muted">
                  Link wa.me abre o aplicativo. Ele não é API oficial e não
                  registra entrega.
                </p>
              </section>
            </div>
            <section className="ep-panel">
              <h2>Eventos do WhatsApp oficial</h2>
              {waEvents.map((e) => (
                <article className="ep-recipe" key={e.id}>
                  <div>
                    <strong>
                      {e.phone || "Evento"} · {e.kind}
                    </strong>
                    <p>{e.text}</p>
                    <small>{date(e.at)}</small>
                  </div>
                </article>
              ))}
              {!waEvents.length && (
                <p className="ep-muted">
                  Nenhum webhook recebido neste espaço.
                </p>
              )}
            </section>
          </>
        )}
        {tab === "Custos" && (
          <>
            <section className="ep-panel">
              <h2>Economia visível, sem estimativa inventada</h2>
              <p>
                Busca local e templates: {currency(0)} de API variável.
                Hospedagem, Microsoft 365, manutenção e tarifas Meta continuam
                separados.
              </p>
              <div className="ep-grid">
                <label>
                  Custo mensal atual (R$)
                  <input
                    type="number"
                    min={0}
                    value={cost.current}
                    onChange={(e) =>
                      setCost((c) => ({ ...c, current: e.target.value }))
                    }
                  />
                </label>
                <label>
                  Hospedagem e serviços incrementais (R$)
                  <input
                    type="number"
                    min={0}
                    value={cost.hosting}
                    onChange={(e) =>
                      setCost((c) => ({ ...c, hosting: e.target.value }))
                    }
                  />
                </label>
                <label>
                  Outros custos mensais (R$)
                  <input
                    type="number"
                    min={0}
                    value={cost.llm}
                    onChange={(e) =>
                      setCost((c) => ({ ...c, llm: e.target.value }))
                    }
                  />
                </label>
                <label>
                  Contatos por mês
                  <input
                    type="number"
                    min={1}
                    value={cost.volume}
                    onChange={(e) =>
                      setCost((c) => ({ ...c, volume: Number(e.target.value) }))
                    }
                  />
                </label>
                <label>
                  Mensagens WhatsApp cobradas
                  <input
                    type="number"
                    min={0}
                    value={cost.waMessages}
                    onChange={(e) =>
                      setCost((c) => ({
                        ...c,
                        waMessages: Number(e.target.value),
                      }))
                    }
                  />
                </label>
                <label>
                  Tarifa média WhatsApp (R$)
                  <input
                    type="number"
                    min={0}
                    step="0.001"
                    value={cost.waRate}
                    onChange={(e) =>
                      setCost((c) => ({ ...c, waRate: e.target.value }))
                    }
                  />
                </label>
              </div>
              <div className="ep-metrics">
                <article>
                  <span>Cenário informado</span>
                  <strong>{currency(newCost)}</strong>
                </article>
                <article>
                  <span>Custo por contato</span>
                  <strong>
                    {currency(newCost / Math.max(1, cost.volume))}
                  </strong>
                </article>
                <article>
                  <span>Economia mensal</span>
                  <strong>
                    {knownBaseline
                      ? currency(Number(cost.current) - newCost)
                      : "Informe a base"}
                  </strong>
                </article>
              </div>
              <small>
                Simulação com seus valores. Não é fatura nem cotação da Meta.
              </small>
            </section>
            <section className="ep-panel">
              <h2>Controle do processamento</h2>
              <p>
                {summary?.budget.processed ?? 0} de{" "}
                {summary?.budget.limit ?? 3000} registros processados no mês.
                Tentativas e duplicidades também consomem a cota.
              </p>
              <progress
                max={summary?.budget.limit || 3000}
                value={summary?.budget.processed || 0}
              />
              <p>
                IA: 0 chamadas. API paga de descoberta: 0 chamadas. Reaproveite
                a infraestrutura existente para evitar outra implantação.
              </p>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
