import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError, date } from "./api";

type ApiKey = {
  id: string;
  name: string;
  ownerName: string;
  ownerEmail: string;
  expiresAt: string;
  active: boolean;
  state: "active" | "expired" | "revoked";
};

export function ApiKeyPanel() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [issued, setIssued] = useState<{ id: string; token: string } | null>(
    null,
  );
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    let current = true;
    setLoading(true);
    api<ApiKey[]>("/api/admin/api-keys")
      .then((rows) => {
        if (current) setKeys(rows);
      })
      .catch((e: Error) => {
        if (current && !(e instanceof ApiError && e.code === "context_changed"))
          setError(e.message);
      })
      .finally(() => {
        if (current) setLoading(false);
      });
    return () => {
      current = false;
    };
  }, [refresh]);
  async function change(id?: string) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      if (id) {
        await api("/api/admin/api-keys/" + id, "DELETE");
        setIssued((key) => (key?.id === id ? null : key));
        setNotice("Chave revogada. Novas requisições com ela serão recusadas.");
      } else {
        setIssued(
          await api<{ id: string; token: string }>(
            "/api/admin/api-keys",
            "POST",
          ),
        );
        setNotice(
          "Guarde a chave em local seguro. O segredo não pode ser consultado novamente.",
        );
      }
      setRefresh((value) => value + 1);
    } catch (e) {
      if (!(e instanceof ApiError && e.code === "context_changed"))
        setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const states = { active: "Ativa", expired: "Expirada", revoked: "Revogada" };
  return (
    <section className="card" aria-label="Chaves de API">
      <header>
        <h2>Integração por API</h2>
      </header>
      <div className="settings-note">
        <p>As chaves pertencem à empresa selecionada e ao acesso do titular.</p>
        <button
          className="secondary"
          disabled={busy || loading}
          onClick={() => void change()}
        >
          Criar chave de API
        </button>
        {issued && (
          <label className="credential">
            Chave criada · {issued.id}
            <textarea
              readOnly
              value={issued.token}
              onFocus={(event) => event.target.select()}
            />
          </label>
        )}
        {notice && <p role="status">{notice}</p>}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {loading && <p role="status">Consultando chaves…</p>}
        {!loading && keys.length === 0 && (
          <p>Nenhuma chave cadastrada nesta empresa.</p>
        )}
      </div>
      {keys.map((key) => (
        <article
          className="document-row"
          key={key.id}
          aria-label={"Chave " + key.id}
        >
          <div>
            <strong>{key.name || "Chave de API"}</strong>
            <span>
              {key.ownerName} · {key.ownerEmail}
            </span>
            <span>
              Validade: {date(key.expiresAt)} · {states[key.state]}
            </span>
            <code>{key.id}</code>
          </div>
          <button
            className="secondary compact"
            disabled={busy || !key.active}
            onClick={() => void change(key.id)}
          >
            Revogar chave
          </button>
        </article>
      ))}
    </section>
  );
}

export function InvitationAcceptance({
  email,
  initialToken = "",
  onAccepted,
}: {
  email: string;
  initialToken?: string;
  onAccepted: () => Promise<void>;
}) {
  const [token, setToken] = useState(initialToken);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  async function accept(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api("/api/auth/invitations/accept-existing", "POST", {
        token: token.trim(),
      });
      setToken("");
      history.replaceState(null, "", location.pathname);
      await onAccepted();
      setNotice(
        "Convite aceito. A empresa está disponível no seletor Empresa.",
      );
    } catch (e) {
      if (!(e instanceof ApiError && e.code === "context_changed"))
        setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="card full" aria-label="Aceitar convite">
      <header>
        <h2>Convite para outra empresa</h2>
      </header>
      <form className="settings-note" onSubmit={accept}>
        <p>Entre com a conta destinatária do convite. Conta atual: {email}.</p>
        <label>
          Código do convite
          <input
            value={token}
            onChange={(event) => setToken(event.target.value)}
            required
            minLength={64}
            maxLength={64}
            autoComplete="off"
          />
        </label>
        <button
          className="primary compact"
          disabled={busy || token.trim().length !== 64}
        >
          Aceitar convite com esta conta
        </button>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {notice && <p role="status">{notice}</p>}
      </form>
    </section>
  );
}
