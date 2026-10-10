#!/usr/bin/env bash
set -Eeuo pipefail

# EBT Enterprise - Linux autonomous proposal cycle
# Safe autonomy: one Flow task at a time, verified commit + proposal-branch push only.
# Never merges, deploys, migrates, force-pushes, resets or sends external messages.

REPO_DIR="${REPO_DIR:-/opt/ebt/ebt-platform}"
REMOTE="${REMOTE:-origin}"
BASE_BRANCH="${BASE_BRANCH:-codex/enterprise-blocks-15min-20261009}"
PROPOSAL_BRANCH="${PROPOSAL_BRANCH:-codex/flow-history-proposal-vps-20261009}"
STATE_DIR="${STATE_DIR:-/var/lib/ebt-engineering}"
MANIFEST_REL="${MANIFEST_REL:-planejamento/engineering_blocks.json}"
RUNNER_REL="${RUNNER_REL:-scripts/ops/engineering_runner.py}"
WATCH_REL="${WATCH_REL:-scripts/ops/engineering_watch.py}"
WATCH_STATE="${WATCH_STATE:-$STATE_DIR/watch-state.json}"
LOCK_FILE="${LOCK_FILE:-$STATE_DIR/auto-cycle.lock}"
PENDING_PUSH="${PENDING_PUSH:-$STATE_DIR/pending-push.json}"
AUTO_PUSH_PROPOSAL="${AUTO_PUSH_PROPOSAL:-1}"
DRY_RUN=0

