import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  api,
  ApiError,
  date,
  download,
  labels,
  resetContext,
  setAccess,
  route,
  stages,
  type Contact,
  type Conversation,
  type Document,
  type Me,
  type Member,
  type Message,
  type Note,
  type Organization,
  type Summary,
  type Task,
} from "./api";
import { parseContactsCsv, downloadContactsTemplate } from "./csv";
import { Brand } from "./Brand";

type View =
  "daily" | "contacts" | "tasks" | "messages" | "documents" | "settings";
function mergeMessages(current: Message[], incoming: Message[]) {
  const index = new Map(current.map((m) => [m.messageId, m]));
  for (const message of incoming) index.set(message.messageId, message);
  return [...index.values()].sort(
    (a, b) =>
      a.createdAt.localeCompare(b.createdAt) ||
      a.messageId.localeCompare(b.messageId),
  );
}
const views: { id: View; name: string; icon: string }[] = [
  { id: "daily", name: "Meu dia", icon: "grid" },
  { id: "contacts", name: "Relacionamentos", icon: "people" },
  { id: "tasks", name: "Tarefas", icon: "check" },
  { id: "messages", name: "Conversas", icon: "message" },
  { id: "documents", name: "Documentos", icon: "file" },
  { id: "settings", name: "Configurações", icon: "settings" },
];
function Icon({ name }: { name: string }) {
  const paths: Record<string, string> = {
    grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
    people:
      "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M16 3a4 4 0 0 1 0 8 M22 21v-2a4 4 0 0 0-3-4 M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
    check:
      "M9 11l3 3L22 4 M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11",
    message:
      "M21 15a3 3 0 0 1-3 3H8l-5 3V6a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3z M7 8h10 M7 12h7",
    file: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M8 13h8 M8 17h6",
    settings:
      "M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8 M12 2v3 M12 19v3 M2 12h3 M19 12h3 M5 5l2 2 M17 17l2 2 M5 19l2-2 M17 7l2-2",
    arrow: "M5 12h14 M13 6l6 6-6 6",
    plus: "M12 5v14 M5 12h14",
    search: "M21 21l-5-5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0",
    close: "M6 6l12 12 M6 18L18 6",
  };
  return (
    <svg
      aria-hidden="true"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={paths[name] ?? paths.arrow} />
    </svg>
  );
}
function Badge({ value }: { value: string }) {
  return (
    <span className={"badge badge-" + value}>{labels[value] ?? value}</span>
  );
}
function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <Icon name="file" />
      <strong>{title}</strong>
      <p>{children}</p>
    </div>
  );
}
function Modal({
  title,
  children,
  close,
  busy,
}: {
  title: string;
  children: ReactNode;
  close: () => void;
  busy: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    ref.current
      ?.querySelector<HTMLElement>("input,button,textarea,select")
      ?.focus();
    return () => previous?.focus();
  }, []);
  return (
    <div className="scrim" onClick={() => !busy && close()}>
      <div
        ref={ref}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => {
          if (e.key === "Escape" && !busy) close();
          if (e.key === "Tab") {
            const controls = ref.current?.querySelectorAll<HTMLElement>(
              "button:not(:disabled),input,select,textarea,a[href]",
            );
            if (controls?.length) {
              const first = controls[0],
                last = controls[controls.length - 1];
              if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
              } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
              }
            }
          }
        }}
      >
        <header>
          <h2 id="dialog-title">{title}</h2>
          <button
            aria-label="Fechar"
            className="icon-button"
            disabled={busy}
            onClick={close}
          >
            <Icon name="close" />
          </button>
        </header>
        {children}
      </div>
    </div>
  );
}
function Login({ onLogin }: { onLogin: (me: Me) => void }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const activation = new URLSearchParams(location.search).get("activation");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      if (activation)
        await api("/api/auth/activate", "POST", {
          token: activation,
          name: data.get("name"),
          password: data.get("password"),
        });
      else
        await api("/api/auth/login", "POST", {
          email: data.get("email"),
          password: data.get("password"),
        });
      resetContext();
      history.replaceState(null, "", location.pathname);
      onLogin(await api<Me>("/api/auth/me"));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login">
      <div className="login-story">
        <div className="brand">
          <Brand />
        </div>
        <div>
          <span className="eyebrow">RELACIONAMENTOS QUE AVANÇAM</span>
          <h1>
            Seu próximo passo.
            <br />
            <em>Em um só lugar.</em>
          </h1>
          <p>
            Contatos, conversas e compromissos conectados.
            <br />
            Uma visão clara do que precisa acontecer hoje.
          </p>
        </div>
        <span className="login-foot">
          EBT Enterprise • Plataforma de gestão
        </span>
      </div>
      <main className="login-form">
        <span className="eyebrow">SEU ESPAÇO DE TRABALHO</span>
        <h2>{activation ? "Ative seu acesso" : "Bem-vindo ao Connect"}</h2>
        <p>
          {activation
            ? "Crie sua senha para entrar na empresa que convidou você."
            : "Entre com o acesso autorizado pela sua empresa."}
        </p>
        <form onSubmit={submit}>
          {activation ? (
            <label>
              Seu nome
              <input name="name" autoComplete="name" required maxLength={120} />
            </label>
          ) : (
            <label>
              E-mail
              <input
                name="email"
                type="email"
                autoComplete="username"
                required
              />
            </label>
          )}
          <label>
            Senha
            <input
              name="password"
              type="password"
              autoComplete={activation ? "new-password" : "current-password"}
              minLength={activation ? 12 : undefined}
              required
            />
          </label>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          <button className="primary wide" disabled={busy}>
            {busy
              ? "Validando acesso…"
              : activation
                ? "Ativar e entrar"
                : "Entrar"}
            <Icon name="arrow" />
          </button>
        </form>
        <p className="small">
          Seu acesso determina a empresa e a carteira disponíveis.
        </p>
      </main>
    </div>
  );
}
type Dialog =
  | "contact"
  | "edit"
  | "organization"
  | "note"
  | "task"
  | "close"
  | "document"
  | "version"
  | "import"
  | "invite"
  | "reject"
  | null;
