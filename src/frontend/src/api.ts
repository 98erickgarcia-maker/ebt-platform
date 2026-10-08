export type Me = {
  name: string;
  email: string;
  userId: string;
  tenantId: string;
  role: string;
  portfolio: string;
  tenants: { id: string; name: string; product: string; role: string }[];
};
export type Contact = {
  id: string;
  name: string;
  email: string;
  phone: string;
  externalKey: string;
  organizationId: string | null;
  ownerId: string;
  portfolio: string;
  stage: string;
  version: number;
  createdAt: string;
  nextAction: {
    id: string;
    title: string;
    dueAt: string;
    ownerId: string;
  } | null;
};
export type Task = {
  id: string;
  contactId: string;
  title: string;
  ownerId: string;
  dueAt: string;
  state: string;
  result: string;
  version: number;
};
export type Note = {
  id: string;
  kind: string;
  content: string;
  actorId: string;
  occurredAt: string;
  recordedAt: string;
};
export type Conversation = {
  id: string;
  contactId: string;
  contactName: string;
  contactPhone: string;
  contactEmail: string;
  state: string;
  lastInboundAt: string | null;
  version: number;
  channelName: string;
  provider: string;
};
export type Message = {
  messageId: string;
  conversationId: string;
  direction: string;
  content: string;
  status: string;
  providerId: string;
  failureCode: string;
  createdAt: string;
};
export type Document = {
  id: string;
  contactId: string;
  taskId: string | null;
  title: string;
  currentVersion: number;
  reviewState: string;
  version: number;
};
export type Member = {
  id: string;
  userId: string;
  name: string;
  role: string;
  portfolio: string;
  active: boolean;
  version: number;
};
export type Organization = { id: string; name: string; portfolio: string };
export type ImportRow = {
  externalKey: string;
  name: string;
  email: string;
  phone: string;
};
export type Summary = {
  contacts: number;
  openTasks: number;
  overdue: number;
  stages: { stage: string; count: number }[];
};
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}
let csrf: string | undefined;
let generation = 0;
let accessFingerprint: string | undefined;
export function setAccess(me: Me) {
  accessFingerprint = `${me.tenantId}|${me.role}|${me.portfolio}`;
}
export function resetContext() {
  csrf = undefined;
  accessFingerprint = undefined;
  generation++;
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
  headers: Record<string, string> = {},
): Promise<T> {
  const url = new URL(path, window.location.origin);
  if (
    url.origin !== window.location.origin ||
    !url.pathname.startsWith("/api/")
  )
    throw new Error("Destino de API inválido.");
  const current = generation;
  if (method !== "GET") {
    if (accessFingerprint)
      headers["X-Expected-Tenant"] = accessFingerprint.split("|")[0];
    if (!csrf) {
      const response = await fetch("/api/security/csrf", {
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error("Não foi possível validar a sessão.");
      csrf = ((await response.json()) as { token: string }).token;
    }
    headers["X-CSRF-TOKEN"] = csrf!;
  }
  const isForm = body instanceof FormData;
  if (current !== generation)
    throw new ApiError(0, "context_changed", "Contexto alterado.");
  if (body !== undefined && !isForm)
    headers["Content-Type"] = "application/json";
  let response: Response;
  try {
    response = await fetch(url.pathname + url.search, {
      method,
      credentials: "same-origin",
      headers,
      body:
        body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      0,
      "network_uncertain",
      "Não foi possível confirmar o resultado. Atualize o registro antes de repetir.",
    );
  }
  if (current !== generation)
    throw new ApiError(0, "context_changed", "Contexto alterado.");
  const signature = response.headers.get("X-Access-Scope");
  if (signature && accessFingerprint && signature !== accessFingerprint) {
    resetContext();
    window.dispatchEvent(new Event("ebt:access-changed"));
    throw new ApiError(0, "context_changed", "Permissões alteradas.");
  }
  if (!response.ok) {
    const problem = (await response.json().catch(() => ({}))) as {
      code?: string;
      title?: string;
      traceId?: string;
    };
    if (response.status === 401)
      window.dispatchEvent(new Event("ebt:unauthorized"));
    throw new ApiError(
      response.status,
      problem.code ?? "request_failed",
      (problem.title ?? "A solicitação não pôde ser concluída.") +
        (problem.traceId ? ` Código: ${problem.traceId}` : ""),
    );
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
export async function download(path: string): Promise<void> {
  const response = await fetch(path, { credentials: "same-origin" });
  if (!response.ok) {
    const p = (await response.json()) as { title: string };
    throw new Error(p.title);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = window.document.createElement("a");
  const header = response.headers.get("content-disposition") ?? "";
  link.download = header.match(/filename="?([^";]+)/)?.[1] ?? "documento";
  link.href = url;
  link.click();
  URL.revokeObjectURL(url);
}
export const route = "/api/connect/v1";
export const stages = ["novo", "contato", "proposta", "ganho", "encerrado"];
export const labels: Record<string, string> = {
  novo: "Novo",
  contato: "Em contato",
  proposta: "Proposta",
  ganho: "Ganho",
  encerrado: "Encerrado",
  open: "Aberta",
  done: "Concluída",
  cancelled: "Cancelada",
  queued: "Na fila",
  accepted: "Aceita pelo canal",
  sent: "Enviada",
  delivered: "Entregue",
  read: "Lida",
  failed: "Falhou",
  unknown: "Resultado incerto",
  received: "Recebida",
  pending: "Aguardando revisão",
  approved: "Aprovado",
  rejected: "Rejeitado",
  admin: "Administrador",
  operator: "Operador",
  reader: "Consulta",
  support: "Suporte técnico",
};
export const date = (value: string) =>
  new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "America/Sao_Paulo",
  }).format(new Date(value));