log() { printf '%s %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }
die() { log "ERROR: $*" >&2; exit 30; }

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
elif [[ $# -gt 0 ]]; then
  die "Unknown argument: $1"
fi

for cmd in git python3 flock; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[[ "$AUTO_PUSH_PROPOSAL" == "0" || "$AUTO_PUSH_PROPOSAL" == "1" ]] || die "AUTO_PUSH_PROPOSAL must be 0 or 1"
[[ -d "$REPO_DIR/.git" ]] || die "Git repository not found: $REPO_DIR"
mkdir -p "$STATE_DIR"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "Another EBT engineering cycle is already active; exiting without overlap."
  exit 0
fi

MANIFEST="$REPO_DIR/$MANIFEST_REL"
RUNNER="$REPO_DIR/$RUNNER_REL"
WATCH="$REPO_DIR/$WATCH_REL"
[[ -f "$MANIFEST" ]] || die "Manifest not found: $MANIFEST"
[[ -f "$RUNNER" ]] || die "Runner not found: $RUNNER"

is_dirty() {
  [[ -n "$(git -C "$REPO_DIR" status --porcelain --untracked-files=all)" ]]
}

remote_proposal_sha() {
  git -C "$REPO_DIR" ls-remote --heads "$REMOTE" "refs/heads/$PROPOSAL_BRANCH" 2>/dev/null | awk 'NR==1 {print $1}'
}

manifest_allowed_paths() {
  python3 - "$MANIFEST" <<'PY'
import json, pathlib, sys
obj = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for value in obj.get("allowed_paths", []):
    if isinstance(value, str):
        print(value)
PY
}

validate_dirty_paths() {
  local changed
  changed="$(git -C "$REPO_DIR" status --porcelain=v1 --untracked-files=all | sed -E 's/^.. //' | sed -E 's/.* -> //')"
  [[ -z "$changed" ]] && return 0
  CHANGED_PATHS="$changed" python3 - "$MANIFEST" <<'PY'
import json, os, pathlib, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
allowed = set(manifest.get("allowed_paths", []))
changed = [x for x in os.environ.get("CHANGED_PATHS", "").splitlines() if x]
invalid = [p for p in changed if p not in allowed or pathlib.PurePosixPath(p).name.startswith(".env")]
if invalid:
    raise SystemExit("changed path outside manifest allowlist: " + ", ".join(invalid))
PY
}

write_pending_push() {
  local sha="$1" expected_remote="$2" task="$3"
  PENDING_SHA="$sha" EXPECTED_REMOTE="$expected_remote" TASK_ID="$task" PROPOSAL_BRANCH="$PROPOSAL_BRANCH" \
    python3 - "$PENDING_PUSH" <<'PY'
import json, os, pathlib, tempfile
path = pathlib.Path(__import__('sys').argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
record = {
    "schema_version": 1,
    "branch": os.environ["PROPOSAL_BRANCH"],
    "sha": os.environ["PENDING_SHA"],
    "expected_remote": os.environ["EXPECTED_REMOTE"] or None,
    "task": os.environ["TASK_ID"],
}
fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", text=True)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(record, handle, separators=(",", ":"))
        handle.flush(); os.fsync(handle.fileno())
    os.chmod(name, 0o600)
    os.replace(name, path)
finally:
    if os.path.exists(name): os.unlink(name)
PY
}

read_pending_push() {
  python3 - "$PENDING_PUSH" "$PROPOSAL_BRANCH" <<'PY'
import json, pathlib, re, sys
path = pathlib.Path(sys.argv[1])
expected_branch = sys.argv[2]
obj = json.loads(path.read_text(encoding="utf-8"))
if set(obj) != {"schema_version","branch","sha","expected_remote","task"} or obj["schema_version"] != 1:
    raise SystemExit("invalid pending-push schema")
if obj["branch"] != expected_branch:
    raise SystemExit("pending-push branch mismatch")
if not isinstance(obj["sha"], str) or not re.fullmatch(r"[0-9a-f]{40}", obj["sha"]):
    raise SystemExit("invalid pending-push sha")
if obj["expected_remote"] is not None and (not isinstance(obj["expected_remote"], str) or not re.fullmatch(r"[0-9a-f]{40}", obj["expected_remote"])):
    raise SystemExit("invalid pending remote sha")
if not isinstance(obj["task"], str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", obj["task"]):
    raise SystemExit("invalid pending task")
print(obj["sha"])
print(obj["expected_remote"] or "")
print(obj["task"])
PY
}

push_exact_sha() {
  local sha="$1" expected_remote="$2" task="$3"
  [[ "$AUTO_PUSH_PROPOSAL" == "1" ]] || { log "Automatic proposal push disabled; commit retained locally."; return 0; }
  is_dirty && die "Refusing proposal push with a dirty worktree."
  [[ "$(git -C "$REPO_DIR" rev-parse HEAD)" == "$sha" ]] || die "Pending push SHA is not current HEAD."

  local current_remote
  current_remote="$(remote_proposal_sha)"
  if [[ -n "$expected_remote" ]]; then
    [[ "$current_remote" == "$expected_remote" ]] || die "Remote proposal branch changed before push; manual reconciliation required."
  else
    [[ -z "$current_remote" ]] || die "Proposal branch appeared remotely before first push; manual reconciliation required."
  fi

  log "Pushing verified task $task as exact SHA $sha to proposal branch only."
  git -C "$REPO_DIR" push "$REMOTE" "$sha:refs/heads/$PROPOSAL_BRANCH"
  git -C "$REPO_DIR" fetch --prune "$REMOTE" "$PROPOSAL_BRANCH"
  [[ "$(remote_proposal_sha)" == "$sha" ]] || die "Remote readback did not match pushed SHA."
  rm -f "$PENDING_PUSH"
  log "Verified remote proposal SHA=$sha"
}

log "Fetching remote refs without changing the worktree."
git -C "$REPO_DIR" fetch --prune "$REMOTE"

current_branch="$(git -C "$REPO_DIR" branch --show-current)"
if [[ "$current_branch" != "$PROPOSAL_BRANCH" ]]; then
  is_dirty && die "Worktree has local changes on '$current_branch'; refusing automatic branch switch."

  if git -C "$REPO_DIR" show-ref --verify --quiet "refs/heads/$PROPOSAL_BRANCH"; then
    log "Switching to existing local proposal branch: $PROPOSAL_BRANCH"
    (( DRY_RUN == 1 )) || git -C "$REPO_DIR" switch "$PROPOSAL_BRANCH"
  elif git -C "$REPO_DIR" show-ref --verify --quiet "refs/remotes/$REMOTE/$PROPOSAL_BRANCH"; then
    log "Creating local proposal branch from remote proposal branch."
    (( DRY_RUN == 1 )) || git -C "$REPO_DIR" switch --track -c "$PROPOSAL_BRANCH" "$REMOTE/$PROPOSAL_BRANCH"
  elif git -C "$REPO_DIR" show-ref --verify --quiet "refs/remotes/$REMOTE/$BASE_BRANCH"; then
    log "Bootstrapping local proposal branch from $REMOTE/$BASE_BRANCH."
    (( DRY_RUN == 1 )) || git -C "$REPO_DIR" switch --no-track -c "$PROPOSAL_BRANCH" "$REMOTE/$BASE_BRANCH"
  else
    die "Neither proposal nor base branch exists remotely."
  fi
fi

if (( DRY_RUN == 0 )); then
  current_branch="$(git -C "$REPO_DIR" branch --show-current)"
  [[ "$current_branch" == "$PROPOSAL_BRANCH" ]] || die "Exact proposal branch is required."
fi

PROPOSAL_BRANCH="$PROPOSAL_BRANCH" python3 - "$MANIFEST" <<'PY'
import json, os, pathlib, sys
path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
expected = os.environ["PROPOSAL_BRANCH"]
errors = []
if data.get("branch") != expected: errors.append(f"manifest branch={data.get('branch')!r}, expected={expected!r}")
if data.get("enabled") is not True: errors.append("manifest is disabled")
for key in ("allow_deploy", "allow_migration", "allow_external_messages"):
    if data.get(key) is not False: errors.append(f"unsafe policy: {key} must be false")
if data.get("allow_push") is not False: errors.append("runner allow_push must stay false; wrapper owns reviewed proposal sync")
if data.get("concurrency") != 1: errors.append("concurrency must be exactly 1")
if errors: raise SystemExit("; ".join(errors))
PY

if [[ -f "$PENDING_PUSH" ]]; then
  mapfile -t pending < <(read_pending_push)
  [[ ${#pending[@]} -eq 3 ]] || die "Unable to read pending push checkpoint."
  [[ ! -n "$(git -C "$REPO_DIR" status --porcelain --untracked-files=all)" ]] || die "Pending push exists but worktree is dirty."
  if (( DRY_RUN == 1 )); then
    log "DRY RUN: pending verified SHA ${pending[0]} would be synchronized before model execution."
    exit 0
  fi
  push_exact_sha "${pending[0]}" "${pending[1]}" "${pending[2]}"
fi

if git -C "$REPO_DIR" show-ref --verify --quiet "refs/remotes/$REMOTE/$PROPOSAL_BRANCH"; then
  local_head="$(git -C "$REPO_DIR" rev-parse HEAD)"
  remote_head="$(git -C "$REPO_DIR" rev-parse "$REMOTE/$PROPOSAL_BRANCH")"
  if is_dirty; then
    [[ "$local_head" == "$remote_head" ]] || die "Remote proposal branch changed while local proposal files are dirty. Manual reconciliation required."
  else
    if git -C "$REPO_DIR" merge-base --is-ancestor "$local_head" "$remote_head"; then
      if [[ "$local_head" != "$remote_head" ]]; then
        log "Fast-forwarding proposal branch to remote head."
        (( DRY_RUN == 1 )) || git -C "$REPO_DIR" merge --ff-only "$REMOTE/$PROPOSAL_BRANCH"
      fi
    elif git -C "$REPO_DIR" merge-base --is-ancestor "$remote_head" "$local_head"; then
      die "Local proposal branch is ahead of remote without a pending-push checkpoint. Refusing unknown automatic push."
    else
      die "Local and remote proposal branches diverged. No reset/force is allowed."
    fi
  fi
fi

validate_dirty_paths
head="$(git -C "$REPO_DIR" rev-parse HEAD)"
log "Preflight OK. branch=$PROPOSAL_BRANCH head=$head dirty=$(is_dirty && echo yes || echo no) auto_push=$AUTO_PUSH_PROPOSAL"

if (( DRY_RUN == 1 )); then
  log "DRY RUN complete. No model, checks, commit, push, merge or deploy executed."
  exit 0
fi

set +e
runner_output="$(python3 "$RUNNER" --workspace "$REPO_DIR" --state "$STATE_DIR" --manifest "$MANIFEST" 2>&1)"
runner_rc=$?
set -e
printf '%s\n' "$runner_output"

last_json="$(printf '%s\n' "$runner_output" | tail -n 1)"
status="$(printf '%s' "$last_json" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("status","unknown"))' 2>/dev/null || true)"
task="$(printf '%s' "$last_json" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("task",""))' 2>/dev/null || true)"
[[ -n "$status" ]] || status="unknown"
log "Runner status=$status task=${task:-none} exit=$runner_rc"

if [[ -f "$STATE_DIR/heartbeat.json" && -f "$WATCH" ]]; then
  set +e
  python3 "$WATCH" --heartbeat "$STATE_DIR/heartbeat.json" --state "$WATCH_STATE" --lease-seconds 1800 --progress-seconds 1800
  watch_rc=$?
  set -e
  log "Watch exit=$watch_rc"
fi

if [[ "$status" == "task_verified" ]]; then
  [[ -n "$task" ]] || die "task_verified response did not identify task."
  validate_dirty_paths
  git -C "$REPO_DIR" diff --check

  mapfile -t allowed < <(manifest_allowed_paths)
  [[ ${#allowed[@]} -gt 0 ]] || die "Manifest allowed_paths is empty."

  changed="$(git -C "$REPO_DIR" status --porcelain=v1 --untracked-files=all | sed -E 's/^.. //' | sed -E 's/.* -> //' | sed '/^$/d')"
  if [[ -z "$changed" ]]; then
    log "Task $task verified with no repository delta; no commit/push required."
    exit 0
  fi

  remote_before="$(remote_proposal_sha)"
  current_head="$(git -C "$REPO_DIR" rev-parse HEAD)"
  if [[ -n "$remote_before" && "$remote_before" != "$current_head" ]]; then
    die "Remote SHA changed before commit; refusing to package task $task."
  fi

  mapfile -t changed_paths <<< "$changed"
  git -C "$REPO_DIR" add -- "${changed_paths[@]}"
  staged="$(git -C "$REPO_DIR" diff --cached --name-only)"
  [[ -n "$staged" ]] || die "Task $task reported repository changes but nothing was staged."
  STAGED_PATHS="$staged" python3 - "$MANIFEST" <<'PY'
import json, os, pathlib, sys
m = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
allowed = set(m.get("allowed_paths", []))
paths = [p for p in os.environ.get("STAGED_PATHS", "").splitlines() if p]
invalid = [p for p in paths if p not in allowed]
if invalid: raise SystemExit("staged path outside allowlist: " + ", ".join(invalid))
PY
  git -C "$REPO_DIR" diff --cached --check
  git -C "$REPO_DIR" commit -m "chore(flow): verified proposal $task"
  sha="$(git -C "$REPO_DIR" rev-parse HEAD)"
  [[ -z "$(git -C "$REPO_DIR" status --porcelain --untracked-files=all)" ]] || die "Worktree not clean after verified task commit."
  write_pending_push "$sha" "$remote_before" "$task"
  push_exact_sha "$sha" "$remote_before" "$task"
  exit 0
fi

case "$status" in
  proposal_review_ready)
    is_dirty && die "Proposal queue reports review-ready but worktree is dirty."
    log "Proposal queue reached proposal_review_ready. Release/merge/deploy remain separate and prohibited."
    exit 0
    ;;
  quota|cooldown|auth|daily_limit|paused|locked|blocked)
    exit 20
    ;;
  *)
    exit 30
    ;;
esac
