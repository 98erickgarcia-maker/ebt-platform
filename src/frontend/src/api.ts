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
  organizationName?: string | null;
  activeSince?: string | null;
  prospection?: {
    source: string;
    sourceUrl: string;
    segment: string;
    contactRole: string;
    need: string;
    preferredChannel: string;
    bestTime: string;
    decisionMaker: string;
  };
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
  recipient: string;
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
  withoutNextAction?: number;
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
let accessIdentity: string | undefined;
let csrfRequest: { generation: number; promise: Promise<string> } | undefined;
export function setAccess(me: Me) {
  const identity = `${me.userId}|${me.tenantId}|${me.role}|${me.portfolio}`;
  if (accessIdentity && accessIdentity !== identity) resetContext();
  accessIdentity = identity;
  accessFingerprint = `${me.tenantId}|${me.role}|${me.portfolio}`;
}
export function resetContext() {
  csrf = undefined;
  accessFingerprint = undefined;
  accessIdentity = undefined;
  csrfRequest = undefined;
  generation++;
}
function assertCurrent(current: number) {
  if (current !== generation)
    throw new ApiError(0, "context_changed", "Contexto alterado.");
}
function apiPath(path: string): string {
  const url = new URL(path, window.location.origin);
  if (
    url.origin !== window.location.origin ||
    !url.pathname.startsWith("/api/")
  )
    throw new Error("Destino de API inválido.");
  return url.pathname + url.search;
}
function checkScope(response: Response, current: number) {
  assertCurrent(current);
  const signature = response.headers.get("X-Access-Scope");
  if (signature && accessFingerprint && signature !== accessFingerprint) {
    resetContext();
    window.dispatchEvent(new Event("ebt:access-changed"));
    throw new ApiError(0, "context_changed", "Permissões alteradas.");
  }
}
async function csrfToken(current: number): Promise<string> {
  assertCurrent(current);
  if (csrf) return csrf;
  if (csrfRequest?.generation === current) return csrfRequest.promise;
  const request = fetch("/api/security/csrf", {
    credentials: "same-origin",
    cache: "no-store",
    redirect: "error",
  })
    .then(async (response) => {
      assertCurrent(current);
      if (!response.ok) throw new Error("Não foi possível validar a sessão.");
      const payload = (await response.json()) as { token?: string };
      assertCurrent(current);
      if (typeof payload.token !== "string" || !payload.token)
        throw new Error("Resposta de sessão inválida.");
      csrf = payload.token;
      return csrf;
    })
    .finally(() => {
      if (csrfRequest?.promise === request) csrfRequest = undefined;
    });
  csrfRequest = { generation: current, promise: request };
  return request;
}
async function responseError(
  response: Response,
  current: number,
): Promise<never> {
  const problem = (await response.json().catch(() => ({}))) as {
    code?: string;
    title?: string;
    traceId?: string;
  };
  assertCurrent(current);
  if (response.status === 401) {
    resetContext();
    window.dispatchEvent(new Event("ebt:unauthorized"));
  }
  if (problem.code === "csrf_invalid") {
    csrf = undefined;
    csrfRequest = undefined;
  }
  throw new ApiError(
    response.status,
    problem.code ?? "request_failed",
    (problem.title ?? "A solicitação não pôde ser concluída.") +
      (problem.traceId ? ` Código: ${problem.traceId}` : ""),
  );
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
  headers: Record<string, string> = {},
): Promise<T> {
  const destination = apiPath(path);
  const current = generation;
  method = method.toUpperCase();
  headers = { ...headers };
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    if (accessFingerprint)
      headers["X-Expected-Tenant"] = accessFingerprint.split("|")[0];
    headers["X-CSRF-TOKEN"] = await csrfToken(current);
  }
  const isForm = body instanceof FormData;
  if (current !== generation)
    throw new ApiError(0, "context_changed", "Contexto alterado.");
  if (body !== undefined && !isForm)
    headers["Content-Type"] = "application/json";
  let response: Response;
  try {
    response = await fetch(destination, {
      method,
      credentials: "same-origin",
      cache: "no-store",
      redirect: "error",
      headers,
      body:
        body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    });
  } catch {
    assertCurrent(current);
    throw new ApiError(
      0,
      "network_uncertain",
      "Não foi possível confirmar o resultado. Atualize o registro antes de repetir.",
    );
  }
  checkScope(response, current);
  if (!response.ok) return responseError(response, current);
  if (response.status === 204) return undefined as T;
  const payload = (await response.json()) as T;
  assertCurrent(current);
  return payload;
}
export async function download(path: string): Promise<void> {
  const destination = apiPath(path);
  const current = generation;
  const response = await fetch(destination, {
    credentials: "same-origin",
    cache: "no-store",
    redirect: "error",
  });
  checkScope(response, current);
  if (!response.ok) return responseError(response, current);
  const blob = await response.blob();
  assertCurrent(current);
  const url = URL.createObjectURL(blob);
  try {
    const link = window.document.createElement("a");
    const header = response.headers.get("content-disposition") ?? "";
    link.download = header.match(/filename="?([^";]+)/)?.[1] ?? "documento";
    link.href = url;
    link.click();
  } finally {
    URL.revokeObjectURL(url);
  }
}
export const route = "/api/connect/v1";
export const stages = ["novo", "contato", "proposta", "ganho", "encerrado"];
export const labels: Record<string, string> = {
  novo: "Novo",
  contato: "Em contato",
  proposta: "Proposta",
  ganho: "Cliente ativo",
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
