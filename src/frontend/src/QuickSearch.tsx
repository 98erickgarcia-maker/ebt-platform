import { createPortal } from "react-dom";
import { useEffect, useRef, useState } from "react";
import { api, route } from "./api";
type Result = {
  id: string;
  contactId: string;
  title: string;
  context: string;
  kind: string;
};
export function QuickSearch({
  onContact,
}: {
  onContact: (id: string) => void;
}) {
  const [open, setOpen] = useState(false),
    [text, setText] = useState(""),
    [results, setResults] = useState<Result[]>([]),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false),
    [index, setIndex] = useState(0);
  const input = useRef<HTMLInputElement>(null),
    trigger = useRef<HTMLButtonElement>(null),
    panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const shortcut = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((x) => !x);
      }
    };
    window.addEventListener("keydown", shortcut);
    return () => window.removeEventListener("keydown", shortcut);
  }, []);
  useEffect(() => {
    if (open) input.current?.focus();
    else {
      setText("");
      setResults([]);
    }
  }, [open]);
  useEffect(() => {
    let current = true;
    setResults([]);
    setError("");
    setIndex(0);
    if (!open || text.trim().length < 2) {
      setLoading(false);
      return;
    }
    setLoading(true);
    const timer = setTimeout(
      () =>
        void api<Result[]>(route + "/search?search=" + encodeURIComponent(text))
          .then((x) => {
            if (current) setResults(x);
          })
          .catch((e) => {
            if (current) setError(e.message);
          })
          .finally(() => {
            if (current) setLoading(false);
          }),
      250,
    );
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [open, text]);
  function close() {
    setOpen(false);
    trigger.current?.focus();
  }
  function choose(row: Result) {
    close();
    onContact(row.contactId);
  }
  return (
    <>
      <button
        ref={trigger}
        className="secondary quick-search-trigger"
        onClick={() => setOpen(true)}
        aria-haspopup="dialog"
      >
        Buscar no Connect <kbd>Ctrl K</kbd>
      </button>
      {open &&
        createPortal(
          <div
            className="scrim"
            onClick={(e) => {
              if (e.target === e.currentTarget) close();
            }}
          >
            <div
              ref={panel}
              className="modal quick-search"
              role="dialog"
              aria-modal="true"
              aria-labelledby="search-title"
              onKeyDown={(e) => {
                if (e.key === "Escape") {
                  e.preventDefault();
                  close();
                }
                if (e.key === "Tab") {
                  const items = Array.from(
                    panel.current?.querySelectorAll<HTMLElement>(
                      "button, input",
                    ) ?? [],
                  );
                  const first = items[0],
                    last = items.at(-1);
                  if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last?.focus();
                  } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first?.focus();
                  }
                }
              }}
            >
              <header>
                <h2 id="search-title">Buscar no Connect</h2>
                <button className="secondary" onClick={close}>
                  Fechar
                </button>
              </header>
              <label>
                Contato, organização, tarefa ou documento
                <input
                  ref={input}
                  value={text}
                  maxLength={160}
                  onChange={(e) => setText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "ArrowDown") {
                      e.preventDefault();
                      setIndex((x) => Math.min(x + 1, results.length - 1));
                    }
                    if (e.key === "ArrowUp") {
                      e.preventDefault();
                      setIndex((x) => Math.max(0, x - 1));
                    }
                    if (e.key === "Enter" && results[index]) {
                      e.preventDefault();
                      choose(results[index]);
                    }
                  }}
                  aria-controls="search-results"
                />
              </label>
              {error && <p role="alert">{error}</p>}
              {loading && <p role="status">Buscando…</p>}
              <div id="search-results">
                {results.map((row, i) => (
                  <button
                    key={row.kind + row.id}
                    className={
                      index === i
                        ? "search-result highlighted"
                        : "search-result"
                    }
                    onClick={() => choose(row)}
                  >
                    <strong>{row.title}</strong>
                    <small>
                      {{
                        contact: "Relacionamento",
                        task: "Tarefa",
                        document: "Documento",
                      }[row.kind] ?? row.kind}{" "}
                      · {row.context}
                    </small>
                  </button>
                ))}
              </div>
              {!loading &&
                !error &&
                text.trim().length >= 2 &&
                results.length === 0 && (
                  <p>Nenhum resultado no seu acesso atual.</p>
                )}
              <small>
                A busca respeita sua empresa e carteira. Selecione um resultado
                para abrir o relacionamento de origem.
              </small>
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
export function DuplicateHints({
  email,
  phone,
  exclude,
  onContact,
}: {
  email: string;
  phone: string;
  exclude?: string;
  onContact: (id: string) => void;
}) {
  const [matches, setMatches] = useState<{ id: string; name: string }[]>([]),
    [error, setError] = useState("");
  useEffect(() => {
    let current = true;
    setMatches([]);
    setError("");
    if (!email.trim() && phone.replace(/\D/g, "").length < 10) return;
    const timer = setTimeout(
      () =>
        void api<{ id: string; name: string }[]>(
          route +
            "/contacts/duplicates?" +
            new URLSearchParams({
              email: email.includes("@") ? email : "",
              phone: phone.replace(/\D/g, "").length >= 10 ? phone : "",
              ...(exclude ? { exclude } : {}),
            }),
        )
          .then((x) => {
            if (current) setMatches(x);
          })
          .catch((e) => {
            if (current) setError(e.message);
          }),
      400,
    );
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [email, phone, exclude]);
  if (error)
    return (
      <p className="small" role="status">
        Não foi possível conferir duplicidades: {error}
      </p>
    );
  if (!matches.length) return null;
  return (
    <aside className="duplicate-hints">
      <strong>Contatos com este e-mail ou telefone</strong>
      <p>Confira antes de criar outro ID.</p>
      {matches.map((x) => (
        <button
          type="button"
          className="secondary"
          key={x.id}
          onClick={() => onContact(x.id)}
        >
          {x.name} · abrir cadastro
        </button>
      ))}
    </aside>
  );
}