export function App() {
  const [me, setMe] = useState<Me | null>(null),
    [starting, setStarting] = useState(true);
  const [view, setView] = useState<View>("daily"),
    [menu, setMenu] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<Summary>({
    contacts: 0,
    openTasks: 0,
    overdue: 0,
    stages: [],
  });
  const [contacts, setContacts] = useState<Contact[]>([]),
    [total, setTotal] = useState(0),
    [page, setPage] = useState(1),
    [search, setSearch] = useState(""),
    [stage, setStage] = useState("");
  const [selected, setSelected] = useState<Contact | null>(null),
    [tasks, setTasks] = useState<Task[]>([]),
    [notes, setNotes] = useState<Note[]>([]),
    [docs, setDocs] = useState<Document[]>([]),
    [conversations, setConversations] = useState<Conversation[]>([]),
    [members, setMembers] = useState<Member[]>([]),
    [orgs, setOrgs] = useState<Organization[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null),
    [messages, setMessages] = useState<Message[]>([]),
    [messageVersion, setMessageVersion] = useState(""),
    [messageCursor, setMessageCursor] = useState<string | null>(null),
    [draft, setDraft] = useState("");
  const [documentVersions, setDocumentVersions] = useState<
    {
      number: number;
      fileName: string;
      reviewState: string;
      reviewReason: string;
      createdAt: string;
    }[]
  >([]);
  const [taskFilter, setTaskFilter] = useState("");
  const [taskOwner, setTaskOwner] = useState("");
  const [taskFrom, setTaskFrom] = useState("");
  const [taskTo, setTaskTo] = useState("");
  const [dialog, setDialog] = useState<Dialog>(null),
    [activeTask, setActiveTask] = useState<Task | null>(null),
    [activeDoc, setActiveDoc] = useState<Document | null>(null),
    [preview, setPreview] = useState<{
      id: string;
      payloadHash: string;
      rows: { externalKey: string; name: string }[];
    } | null>(null);
  const operationKey = useRef(crypto.randomUUID()),
    replyKey = useRef(crypto.randomUUID()),
    loadSequence = useRef(0),
    pagingStarted = useRef(false),
    [refresh, setRefresh] = useState(0),
    [audit, setAudit] = useState<
      { id: string; action: string; at: string; traceId: string }[]
    >([]),
    [credential, setCredential] = useState("");
  const writable = me?.role !== "reader",
    admin = me?.role === "admin";
  function conversationRecipient(item: Conversation | null) {
    if (!item) return "";
    if (!item.recipient?.trim()) return "";
    return item.recipient.startsWith("+")
      ? item.recipient
      : "+" + item.recipient;
  }
  function clearContactResources() {
    setTasks([]);
    setNotes([]);
    setDocs([]);
    setConversations([]);
    setConversation(null);
    setMessages([]);
    setMessageVersion("");
    setMessageCursor(null);
    setDraft("");
    setActiveTask(null);
    setActiveDoc(null);
    setDocumentVersions([]);
  }
  function openConversation(item: Conversation) {
    setConversation(item);
    setMessages([]);
    setMessageVersion("");
    setMessageCursor(null);
    setDraft("");
    setView("messages");
    setError("");
    replyKey.current = crypto.randomUUID();
  }
  useEffect(() => {
    api<Me>("/api/auth/me")
      .then(setMe)
      .catch((e) => {
        if (!(e instanceof ApiError && e.status === 401))
          setError((e as Error).message);
      })
      .finally(() => setStarting(false));
    const clearPrivate = () => {
      loadSequence.current++;
      setSelected(null);
      setConversation(null);
      setContacts([]);
      setTasks([]);
      setDocs([]);
      setNotes([]);
      setMessages([]);
      setMessageVersion("");
      setMessageCursor(null);
      setDraft("");
      setActiveTask(null);
      setActiveDoc(null);
      setCredential("");
      setMembers([]);
      setOrgs([]);
      setAudit([]);
      setDialog(null);
      setPreview(null);
      setDocumentVersions([]);
      setTaskFilter("");
      setTaskOwner("");
      setTaskFrom("");
      setTaskTo("");
      setSummary({ contacts: 0, openTasks: 0, overdue: 0, stages: [] });
      setView("daily");
      setSearch("");
      setStage("");
      setPage(1);
    };
    const unauthorized = () => {
      resetContext();
      clearPrivate();
      setMe(null);
    };
    const changed = () => {
      clearPrivate();
      setNotice("Seu acesso foi atualizado. Confira a empresa e a carteira.");
      void api<Me>("/api/auth/me").then(setMe).catch(unauthorized);
    };
    window.addEventListener("ebt:unauthorized", unauthorized);
    window.addEventListener("ebt:access-changed", changed);
    return () => {
      window.removeEventListener("ebt:unauthorized", unauthorized);
      window.removeEventListener("ebt:access-changed", changed);
    };
  }, []);
  useEffect(() => {
    if (me) setAccess(me);
  }, [me]);
  const selectedId = selected?.id;
  const load = useCallback(async () => {
    if (!me) return;
    const sequence = ++loadSequence.current;
    setLoading(true);
    try {
      const [s, c, t, d, conv, m, o] = await Promise.all([
        api<Summary>(route + "/summary"),
        api<{ items: Contact[]; total: number }>(
          route +
            "/contacts?" +
            new URLSearchParams({
              search,
              stage,
              page: String(page),
              limit: "25",
            }),
        ),
        api<Task[]>(
          route +
            "/tasks?" +
            new URLSearchParams(
              selectedId
                ? { contactId: selectedId }
                : view === "tasks"
                  ? {
                      ...(taskFilter ? { state: taskFilter } : {}),
                      ...(taskOwner ? { ownerId: taskOwner } : {}),
                      ...(taskFrom
                        ? {
                            dueFrom: new Date(
                              taskFrom + "T00:00:00",
                            ).toISOString(),
                          }
                        : {}),
                      ...(taskTo
                        ? {
                            dueTo: new Date(taskTo + "T00:00:00").toISOString(),
                          }
                        : {}),
                    }
                  : {},
            ),
        ),
        api<Document[]>(
          route + "/documents" + (selectedId ? "?contactId=" + selectedId : ""),
        ),
        api<Conversation[]>(
          route +
            "/conversations" +
            (selectedId ? "?contactId=" + selectedId : ""),
        ),
        api<Member[]>("/api/admin/members"),
        api<Organization[]>(route + "/organizations"),
      ]);
      if (sequence !== loadSequence.current) return;
      setSummary(s);
      setContacts(c.items);
      setTotal(c.total);
      setTasks(t);
      setDocs(d);
      setConversations(conv);
      setMembers(m);
      setOrgs(o);
      if (selectedId) {
        const [detail, history] = await Promise.all([
          api<Contact>(route + "/contacts/" + selectedId),
          api<Note[]>(route + "/contacts/" + selectedId + "/history"),
        ]);
        if (sequence !== loadSequence.current) return;
        setSelected(detail);
        setNotes(history);
      }
    } catch (e) {
      if (
        sequence === loadSequence.current &&
        !(e instanceof ApiError && e.code === "context_changed")
      )
        setError((e as Error).message);
    } finally {
      if (sequence === loadSequence.current) setLoading(false);
    }
  }, [
    me,
    selectedId,
    search,
    stage,
    page,
    view,
    taskFilter,
    taskOwner,
    taskFrom,
    taskTo,
  ]);
  useEffect(() => {
    void load();
  }, [load, refresh]);
  useEffect(() => {
    pagingStarted.current = false;
    setMessageVersion("");
    setMessageCursor(null);
  }, [conversation?.id]);
  useEffect(() => {
    if (!conversation) return;
    let active = true;
    const update = async () => {
      try {
        const result = await api<{
          items: Message[];
          version: string;
          nextCursor: string | null;
        }>(route + "/conversations/" + conversation.id + "/messages");
        if (active) {
          setMessages((current) => mergeMessages(current, result.items));
          setMessageVersion(result.version);
          if (!pagingStarted.current) setMessageCursor(result.nextCursor);
        }
      } catch (e) {
        if (active && !(e instanceof ApiError && e.code === "context_changed"))
          setError((e as Error).message);
      }
    };
    void update();
    const interval = window.setInterval(() => void update(), 5000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [conversation, refresh]);
  async function run(
    action: () => Promise<unknown>,
    message: string,
    close = true,
  ) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      if (close) {
        setDialog(null);
        setPreview(null);
      }
      setRefresh((x) => x + 1);
      setNotice(message);
    } catch (e) {
      if (!(e instanceof ApiError && e.code === "context_changed"))
        setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function navigate(next: View) {
    loadSequence.current++;
    clearContactResources();
    setView(next);
    // The same view must replace a load invalidated by navigation too.
    setRefresh((current) => current + 1);
    setMenu(false);
    setSelected(null);
    setError("");
    setCredential("");
  }
  function openContact(c: Contact) {
    loadSequence.current++;
    clearContactResources();
    setSelected(c);
    setView("contacts");
    setError("");
  }
  function show(kind: Dialog) {
    operationKey.current = crypto.randomUUID();
    setPreview(null);
    setDialog(kind);
    setError("");
  }
  async function switchContext(id: string) {
    setDocumentVersions([]);
    setTaskFilter("");
    setTaskOwner("");
    setTaskFrom("");
    setTaskTo("");
    await run(async () => {
      await api("/api/auth/context/" + id, "POST");
      resetContext();
      loadSequence.current++;
      setSelected(null);
      setConversation(null);
      setContacts([]);
      setTasks([]);
      setDocs([]);
      setNotes([]);
      setMessages([]);
      setMessageVersion("");
      setMessageCursor(null);
      setDraft("");
      setActiveTask(null);
      setActiveDoc(null);
      setCredential("");
      setSummary({ contacts: 0, openTasks: 0, overdue: 0, stages: [] });
      setMembers([]);
      setOrgs([]);
      setAudit([]);
      setPreview(null);
      setSearch("");
      setPage(1);
      setStage("");
      setMe(await api<Me>("/api/auth/me"));
    }, "Empresa selecionada.");
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const value = (name: string) => String(form.get(name) ?? "");
    const headers = { "Idempotency-Key": operationKey.current };
    if (dialog === "contact" || dialog === "edit") {
      const body = {
        name: value("name"),
        email: value("email"),
        phone: value("phone"),
        externalKey:
          selected && dialog === "edit"
            ? selected.externalKey
            : value("externalKey"),
        stage: value("stage"),
        organizationId: value("organizationId") || null,
        ownerId: value("ownerId") || me?.userId,
        portfolio: value("portfolio") || me?.portfolio,
      };
      await run(
        () =>
          api(
            route + "/contacts" + (dialog === "edit" ? "/" + selected!.id : ""),
            dialog === "edit" ? "PUT" : "POST",
            body,
            {
              ...headers,
              ...(dialog === "edit"
                ? { "If-Match": `"${selected!.version}"` }
                : {}),
            },
          ),
        "Contato salvo.",
      );
    } else if (dialog === "organization")
      await run(
        () =>
          api(route + "/organizations", "POST", {
            name: value("name"),
            externalKey: value("externalKey"),
            portfolio: me?.portfolio,
          }),
        "Organização cadastrada.",
      );
    else if (dialog === "note")
      await run(
        () =>
          api(
            route + "/contacts/" + selected!.id + "/history",
            "POST",
            {
              content: value("content"),
              occurredAt: value("occurredAt")
                ? new Date(value("occurredAt")).toISOString()
                : null,
            },
            headers,
          ),
        "Nota registrada no histórico interno.",
      );
    else if (dialog === "task")
      await run(
        () =>
          api(
            route + "/contacts/" + selected!.id + "/tasks",
            "POST",
            {
              title: value("title"),
              dueAt: new Date(value("dueAt")).toISOString(),
              ownerId: value("ownerId") || selected!.ownerId,
            },
            headers,
          ),
        "Tarefa criada. A próxima ação foi atualizada.",
      );
    else if (dialog === "close")
      await run(
        () =>
          api(
            route + "/tasks/" + activeTask!.id + "/close",
            "POST",
            { state: value("state"), result: value("result") },
            { ...headers, "If-Match": `"${activeTask!.version}"` },
          ),
        "Tarefa encerrada com resultado no histórico.",
      );
    else if (dialog === "reject")
      await run(
        () =>
          api(
            route + "/documents/" + activeDoc!.id + "/review",
            "POST",
            { state: "rejected", reason: value("reason") },
            { "If-Match": `"${activeDoc!.version}"` },
          ),
        "Documento rejeitado com motivo registrado.",
      );
    else if (dialog === "document" || dialog === "version")
      await run(
        () =>
          api(
            route +
              (dialog === "version"
                ? "/documents/" + activeDoc!.id + "/versions"
                : "/contacts/" + selected!.id + "/documents"),
            "POST",
            form,
            {
              ...headers,
              ...(dialog === "version"
                ? { "If-Match": `"${activeDoc!.version}"` }
                : {}),
            },
          ),
        "Arquivo salvo como versão privada, aguardando revisão.",
      );
    else if (dialog === "invite")
      await run(async () => {
        const invite = await api<{ activationToken: string }>(
          "/api/admin/invitations",
          "POST",
          {
            email: value("email"),
            role: value("role"),
            portfolio: value("portfolio"),
          },
        );
        setCredential(
          location.origin + "/?activation=" + invite.activationToken,
        );
      }, "Convite preparado. Compartilhe pelo canal autorizado.");
    else if (dialog === "import") {
      if (preview)
        await run(
          () =>
            api(
              route + "/imports/" + preview.id + "/confirm",
              "POST",
              { payloadHash: preview.payloadHash },
              headers,
            ),
          "Lote confirmado. Contatos e IDs persistidos.",
        );
      else
        await run(
          async () => {
            const file = form.get("csv");
            if (!(file instanceof File) || file.size < 1 || file.size > 131072)
              throw new Error("Selecione um CSV UTF-8 de até 128 KiB.");
            const rows = parseContactsCsv(await file.text());
            const result = await api<typeof preview>(
              route + "/imports/preview",
              "POST",
              { rows },
            );
            setPreview(result);
          },
          "Confira o preview antes de confirmar.",
          false,
        );
    }
  }
  async function sendReply(event: FormEvent) {
    event.preventDefault();
    if (!conversation) return;
    const recipient = conversationRecipient(conversation);
    if (!conversation.contactName.trim() || !recipient) {
      setError("Identifique o destinatário antes de confirmar a resposta.");
      return;
    }
    await run(
      async () => {
        const result = await api<{ status: string; version: string }>(
          route + "/conversations/" + conversation.id + "/messages",
          "POST",
          { content: draft, contentType: "text" },
          { "Idempotency-Key": replyKey.current, "If-Match": messageVersion },
        );
        setMessageVersion(result.version);
        setDraft("");
        replyKey.current = crypto.randomUUID();
      },
      "Resposta registrada na fila. A entrega depende da confirmação do canal.",
      false,
    );
  }
  function taskRows(rows: Task[]) {
    return rows.map((t) => (
      <article className="task-row" key={t.id}>
        <span
          className={
            "task-dot " +
            (t.state === "open" && new Date(t.dueAt) < new Date()
              ? "overdue"
              : "")
          }
        />
        <div>
          <strong>{t.title}</strong>
          <span>
            {date(t.dueAt)} ·{" "}
            {members.find((m) => m.userId === t.ownerId)?.name ?? "Responsável"}
          </span>
          {t.result && <p>{t.result}</p>}
        </div>
        <Badge value={t.state} />
        {writable && t.state === "open" && (
          <button
            className="secondary compact"
            onClick={() => {
              setActiveTask(t);
              show("close");
            }}
          >
            Encerrar
          </button>
        )}
      </article>
    ));
  }
  function docRows(rows: Document[]) {
    return rows.map((d) => (
      <article className="document-row" key={d.id}>
        <div className="file-icon">
          <Icon name="file" />
        </div>
        <div>
          <strong>{d.title}</strong>
          <span>Versão {d.currentVersion} · Documento comercial</span>
        </div>
        <Badge value={d.reviewState} />
        <div className="row-actions">
          <button
            className="text-button"
            onClick={() =>
              void run(
                async () => {
                  setActiveDoc(d);
                  setDocumentVersions(
                    await api(route + "/documents/" + d.id + "/versions"),
                  );
                },
                "Versões carregadas.",
                false,
              )
            }
          >
            Versões
          </button>
          {admin && d.reviewState === "pending" && (
            <button
              className="text-button"
              onClick={() => {
                setActiveDoc(d);
                show("reject");
              }}
            >
              Rejeitar
            </button>
          )}
          <button
            className="text-button"
            onClick={() =>
              void run(
                () =>
                  download(
                    route +
                      "/documents/" +
                      d.id +
                      "/download/" +
                      d.currentVersion,
                  ),
                "Arquivo baixado.",
                false,
              )
            }
          >
            Baixar
          </button>
          {writable && (
            <button
              className="text-button"
              onClick={() => {
                setActiveDoc(d);
                show("version");
              }}
            >
              Nova versão
            </button>
          )}
          {admin && d.reviewState === "pending" && (
            <button
              className="secondary compact"
              disabled={busy}
              onClick={() =>
                void run(
                  () =>
                    api(
                      route + "/documents/" + d.id + "/review",
                      "POST",
                      { state: "approved" },
                      { "If-Match": `"${d.version}"` },
                    ),
                  "Documento aprovado.",
                  false,
                )
              }
            >
              Aprovar
            </button>
          )}
        </div>
      </article>
    ));
  }
  if (starting)
    return (
      <div className="boot" role="status">
        Preparando seu espaço de trabalho…
      </div>
    );
  if (!me)
    return (
      <>
        <Login onLogin={setMe} />
        {error && (
          <div className="login-error" role="alert">
            {error}
          </div>
        )}
      </>
    );
  const currentView = views.find((v) => v.id === view)!;
  return (
    <div className="workspace">
      <aside className={"sidebar " + (menu ? "mobile-open" : "")}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("daily");
          }}
        >
          <Brand />
        </a>
        <span className="nav-label">ESPAÇO DE TRABALHO</span>
        <nav aria-label="Navegação principal">
          {views
            .filter((v) => v.id !== "settings" || admin)
            .map((v) => (
              <button
                key={v.id}
                className={view === v.id ? "active" : ""}
                aria-current={view === v.id ? "page" : undefined}
                onClick={() => navigate(v.id)}
              >
                <Icon name={v.icon} />
                {v.name}
                {v.id === "tasks" && summary.openTasks > 0 && (
                  <span className="nav-count">{summary.openTasks}</span>
                )}
              </button>
            ))}
        </nav>
        <div className="sidebar-bottom">
          <span className="avatar">{me.name[0]}</span>
          <div>
            <strong>{me.name}</strong>
            <span>{labels[me.role]}</span>
          </div>
          <button
            aria-label="Sair"
            title="Sair"
            className="icon-button"
            onClick={() =>
              void run(async () => {
                await api("/api/auth/logout", "POST");
                resetContext();
                setMe(null);
                setContacts([]);
                setSelected(null);
                setMessages([]);
                setCredential("");
              }, "")
            }
          >
            <Icon name="arrow" />
          </button>
        </div>
      </aside>
      <div className="main-area">
        <header className="topbar">
          <button
            className="mobile-menu icon-button"
            aria-label="Abrir navegação"
            onClick={() => setMenu(!menu)}
          >
            <Icon name="grid" />
          </button>
          <div className="breadcrumb">
            Plataforma <span>/</span> <strong>Connect</strong>
          </div>
          <label className="context-picker">
            <span>Empresa</span>
            <select
              aria-label="Empresa"
              value={me.tenantId}
              disabled={busy}
              onChange={(e) => void switchContext(e.target.value)}
            >
              {me.tenants.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </label>
          <span className="portfolio">Carteira: {me.portfolio}</span>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <span className="eyebrow">
                {selected ? "RELACIONAMENTO" : "EBT CONNECT"}
              </span>
              <h1>{selected ? selected.name : currentView.name}</h1>
              <p>
                {selected
                  ? "Um contato, um histórico e próximos passos claros."
                  : {
                      daily: "Uma visão clara do que importa agora.",
                      contacts:
                        "Cada relacionamento com contexto e continuidade.",
                      tasks: "Compromissos com responsável, prazo e resultado.",
                      messages:
                        "Acompanhe a conversa e confirme cada resposta.",
                      documents:
                        "Arquivos comerciais privados, com revisão e versões.",
                      settings: "Acessos e registros da sua empresa.",
                    }[view]}
              </p>
            </div>
            <div className="heading-actions">
              <button
                className="secondary"
                disabled={loading || busy}
                onClick={() => setRefresh((x) => x + 1)}
              >
                Atualizar
              </button>
              {writable && (view === "daily" || view === "contacts") && (
                <button className="primary" onClick={() => show("contact")}>
                  <Icon name="plus" />
                  Novo contato
                </button>
              )}
            </div>
          </div>
          {error && !dialog && (
            <div className="alert error" role="alert">
              {error}
              <button aria-label="Fechar aviso" onClick={() => setError("")}>
                <Icon name="close" />
              </button>
            </div>
          )}
          {notice && (
            <div className="alert success" role="status">
              {notice}
              <button
                aria-label="Fechar confirmação"
                onClick={() => setNotice("")}
              >
                <Icon name="close" />
              </button>
            </div>
          )}
          {loading && (
            <div className="loading-bar" role="status">
              Atualizando dados…
            </div>
          )}
          {view === "daily" && (
            <>
              <div className="welcome-card">
                <div>
                  <span className="eyebrow">SEU DIA, COM DIREÇÃO</span>
                  <h2>
                    Olá, {me.name.split(" ")[0]}.<br />
                    Vamos dar o próximo passo.
                  </h2>
                  <p>
                    {summary.overdue
                      ? `${summary.overdue} compromisso(s) precisam de atenção.`
                      : "Acompanhe seus compromissos e avance suas conversas."}
                  </p>
                  <button
                    className="text-button"
                    onClick={() => navigate("tasks")}
                  >
                    Ver minha agenda <Icon name="arrow" />
                  </button>
                </div>
                <div className="welcome-graphic" aria-hidden="true">
                  <div className="orbit">
                    <span className="orbit-center">E</span>
                    <span className="orbit-node node-one">
                      <Icon name="people" />
                    </span>
                    <span className="orbit-node node-two">
                      <Icon name="message" />
                    </span>
                    <span className="orbit-node node-three">
                      <Icon name="check" />
                    </span>
                  </div>
                </div>
              </div>
              <div className="metrics">
                <button onClick={() => navigate("contacts")}>
                  <span>Relacionamentos</span>
                  <strong>{summary.contacts}</strong>
                  <small>
                    Contatos na sua carteira <Icon name="arrow" />
                  </small>
                </button>
                <button onClick={() => navigate("tasks")}>
                  <span>Próximos compromissos</span>
                  <strong>{summary.openTasks}</strong>
                  <small>
                    Tarefas em aberto <Icon name="arrow" />
                  </small>
                </button>
                <button
                  className={summary.overdue ? "attention" : ""}
                  onClick={() => navigate("tasks")}
                >
                  <span>Precisam de atenção</span>
                  <strong>{summary.overdue}</strong>
                  <small>
                    Prazos vencidos <Icon name="arrow" />
                  </small>
                </button>
              </div>
              <div className="dashboard-grid">
                <section className="card">
                  <header>
                    <h2>Próximas ações</h2>
                    <button
                      className="text-button"
                      onClick={() => navigate("tasks")}
                    >
                      Ver todas
                    </button>
                  </header>
                  {tasks.filter((t) => t.state === "open").length ? (
                    taskRows(
                      tasks.filter((t) => t.state === "open").slice(0, 5),
                    )
                  ) : (
                    <Empty title="Sua agenda está em dia">
                      Crie uma tarefa no contato para definir o próximo passo.
                    </Empty>
                  )}
                </section>
                <section className="card">
                  <header>
                    <h2>Relacionamentos por etapa</h2>
                  </header>
                  <div className="stage-list">
                    {stages.map((s) => (
                      <button
                        key={s}
                        onClick={() => {
                          navigate("contacts");
                          setStage(s);
                        }}
                      >
                        <Badge value={s} />
                        <strong>
                          {summary.stages.find((x) => x.stage === s)?.count ??
                            0}
                        </strong>
                      </button>
                    ))}
                  </div>
                </section>
              </div>
            </>
          )}
          {view === "contacts" && !selected && (
            <section className="card">
              <div className="toolbar">
                <label className="search">
                  <Icon name="search" />
                  <input
                    aria-label="Buscar contatos"
                    placeholder="Buscar por nome, e-mail ou telefone"
                    value={search}
                    onChange={(e) => {
                      setSearch(e.target.value);
                      setPage(1);
                    }}
                  />
                </label>
                <select
                  aria-label="Filtrar etapa"
                  value={stage}
                  onChange={(e) => {
                    setStage(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">Todas as etapas</option>
                  {stages.map((s) => (
                    <option key={s} value={s}>
                      {labels[s]}
                    </option>
                  ))}
                </select>
                {writable && (
                  <>
                    <button
                      className="secondary"
                      onClick={() => show("organization")}
                    >
                      Organização
                    </button>
                    <button
                      className="secondary"
                      onClick={() => show("import")}
                    >
                      Importar
                    </button>
                  </>
                )}
              </div>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Contato</th>
                      <th>Etapa</th>
                      <th>Responsável</th>
                      <th>Próxima ação</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {contacts.map((c) => (
                      <tr key={c.id}>
                        <td>
                          <button
                            className="contact-link"
                            onClick={() => openContact(c)}
                          >
                            <span className="avatar light">{c.name[0]}</span>
                            <span>
                              <strong>{c.name}</strong>
                              <small>
                                {c.email ||
                                  (c.phone
                                    ? "+" + c.phone
                                    : "Sem e-mail ou telefone")}
                              </small>
                            </span>
                          </button>
                        </td>
                        <td>
                          <Badge value={c.stage} />
                        </td>
                        <td>
                          {members.find((m) => m.userId === c.ownerId)?.name ??
                            "Responsável"}
                        </td>
                        <td>
                          {c.nextAction ? (
                            <>
                              <strong className="table-action">
                                {c.nextAction.title}
                              </strong>
                              <small>{date(c.nextAction.dueAt)}</small>
                            </>
                          ) : (
                            <span className="muted">Definir próximo passo</span>
                          )}
                        </td>
                        <td>
                          <button
                            aria-label={"Abrir " + c.name}
                            className="icon-button"
                            onClick={() => openContact(c)}
                          >
                            <Icon name="arrow" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {!contacts.length && (
                <Empty title="Nenhum contato encontrado">
                  Ajuste os filtros ou cadastre seu primeiro relacionamento.
                </Empty>
              )}
              <footer className="pagination">
                <span>
                  {total} contato(s) · Página {page}
                </span>
                <div>
                  <button
                    className="secondary compact"
                    disabled={page === 1 || loading}
                    onClick={() => setPage(page - 1)}
                  >
                    Anterior
                  </button>
                  <button
                    className="secondary compact"
                    disabled={page * 25 >= total || loading}
                    onClick={() => setPage(page + 1)}
                  >
                    Próxima
                  </button>
                </div>
              </footer>
            </section>
          )}
          {view === "contacts" && selected && (
            <>
              <button
                className="back text-button"
                onClick={() => {
                  loadSequence.current++;
                  clearContactResources();
                  setSelected(null);
                }}
              >
                ← Voltar aos relacionamentos
              </button>
              <div className="detail-grid">
                <section className="card contact-card">
                  <span className="avatar large">{selected.name[0]}</span>
                  <h2>{selected.name}</h2>
                  <Badge value={selected.stage} />
                  <dl>
                    <dt>E-mail</dt>
                    <dd>{selected.email || "Não informado"}</dd>
                    <dt>Telefone</dt>
                    <dd>
                      {selected.phone ? "+" + selected.phone : "Não informado"}
                    </dd>
                    <dt>Organização</dt>
                    <dd>
                      {orgs.find((o) => o.id === selected.organizationId)
                        ?.name ?? "Não vinculada"}
                    </dd>
                    <dt>Responsável</dt>
                    <dd>
                      {members.find((m) => m.userId === selected.ownerId)
                        ?.name ?? "Responsável"}
                    </dd>
                    <dt>Carteira</dt>
                    <dd>{selected.portfolio}</dd>
                    <dt>ID do contato</dt>
                    <dd className="mono small">{selected.id}</dd>
                  </dl>
                  {writable && (
                    <button
                      className="secondary wide"
                      onClick={() => show("edit")}
                    >
                      Editar cadastro e etapa
                    </button>
                  )}
                  <div className="next-action">
                    <span className="eyebrow">PRÓXIMO PASSO</span>
                    <strong>
                      {selected.nextAction?.title ?? "Nenhuma tarefa aberta"}
                    </strong>
                    {selected.nextAction && (
                      <span>{date(selected.nextAction.dueAt)}</span>
                    )}
                    {writable && (
                      <button
                        className="text-button"
                        onClick={() => show("task")}
                      >
                        Criar tarefa <Icon name="plus" />
                      </button>
                    )}
                  </div>
                </section>
                <div className="detail-content">
                  <section className="card">
                    <header>
                      <h2>Histórico do relacionamento</h2>
                      {writable && (
                        <button
                          className="secondary compact"
                          onClick={() => show("note")}
                        >
                          Registrar nota
                        </button>
                      )}
                    </header>
                    {notes.length ? (
                      <div className="timeline">
                        {notes.map((n) => (
                          <article key={n.id}>
                            <span className="timeline-dot" />
                            <div>
                              <small>
                                {date(n.occurredAt)} ·{" "}
                                {members.find((m) => m.userId === n.actorId)
                                  ?.name ?? "Autor registrado"}
                              </small>
                              <p>{n.content}</p>
                              <span className="small muted">
                                {n.kind === "note"
                                  ? "Nota interna"
                                  : "Registro de atividade"}
                              </span>
                            </div>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <Empty title="O histórico começa aqui">
                        Registre uma nota interna ou conclua uma tarefa.
                      </Empty>
                    )}
                  </section>
                  <section className="card">
                    <header>
                      <h2>Tarefas do contato</h2>
                      {writable && (
                        <button
                          className="secondary compact"
                          onClick={() => show("task")}
                        >
                          Nova tarefa
                        </button>
                      )}
                    </header>
                    {tasks.length ? (
                      taskRows(tasks)
                    ) : (
                      <Empty title="Nenhuma tarefa">
                        Defina um compromisso com prazo e responsável.
                      </Empty>
                    )}
                  </section>
                  <section className="card">
                    <header>
                      <h2>Conversas</h2>
                    </header>
                    {conversations.length ? (
                      conversations.map((c) => (
                        <button
                          className="conversation-preview"
                          key={c.id}
                          onClick={() => openConversation(c)}
                        >
                          <Icon name="message" />
                          <div>
                            <strong>{c.channelName}</strong>
                            <span>
                              {c.lastInboundAt
                                ? "Última entrada: " + date(c.lastInboundAt)
                                : "Sem mensagem recebida"}
                            </span>
                          </div>
                          <Icon name="arrow" />
                        </button>
                      ))
                    ) : (
                      <Empty title="Sem conversa vinculada">
                        As mensagens recebidas por um canal configurado
                        aparecerão aqui.
                      </Empty>
                    )}
                  </section>
                  <section className="card">
                    <header>
                      <h2>Documentos comerciais</h2>
                      {writable && (
                        <button
                          className="secondary compact"
                          onClick={() => show("document")}
                        >
                          Enviar arquivo
                        </button>
                      )}
                    </header>
                    {docs.length ? (
                      docRows(docs)
                    ) : (
                      <Empty title="Nenhum documento">
                        Envie um PDF ou texto comercial para revisão.
                      </Empty>
                    )}
                  </section>
                </div>
              </div>
            </>
          )}
          {view === "tasks" && (
            <section className="card">
              <header>
                <h2>Agenda e resultados</h2>
                <span className="small muted">
                  Crie tarefas dentro de um relacionamento
                </span>
              </header>
              <label className="task-filter">
                Situação
                <select
                  value={taskFilter}
                  onChange={(e) => setTaskFilter(e.target.value)}
                >
                  <option value="">Todas</option>
                  <option value="open">Abertas</option>
                  <option value="done">Concluídas</option>
                  <option value="cancelled">Canceladas</option>
                </select>
              </label>
              <div className="task-filters">
                <label>
                  Responsável
                  <select
                    value={taskOwner}
                    onChange={(e) => setTaskOwner(e.target.value)}
                  >
                    <option value="">Todos</option>
                    {members
                      .filter(
                        (m) =>
                          m.active && ["admin", "operator"].includes(m.role),
                      )
                      .map((m) => (
                        <option key={m.userId} value={m.userId}>
                          {m.name}
                        </option>
                      ))}
                  </select>
                </label>
                <label>
                  Desde
                  <input
                    type="date"
                    value={taskFrom}
                    onChange={(e) => setTaskFrom(e.target.value)}
                  />
                </label>
                <label>
                  Antes de
                  <input
                    type="date"
                    value={taskTo}
                    onChange={(e) => setTaskTo(e.target.value)}
                  />
                </label>
              </div>
              <p className="small muted">
                Até 100 compromissos por consulta. Use os filtros para delimitar
                o período.
              </p>
              {tasks.length ? (
                taskRows(tasks)
              ) : (
                <Empty title="Nenhum compromisso registrado">
                  Abra um contato para definir sua próxima ação.
                </Empty>
              )}
            </section>
          )}
          {view === "messages" && (
            <div className="inbox">
              <section className="card conversation-list">
                <header>
                  <h2>Conversas</h2>
                </header>
                {conversations.length ? (
                  conversations.map((c) => (
                    <button
                      key={c.id}
                      className={conversation?.id === c.id ? "selected" : ""}
                      onClick={() => openConversation(c)}
                    >
                      <span className="avatar light">
                        <Icon name="message" />
                      </span>
                      <div>
                        <strong>
                          {c.contactName || "Destinatário não identificado"}
                        </strong>
                        <span>
                          {c.channelName}
                          {conversationRecipient(c)
                            ? " · " + conversationRecipient(c)
                            : " · sem referência de destinatário"}
                        </span>
                      </div>
                    </button>
                  ))
                ) : (
                  <Empty title="Sem conversas">
                    Configure um canal para receber mensagens.
                  </Empty>
                )}
              </section>
              <section className="card conversation-panel">
                {conversation ? (
                  <>
                    <header>
                      <div>
                        <h2>
                          {conversation.contactName ||
                            "Destinatário não identificado"}
                        </h2>
                        <span className="small muted">
                          {conversation.channelName}
                          {conversationRecipient(conversation)
                            ? " · " + conversationRecipient(conversation)
                            : " · sem referência de destinatário"}
                          {conversation.provider === "qa"
                            ? " · Teste local, sem envio real"
                            : ""}
                        </span>
                      </div>
                      <Badge value={conversation.state} />
                    </header>
                    <div className="messages" aria-live="polite">
                      {messages.length ? (
                        messages.map((m) => (
                          <article
                            className={"message " + m.direction}
                            key={m.messageId}
                          >
                            <p>{m.content}</p>
                            <div>
                              <time>{date(m.createdAt)}</time>
                              <Badge value={m.status} />
                            </div>
                            {m.failureCode && (
                              <small>
                                {m.status === "unknown"
                                  ? "Confirme o resultado no canal antes de decidir um novo envio."
                                  : "O canal informou falha ou a política impediu o envio."}
                              </small>
                            )}
                          </article>
                        ))
                      ) : (
                        <Empty title="Conversa pronta para acompanhamento">
                          As mensagens recebidas e respostas confirmadas
                          aparecerão aqui.
                        </Empty>
                      )}
                      {messageCursor && (
                        <button
                          className="secondary"
                          onClick={() =>
                            void run(
                              async () => {
                                const next = await api<{
                                  items: Message[];
                                  nextCursor: string | null;
                                }>(
                                  route +
                                    "/conversations/" +
                                    conversation.id +
                                    "/messages?cursor=" +
                                    messageCursor,
                                );
                                pagingStarted.current = true;
                                setMessages((current) =>
                                  mergeMessages(current, next.items),
                                );
                                setMessageCursor(next.nextCursor);
                              },
                              "",
                              false,
                            )
                          }
                        >
                          Carregar mensagens anteriores
                        </button>
                      )}
                    </div>
                    {writable ? (
                      <form className="reply" onSubmit={sendReply}>
                        <label htmlFor="reply">
                          Resposta para{" "}
                          {conversation.contactName ||
                            "destinatário não identificado"}
                        </label>
                        <span className="small muted">
                          Destinatário:{" "}
                          {conversationRecipient(conversation) ||
                            "não identificado — confirme o cadastro antes de responder"}
                        </span>
                        <textarea
                          id="reply"
                          placeholder="Escreva sua resposta…"
                          value={draft}
                          maxLength={4000}
                          required
                          onChange={(e) => {
                            if (draft !== e.target.value)
                              replyKey.current = crypto.randomUUID();
                            setDraft(e.target.value);
                          }}
                        />
                        <footer>
                          <span>Confira o texto antes de confirmar.</span>
                          <button
                            className="primary"
                            disabled={
                              busy ||
                              !messageVersion ||
                              !draft.trim() ||
                              !conversation.contactName.trim() ||
                              !conversationRecipient(conversation)
                            }
                          >
                            Confirmar resposta <Icon name="arrow" />
                          </button>
                        </footer>
                      </form>
                    ) : (
                      <div className="read-only">
                        Seu perfil permite acompanhar a conversa.
                      </div>
                    )}
                  </>
                ) : (
                  <Empty title="Selecione uma conversa">
                    Mensagens e respostas ficam vinculadas ao contato correto.
                  </Empty>
                )}
              </section>
            </div>
          )}
          {view === "documents" && (
            <section className="card">
              <header>
                <h2>Biblioteca comercial</h2>
                <span className="small muted">
                  Envie novos arquivos pelo contato
                </span>
              </header>
              {docs.length ? (
                docRows(docs)
              ) : (
                <Empty title="Nenhum arquivo comercial">
                  Documentos privados, revisões e versões serão exibidos aqui.
                </Empty>
              )}
            </section>
          )}
          {view === "settings" && admin && (
            <div className="settings-grid">
              <section className="card">
                <header>
                  <h2>Equipe e acesso</h2>
                  <button
                    className="primary compact"
                    onClick={() => show("invite")}
                  >
                    Preparar convite
                  </button>
                </header>
                {members.map((m) => (
                  <article className="member-row" key={m.id}>
                    <span className="avatar light">{m.name[0]}</span>
                    <div>
                      <strong>{m.name}</strong>
                      <span>{m.portfolio}</span>
                    </div>
                    <select
                      aria-label={"Perfil de " + m.name}
                      value={m.role}
                      disabled={busy}
                      onChange={(e) =>
                        void run(
                          () =>
                            api(
                              "/api/admin/members/" + m.id,
                              "PUT",
                              {
                                role: e.target.value,
                                portfolio: m.portfolio,
                                active: m.active,
                              },
                              { "If-Match": `"${m.version}"` },
                            ),
                          "Perfil atualizado.",
                          false,
                        )
                      }
                    >
                      <option value="admin">Administrador</option>
                      <option value="operator">Operador</option>
                      <option value="reader">Consulta</option>
                      <option value="support">Suporte técnico</option>
                    </select>
                    <button
                      className="secondary compact"
                      disabled={busy}
                      onClick={() =>
                        void run(
                          () =>
                            api(
                              "/api/admin/members/" + m.id,
                              "PUT",
                              {
                                role: m.role,
                                portfolio: m.portfolio,
                                active: !m.active,
                              },
                              { "If-Match": `"${m.version}"` },
                            ),
                          m.active ? "Acesso desativado." : "Acesso reativado.",
                          false,
                        )
                      }
                    >
                      {m.active ? "Desativar" : "Reativar"}
                    </button>
                  </article>
                ))}
                <p className="small muted settings-note">
                  O convite é individual e expira em 48 horas. A preparação não
                  envia e-mail.
                </p>
              </section>
              <section className="card">
                <header>
                  <h2>Integração por API</h2>
                </header>
                <div className="settings-note">
                  <p>
                    Crie uma chave temporária vinculada ao seu acesso. Ela vale
                    apenas para a API Connect da empresa selecionada.
                  </p>
                  <button
                    className="secondary"
                    disabled={busy}
                    onClick={() =>
                      void run(
                        async () => {
                          const key = await api<{ token: string }>(
                            "/api/admin/api-keys",
                            "POST",
                          );
                          setCredential(key.token);
                        },
                        "Chave criada. Guarde em local seguro; ela será exibida apenas nesta sessão.",
                        false,
                      )
                    }
                  >
                    Criar chave de API
                  </button>
                  {credential && (
                    <label className="credential">
                      Chave ou link preparado
                      <textarea
                        readOnly
                        value={credential}
                        onFocus={(e) => e.target.select()}
                      />
                    </label>
                  )}
                </div>
              </section>
              <section className="card full">
                <header>
                  <h2>Registro de ações</h2>
                  <button
                    className="secondary compact"
                    onClick={() =>
                      void run(
                        async () =>
                          setAudit(await api<typeof audit>("/api/admin/audit")),
                        "",
                        false,
                      )
                    }
                  >
                    Consultar registros
                  </button>
                </header>
                {audit.length ? (
                  audit.map((a) => (
                    <article key={a.id} className="audit-row">
                      <strong>{a.action}</strong>
                      <span>{date(a.at)}</span>
                      <code>{a.traceId}</code>
                    </article>
                  ))
                ) : (
                  <Empty title="Consulte o registro da empresa">
                    Ações têm autoria, data e código de atendimento.
                  </Empty>
                )}
              </section>
            </div>
          )}
        </main>
        <footer className="page-footer">
          EBT Enterprise{" "}
          <span>
            Connect · {labels[me.role]} ·{" "}
            {me.tenants.find((t) => t.id === me.tenantId)?.name}
          </span>
        </footer>
      </div>
      {!!documentVersions.length && activeDoc && !dialog && (
        <Modal
          title={"Versões · " + activeDoc.title}
          close={() => setDocumentVersions([])}
          busy={busy}
        >
          {documentVersions.map((v) => (
            <article className="document-row" key={v.number}>
              <div>
                <strong>
                  Versão {v.number} · {v.fileName}
                </strong>
                <span>{date(v.createdAt)}</span>
                {v.reviewReason && <p>{v.reviewReason}</p>}
              </div>
              <Badge value={v.reviewState} />
              <button
                className="text-button"
                onClick={() =>
                  void run(
                    () =>
                      download(
                        route +
                          "/documents/" +
                          activeDoc.id +
                          "/download/" +
                          v.number,
                      ),
                    "Arquivo baixado.",
                    false,
                  )
                }
              >
                Baixar versão {v.number}
              </button>
            </article>
          ))}
        </Modal>
      )}
      {dialog && (
        <Modal
          title={
            {
              contact: "Novo relacionamento",
              edit: "Editar relacionamento",
              organization: "Nova organização",
              note: "Registrar nota interna",
              task: "Novo compromisso",
              close: "Encerrar tarefa",
              document: "Enviar documento comercial",
              version: "Nova versão do documento",
              import: "Importar contatos",
              invite: "Preparar convite",
              reject: "Rejeitar documento",
            }[dialog]
          }
          close={() => setDialog(null)}
          busy={busy}
        >
          <form onSubmit={submit}>
            {dialog === "reject" && (
              <label>
                Motivo da rejeição
                <textarea name="reason" required maxLength={2000} />
              </label>
            )}
            {(dialog === "contact" || dialog === "edit") && (
              <>
                <label>
                  Nome
                  <input
                    name="name"
                    required
                    maxLength={160}
                    defaultValue={dialog === "edit" ? selected?.name : ""}
                  />
                </label>
                <div className="form-grid">
                  <label>
                    E-mail
                    <input
                      name="email"
                      type="email"
                      maxLength={254}
                      defaultValue={dialog === "edit" ? selected?.email : ""}
                    />
                  </label>
                  <label>
                    Telefone com DDI
                    <input
                      name="phone"
                      placeholder="5511999990001"
                      maxLength={24}
                      defaultValue={dialog === "edit" ? selected?.phone : ""}
                    />
                  </label>
                </div>
                {dialog === "contact" && (
                  <label>
                    Chave externa (opcional)
                    <input name="externalKey" maxLength={100} />
                  </label>
                )}
                <div className="form-grid">
                  <label>
                    Etapa
                    <select
                      name="stage"
                      defaultValue={
                        dialog === "edit" ? selected?.stage : "novo"
                      }
                    >
                      {stages.map((s) => (
                        <option key={s} value={s}>
                          {labels[s]}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Responsável
                    <select
                      name="ownerId"
                      defaultValue={
                        dialog === "edit" ? selected?.ownerId : me.userId
                      }
                    >
                      {members
                        .filter(
                          (m) =>
                            m.active &&
                            (m.role === "operator" || m.role === "admin"),
                        )
                        .map((m) => (
                          <option key={m.userId} value={m.userId}>
                            {m.name}
                          </option>
                        ))}
                    </select>
                  </label>
                </div>
                <label>
                  Organização
                  <select
                    name="organizationId"
                    defaultValue={
                      dialog === "edit" ? (selected?.organizationId ?? "") : ""
                    }
                  >
                    <option value="">Sem organização</option>
                    {orgs.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                </label>
                {admin && (
                  <label>
                    Carteira
                    <input
                      name="portfolio"
                      maxLength={60}
                      required
                      defaultValue={
                        dialog === "edit" ? selected?.portfolio : me.portfolio
                      }
                    />
                  </label>
                )}
              </>
            )}
            {dialog === "organization" && (
              <>
                <label>
                  Nome
                  <input name="name" required maxLength={160} />
                </label>
                <label>
                  Chave externa
                  <input name="externalKey" required maxLength={100} />
                </label>
              </>
            )}
            {dialog === "note" && (
              <>
                <label>
                  Conteúdo da nota
                  <textarea name="content" required maxLength={4000} rows={5} />
                </label>
                <label>
                  Data da conversa (opcional)
                  <input name="occurredAt" type="datetime-local" />
                </label>
                <p className="small muted">
                  Sem data, será usado o instante atual. Nota interna não envia
                  mensagem ao cliente.
                </p>
              </>
            )}
            {dialog === "task" && (
              <>
                <label>
                  Próximo passo
                  <input name="title" required maxLength={200} />
                </label>
                <label>
                  Prazo
                  <input name="dueAt" type="datetime-local" required />
                </label>
                <label>
                  Responsável
                  <select name="ownerId" defaultValue={selected?.ownerId}>
                    {members
                      .filter(
                        (m) =>
                          m.active &&
                          (m.role === "operator" || m.role === "admin"),
                      )
                      .map((m) => (
                        <option key={m.userId} value={m.userId}>
                          {m.name}
                        </option>
                      ))}
                  </select>
                </label>
              </>
            )}
            {dialog === "close" && (
              <>
                <p>{activeTask?.title}</p>
                <label>
                  Resultado
                  <select name="state">
                    <option value="done">Concluir</option>
                    <option value="cancelled">Cancelar</option>
                  </select>
                </label>
                <label>
                  Descreva o resultado ou motivo
                  <textarea name="result" required maxLength={2000} rows={4} />
                </label>
              </>
            )}
            {(dialog === "document" || dialog === "version") && (
              <>
                <label>
                  Título
                  <input
                    name="title"
                    required
                    maxLength={200}
                    defaultValue={dialog === "version" ? activeDoc?.title : ""}
                  />
                </label>
                <label>
                  Arquivo PDF ou texto
                  <input name="file" type="file" accept=".pdf,.txt" required />
                </label>
                <label>
                  Tarefa vinculada (opcional)
                  <select
                    name="taskId"
                    defaultValue={
                      dialog === "version" ? (activeDoc?.taskId ?? "") : ""
                    }
                  >
                    <option value="">Sem tarefa</option>
                    {tasks.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.title}
                      </option>
                    ))}
                  </select>
                </label>
                <p className="small muted">
                  Até 2 MiB. Uma nova versão volta para revisão.
                </p>
              </>
            )}
            {dialog === "import" && (
              <>
                {preview ? (
                  <>
                    <p>
                      Confira {preview.rows.length} contato(s). Nenhum cadastro
                      definitivo foi gravado no preview.
                    </p>
                    <ul className="preview-list">
                      {preview.rows.map((r) => (
                        <li key={r.externalKey}>
                          <strong>{r.name}</strong>
                          <code>{r.externalKey}</code>
                        </li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <>
                    <label>
                      Planilha CSV (até 100 contatos)
                      <input
                        name="csv"
                        type="file"
                        accept=".csv,text/csv"
                        required
                      />
                    </label>
                    <p className="small muted">
                      Salve a planilha como CSV UTF-8, com as colunas chave,
                      nome, email e telefone. Confira o preview antes de
                      confirmar.
                    </p>
                    <button
                      className="text-button"
                      type="button"
                      onClick={downloadContactsTemplate}
                    >
                      Baixar modelo da planilha
                    </button>
                  </>
                )}
              </>
            )}
            {dialog === "invite" && (
              <>
                <label>
                  E-mail
                  <input name="email" type="email" required />
                </label>
                <label>
                  Perfil
                  <select name="role">
                    <option value="operator">Operador</option>
                    <option value="reader">Consulta</option>
                    <option value="admin">Administrador</option>
                  </select>
                </label>
                <label>
                  Carteira
                  <input
                    name="portfolio"
                    required
                    defaultValue={me.portfolio}
                    maxLength={60}
                  />
                </label>
              </>
            )}
            {error && (
              <p className="error" role="alert">
                {error}
              </p>
            )}
            <footer className="form-footer">
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => setDialog(null)}
              >
                Cancelar
              </button>
              <button className="primary" disabled={busy}>
                {busy
                  ? "Salvando…"
                  : dialog === "import"
                    ? preview
                      ? "Confirmar importação"
                      : "Preparar preview"
                    : dialog === "close"
                      ? "Confirmar resultado"
                      : "Salvar"}
              </button>
            </footer>
          </form>
        </Modal>
      )}
    </div>
  );
}
