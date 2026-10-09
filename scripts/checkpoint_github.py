"""Reviewed GitHub checkpoints without modifying the checkout or its real index.

No API credits, no force push, no deployment. All subprocesses use argument arrays.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

DEFAULT_CONFIG = "planejamento/continuidade_github.json"
BLOCKED_PARTS = {".git", "tmp", "node_modules", "bin", "obj", "private-integrations", "__pycache__", "playwright-report", "test-results"}
BLOCKED_EXTENSIONS = {".db", ".sqlite", ".sqlite3", ".pfx", ".p12", ".pem", ".key", ".bak", ".zip", ".mp4", ".log"}
TEXT_EXTENSIONS = {".md", ".json", ".py", ".ps1", ".cs", ".csproj", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".css", ".html", ".yml", ".yaml", ".sql", ".txt"}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\b"),
    "azure_storage_key": re.compile(r"(?i)AccountKey\s*=\s*[A-Za-z0-9+/]{40,}={0,2}"),
    "credential_url": re.compile(r"https?://[^\s/:]+:[^\s/@]+@"),
    "literal_secret": re.compile(r'''(?i)(?<![A-Za-z0-9_-])["']?(?:api[_-]?key|access[_-]?token|signing[_-]?secret|client[_-]?secret|password|senha)["']?\s*[:=]\s*["']([A-Za-z0-9_+!/@.-]{12,})["']'''),
}
SYNTHETIC_PREFIXES = ("qa-", "qa!", "test-", "test!", "synthetic-", "example-", "fixture-", "dummy-", "local-only-", "<")


class CheckpointError(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(path, data):
    """Match this repository's LF text policy across Windows and Linux clones."""
    if b"\x00" not in data and (PurePosixPath(path).suffix.lower() in TEXT_EXTENSIONS
                               or PurePosixPath(path).name in {".env.example", ".gitignore", ".gitattributes", "Dockerfile"}):
        return data.replace(b"\r\n", b"\n")
    return data


def git(root, *args, data=None, env=None, optional=False):
    command_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never", **(env or {})}
    result = subprocess.run(["git", "-C", str(root), *args], input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=command_env, timeout=90)
    if result.returncode and not optional:
        # Never print stderr: remotes/authentication errors can contain credentials.
        raise CheckpointError(f"Git {args[0]} falhou (código {result.returncode}); dados privados omitidos.")
    return result.stdout.decode("utf-8", errors="strict").strip() if not result.returncode else None


def safe_path(path):
    p = PurePosixPath(path)
    if (not path or "\\" in path or p.is_absolute() or ".." in p.parts or ":" in path
            or any(part.lower() in BLOCKED_PARTS for part in p.parts) or p.parts[0].lower() == "entregas"
            or p.suffix.lower() in BLOCKED_EXTENSIONS
            or (p.name.lower().startswith(".env") and p.name != ".env.example")):
        raise CheckpointError("Caminho privado ou inválido recusado: " + path)
    return p


def scan(path, data, binary_sha=None):
    safe_path(path)
    if b"\x00" in data or (PurePosixPath(path).suffix.lower() not in TEXT_EXTENSIONS
                            and PurePosixPath(path).name not in {".env.example", ".gitignore", ".gitattributes", "Dockerfile"}):
        if binary_sha != digest(data):
            raise CheckpointError("Binário sem hash revisado: " + path)
        return []
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise CheckpointError("Texto não UTF-8 recusado: " + path) from None
    findings = []
    for label, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            if label == "literal_secret":
                value = match.group(1).lower()
                if value.startswith(SYNTHETIC_PREFIXES) or value in {"replace-me", "changeme-example"}:
                    continue
            findings.append({"path": path, "line": text[:match.start()].count("\n") + 1, "rule": label})
    return findings


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".new")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


@contextmanager
def lock(root):
    # OS file locks are released after a crash; no stale lock requires blind deletion.
    path = root / "tmp/continuidade/checkpoint.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0"); handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                raise CheckpointError("Outro checkpoint está em execução.") from None
            try:
                yield
            finally:
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                raise CheckpointError("Outro checkpoint está em execução.") from None
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)


