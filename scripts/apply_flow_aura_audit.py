"""One-shot, hash-guarded patch reviewed in the FLOW AURA audit. No deploy or gate promotion."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
app = root / 'src/frontend/src/App.tsx'
main = root / 'src/frontend/src/main.tsx'
expected = {
    app: '42fe6bfa90dcf17d7b889d9c8a8d47c2ba2d4bf1bc07961b948b82489907c6ea',
    main: '46443a53ae77169a882cab8fb73a0d5950a50c17b8b52a54ab9d7449133b871d',
}
for file, sha in expected.items():
    assert hashlib.sha256(file.read_bytes()).hexdigest() == sha, 'Source moved: ' + str(file)

def replace_once(text, old, new):
    assert text.count(old) == 1, 'Patch context must match exactly once'
    return text.replace(old, new, 1)

text = app.read_text(encoding='utf-8')
text = replace_once(text, 'import { QuickSearch, DuplicateHints } from "./QuickSearch";', 'import { QuickSearch, DuplicateHints } from "./QuickSearch";\nimport { useMobileNavigation } from "./useMobileNavigation";')
old = '''  useEffect(() => {
    if (!menu) return;
    const dismiss = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenu(false);
        mobileMenuButton.current?.focus();
      }
    };
    window.addEventListener("keydown", dismiss);
    return () => window.removeEventListener("keydown", dismiss);
  }, [menu]);'''
text = replace_once(text, old, '  const sidebarRef = useMobileNavigation(menu, setMenu, mobileMenuButton);')
text = replace_once(text, '<aside id="ebt-sidebar-navigation"', '<aside ref={sidebarRef} id="ebt-sidebar-navigation"')
app.write_text(text, encoding='utf-8', newline='\n')
main.write_text(replace_once(main.read_text(encoding='utf-8'), 'import "./style.css";', 'import "./style.css";\nimport "./flow-aura-audit.css";'), encoding='utf-8', newline='\n')

hook = root / 'src/frontend/src/useMobileNavigation.ts'
assert not hook.exists()
hook.write_text('''import { useEffect, useRef, type RefObject } from "react";

/** Non-modal disclosure: enter the navigation on open, never trap keyboard focus. */
export function useMobileNavigation(
  open: boolean,
  setOpen: (value: boolean) => void,
  triggerRef: RefObject<HTMLButtonElement | null>,
) {
  const sidebarRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!open) return;
    const sidebar = sidebarRef.current;
    const trigger = triggerRef.current;
    const mobile = window.matchMedia("(max-width: 680px)");
    if (!mobile.matches || !sidebar) {
      setOpen(false);
      return;
    }
    const active = sidebar.querySelector<HTMLButtonElement>(
      'nav button[aria-current="page"]',
    ) ?? sidebar.querySelector<HTMLButtonElement>("nav button");
    active?.focus({ preventScroll: true });
    active?.scrollIntoView({ block: "nearest", inline: "nearest" });

    const outside = (target: EventTarget | null) =>
      target instanceof Node && !sidebar.contains(target) && target !== trigger;
    const leave = (event: FocusEvent) => {
      if (outside(event.target)) setOpen(false);
    };
    const pointer = (event: PointerEvent) => {
      if (outside(event.target) && !trigger?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.preventDefault();
      setOpen(false);
      trigger?.focus({ preventScroll: true });
    };
    const resize = () => {
      if (!mobile.matches) setOpen(false);
    };
    document.addEventListener("focusin", leave);
    document.addEventListener("pointerdown", pointer);
    window.addEventListener("keydown", escape);
    mobile.addEventListener("change", resize);
    return () => {
      document.removeEventListener("focusin", leave);
      document.removeEventListener("pointerdown", pointer);
      window.removeEventListener("keydown", escape);
      mobile.removeEventListener("change", resize);
    };
  }, [open, setOpen, triggerRef]);
  return sidebarRef;
}
''', encoding='utf-8', newline='\n')

css = root / 'src/frontend/src/flow-aura-audit.css'
assert not css.exists()
css.write_text('''/* FLOW + AURA audit: preserve identity, expose all operational information. */
/* Shared shell: long contact names must not push page actions outside the viewport. */
.page-heading { flex-wrap: wrap; }
.page-heading > div:first-child { flex: 1 1 20rem; min-width: 0; }
.page-heading h1 { overflow-wrap: anywhere; }
.heading-actions { flex-wrap: wrap; min-width: 0; }

/* A fixed sidebar must remain usable with short windows and enlarged content. */
.sidebar { overflow-y: auto; overscroll-behavior: contain; }
.sidebar nav, .sidebar .brand, .sidebar-bottom { flex-shrink: 0; }
.sidebar-bottom > div { min-width: 0; overflow-wrap: anywhere; }
.sidebar :focus-visible { outline: 3px solid #ff9a5e; outline-offset: 3px; }

.flow-contact-360 { --contact-panel-inset: clamp(16px, 2vw, 24px); }
.flow-contact-360 :is(h2, h3, p, strong, dd, dt, .contact-shortcuts a),
.flow-aura-daily :is(.task-row strong, .metrics strong) {
  overflow-wrap: anywhere;
}
.flow-contact-360 .card > header { flex-wrap: wrap; }
.flow-contact-360 .card > header > *,
.flow-contact-360 .timeline article > div,
.flow-contact-360 .task-row > div,
.flow-aura-daily .task-row > div { min-width: 0; }
.flow-contact-360 .task-row,
.flow-aura-daily .task-row { flex-wrap: wrap; }
.flow-contact-360 .task-row > div,
.flow-aura-daily .task-row > div { flex: 1 1 12rem; }
.flow-contact-360 :is(button, a),
.flow-aura-daily .task-row button { max-width: 100%; overflow-wrap: anywhere; }
.flow-contact-360 .next-action strong { display: block; }

/* Keep controls and reading text away from the clipped, rounded card boundary. */
.flow-contact-360 .commercial-templates {
  padding: 0 var(--contact-panel-inset) 22px;
}
.flow-contact-360 .commercial-templates > header {
  margin-inline: calc(-1 * var(--contact-panel-inset));
  margin-bottom: 16px;
}
.flow-contact-360 .commercial-templates :is(input, textarea, select) {
  min-width: 0;
  max-width: 100%;
  border-color: #77716b;
}
.flow-contact-360 .qualification-detail {
  padding: 18px var(--contact-panel-inset);
}
.flow-contact-360 .qualification-detail summary {
  min-height: 24px;
  margin: 0;
  overflow-wrap: anywhere;
}
.flow-contact-360 .qualification-detail[open] summary { margin-bottom: 16px; }
.flow-contact-360 .qualification-detail dl {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr);
}
.flow-contact-360 summary:focus-visible {
  outline: 3px solid #9a3a09;
  outline-offset: 3px;
  border-radius: 3px;
}
.flow-aura-daily .flow-hero-cta:focus-visible {
  outline: 3px solid #fffdfa;
  outline-offset: 4px;
}
@media (max-width: 480px) {
  .flow-contact-360 .qualification-detail dl { grid-template-columns: minmax(0, 1fr); }
  .flow-contact-360 .qualification-detail dd { margin-bottom: 10px; }
}
@media print {
  /* Global print CSS hides buttons; these buttons ALSO contain essential data. */
  .flow-aura-daily .metrics > button,
  .flow-aura-daily .stage-list > button {
    display: block !important;
    background: #fff !important;
    color: #111214 !important;
    border: 1px solid #77716b;
    box-shadow: none;
    transform: none;
    break-inside: avoid;
  }
  .flow-aura-daily .stage-list > button { display: flex !important; }
  .flow-aura-daily .metrics svg,
  .flow-aura-daily .welcome-graphic,
  .flow-aura-daily .flow-section-heading > span { display: none !important; }
  .flow-aura-daily .welcome-card .eyebrow,
  .flow-aura-daily .flow-hero-status { color: #333437 !important; }
}
''', encoding='utf-8', newline='\n')

# This is an explicit, finite reviewed file list, not automatic approval of a tree.
manifest_path = root / 'planejamento/continuidade_github.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
reviewed = [
    'src/frontend/src/App.tsx', 'src/frontend/src/main.tsx',
    'src/frontend/src/useMobileNavigation.ts', 'src/frontend/src/flow-aura-audit.css',
    'src/frontend/e2e/flow-aura-audit.spec.ts',
]
for name in reviewed:
    entry = next((entry for entry in manifest['files'] if entry['path'] == name), None)
    if entry is None:
        entry = {'path': name}
        manifest['files'].append(entry)
    entry['reviewed_sha256'] = hashlib.sha256((root / name).read_bytes()).hexdigest()
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
# Temporary transport helpers do not belong to the delivered product diff.
for name in ['.github/workflows/flow-aura-audit-snapshot.yml', '.github/workflows/apply-flow-aura-audit.yml', 'scripts/apply_flow_aura_audit.py']:
    (root / name).unlink(missing_ok=True)
print('Applied only the reviewed UI patch; no API, SQL, production, budget or approval gate changed.')