def remote_head(root, remote, branch):
    rows = git(root, "ls-remote", "--heads", remote, "refs/heads/" + branch)
    return rows.split()[0] if rows else None


def load_snapshot(root, config):
    root = root.resolve()
    files = config["files"]
    if len({x["path"].lower() for x in files}) != len(files):
        raise CheckpointError("Manifesto contém caminhos repetidos.")
    snapshot, findings = {}, []
    for entry in files:
        relative = entry["path"]
        safe_path(relative)
        path = root / relative
        if path.is_symlink() or not path.is_file() or root not in path.resolve().parents:
            raise CheckpointError("Arquivo ausente ou fora do projeto: " + relative)
        if path.stat().st_size > 16 * 1024 * 1024:
            raise CheckpointError("Arquivo excede limite do checkpoint: " + relative)
        data = canonical_bytes(relative, path.read_bytes())
        findings.extend(scan(relative, data, entry.get("binary_sha256")))
        snapshot[relative] = data
    if findings:
        # Only paths/line/rule are returned; never matched credentials.
        raise CheckpointError("Scanner bloqueou o checkpoint: " + json.dumps(findings, ensure_ascii=False))
    return snapshot


def checkpoint(root, config_path, *, approve=False, push=False, dry_run=False):
    root = root.resolve()
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    branch, remote = config["branch"], config["remote"]
    if not branch.startswith("codex/") or git(root, "check-ref-format", "refs/heads/" + branch, optional=True) is None:
        raise CheckpointError("Checkpoint exige branch codex/ válida.")
    if remote != "origin" or git(root, "remote", "get-url", remote) != config["repository_url"]:
        raise CheckpointError("Remote difere do repositório aprovado.")
    snapshot = load_snapshot(root, config)
    changed = [e["path"] for e in config["files"] if digest(snapshot[e["path"]]) != e["reviewed_sha256"]]
    report = {"schema_version": 1, "checked_at_utc": now(), "branch": branch, "files": len(snapshot),
              "status": "dry_run", "remote_verified": False, "changed_reviewed_files": changed,
              "product_gates_promoted": False, "deploy_performed": False}
    if changed and not approve:
        # Scheduler cannot publish content that was changed since human/agent review.
        raise CheckpointError("Revisão necessária antes do GitHub; executar --approve após conferir: " + ", ".join(changed))
    if dry_run:
        return report
    if approve:
        for entry in config["files"]:
            entry["reviewed_sha256"] = digest(snapshot[entry["path"]])
        config["reviewed_at_utc"] = now()
        atomic_json(config_path, config)
    # Config isn't in its own hash list; nevertheless validate the exact JSON saved in Git.
    config_relative = config_path.relative_to(root).as_posix()
    safe_path(config_relative)
    snapshot[config_relative] = canonical_bytes(config_relative, config_path.read_bytes())
    if scan(config_relative, snapshot[config_relative]):
        raise CheckpointError("Configuração contém possível segredo.")
    ref = "refs/heads/" + branch
    old = git(root, "rev-parse", "--verify", ref, optional=True)
    base = old or git(root, "rev-parse", config["initial_base_ref"])
    if push:
        observed = remote_head(root, remote, branch)
        # If the last push failed, an ancestor on the remote is an acceptable retry.
        if observed and observed != old and (not old or git(root, "merge-base", "--is-ancestor", observed, old, optional=True) is None):
            raise CheckpointError("Branch remota mudou; reconciliar antes de salvar, sem force push.")
    original_index = Path(git(root, "rev-parse", "--git-path", "index"))
    if not original_index.is_absolute():
        original_index = root / original_index
    index_before = digest(original_index.read_bytes()) if original_index.exists() else None
    head_before = git(root, "rev-parse", "HEAD")
    with tempfile.TemporaryDirectory(prefix="ebt-checkpoint-") as directory:
        env = {"GIT_INDEX_FILE": str(Path(directory) / "index")}
        git(root, "read-tree", base, env=env)

        def stage(path, data):
            blob = git(root, "hash-object", "-w", "--stdin", data=data)
            git(root, "update-index", "--add", "--cacheinfo", "100644", blob, path, env=env)

        # Freeze bytes first and batch Git processes; the real worktree/index stays untouched.
        frozen = []
        for number, (path, data) in enumerate(snapshot.items()):
            temporary_file = Path(directory) / ("blob-" + str(number))
            temporary_file.write_bytes(data)
            frozen.append((path, temporary_file))
        index_entries = []
        for start in range(0, len(frozen), 40):
            batch = frozen[start:start + 40]
            blobs = git(root, "hash-object", "-w", "--no-filters", "--", *(str(file) for _, file in batch)).splitlines()
            if len(blobs) != len(batch):
                raise CheckpointError("Git não confirmou todos os blobs do checkpoint.")
            index_entries.extend(("100644 " + blob + "\t" + path + "\0").encode("utf-8")
                                 for (path, _), blob in zip(batch, blobs))
        git(root, "update-index", "-z", "--index-info", data=b"".join(index_entries), env=env)
        proposed_tree = git(root, "write-tree", env=env)
        prior_tree = git(root, "rev-parse", base + "^{tree}")
        if proposed_tree == prior_tree and old:
            commit = old
            report["status"] = "unchanged_local"
        else:
            manifest = {"schema_version": 1, "created_at_utc": now(), "branch": branch,
                        "parent_checkpoint": old, "base": base, "source_head": head_before,
                        "validation": "checkpoint de conteúdo revisado; não promove gates do produto",
                        "next_step_source": "planejamento/estado_continuidade.json",
                        "files": [{"path": p, "sha256": digest(d)} for p, d in sorted(snapshot.items())]}
            stage("continuidade/CHECKPOINT.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode())
            tree = git(root, "write-tree", env=env)
            args = ["commit-tree", tree, "-p", base]
            # Preserve the divergent local history without changing main or merging its files blindly.
            if not old and head_before != base and git(root, "merge-base", "--is-ancestor", head_before, base, optional=True) is None:
                args += ["-p", head_before]
            commit = git(root, *args, data=b"checkpoint: EBT Enterprise reviewed continuity snapshot\n")
            git(root, "update-ref", ref, commit, old or "0" * 40)
            report["status"] = "saved_local"
        # Pin the exact bytes, not files reread during the upload.
        raced = [p for p, data in snapshot.items() if not (root / p).is_file() or canonical_bytes(p, (root / p).read_bytes()) != data]
        if raced:
            raise CheckpointError("Arquivos mudaram durante o checkpoint; commit local preservado, repetir revisão: " + ", ".join(raced))
    if git(root, "rev-parse", "HEAD") != head_before or (digest(original_index.read_bytes()) if original_index.exists() else None) != index_before:
        raise CheckpointError("Checkout/index mudou concorrentemente; checkpoint local preservado, publicação interrompida.")
    report.update(commit=commit, tree=git(root, "rev-parse", commit + "^{tree}"))
    if push:
        git(root, "-c", "core.hooksPath=", "push", remote, ref + ":" + ref)
        if remote_head(root, remote, branch) != commit:
            raise CheckpointError("Commit local preservado; confirmação remota não corresponde ao SHA.")
        report.update(status="saved_github", remote_verified=True,
                      commit_url=config["repository_url"].removesuffix(".git") + "/commit/" + commit)
    atomic_json(root / "tmp/continuidade/ultimo_checkpoint.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--approve", action="store_true", help="Registrar revisão explícita dos bytes atuais, após inspeção do diff.")
    parser.add_argument("--push", action="store_true", help="Salvar e conferir o SHA no GitHub.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    config_path = root / args.config
    try:
        safe_path(args.config)
        with lock(root):
            result = checkpoint(root, config_path, approve=args.approve, push=args.push, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (CheckpointError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        message = str(exc) if isinstance(exc, CheckpointError) else type(exc).__name__ + ": falha local; detalhes privados omitidos."
        result = {"checked_at_utc": now(), "status": "blocked", "remote_verified": False, "reason": message}
        # A failure record must not masquerade as the last successful upload.
        atomic_json(root / "tmp/continuidade/ultima_falha.json", result)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
