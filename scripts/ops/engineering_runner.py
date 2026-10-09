"""Sequential proposal runner. Never deploys, migrates, sends, commits or pushes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time
import uuid

CHECKS = {
    'diff': ['git', 'diff', '--check'],
    'backend': ['dotnet', 'run', '--project', 'tests/WazVox.ProtocolTests', '--no-restore'],
    'frontend': ['npm', '--prefix', 'src/frontend', 'run', 'build'],
}
SCHEMA = {'type': 'object', 'additionalProperties': False,
          'properties': {'status': {'type': 'string', 'enum': ['completed', 'blocked']},
                         'summary': {'type': 'string'},
                         'evidence_paths': {'type': 'array', 'items': {'type': 'string'}}},
          'required': ['status', 'summary', 'evidence_paths']}


def classify(raw):
    for category, pattern in [('quota', r'429|quota|rate.?limit|usage.?limit|out of credits|credits.*exhaust'),
                              ('auth', r'401|unauthorized|not logged|invalid.*token'),
                              ('network', r'connection|network|timed.out|stream disconnected')]:
        if re.search(pattern, raw, re.I):
            return category
    return 'model_failed'


def secret_like(raw):
    return bool(re.search(r'sk-[A-Za-z0-9_-]{12,}|PRIVATE KEY|Bearer\s+[A-Za-z0-9._-]{12,}|'
                          r'(?:password|senha|access_token|api_key)\s*[=:]\s*[^\s,]{8,}', raw, re.I))


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('state_symlink')
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def changed_paths(workspace, run):
    result = run(['git', 'diff', '--name-only', 'HEAD'], cwd=workspace)
    extra = run(['git', 'ls-files', '--others', '--exclude-standard'], cwd=workspace)
    if result.returncode or extra.returncode:
        raise ValueError('git_unavailable')
    return set(result.stdout.splitlines()) | set(extra.stdout.splitlines())


def validate_paths(workspace, paths, allowed):
    for name in paths:
        path = workspace / name
        if (name not in allowed or path.is_symlink() or not path.resolve().is_relative_to(workspace)
                or any(p in {'.git', '.codex', '.runtime'} for p in Path(name).parts)
                or path.name.startswith('.env')):
            raise ValueError('scope_violation')
        if path.is_file() and (path.stat().st_size > 1_000_000 or secret_like(path.read_text(encoding='utf-8'))):
            raise ValueError('private_or_oversized_output')


def command(argv, *, cwd, timeout=900):
    # Inherit only CLI necessities. No DB/mail/cloud/token environment reaches the model.
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'CODEX_HOME', 'LANG', 'TMPDIR') if k in os.environ}
    env['GIT_TERMINAL_PROMPT'] = '0'
    proc = subprocess.Popen(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=(os.name != 'nt'))
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name != 'nt':
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        proc.communicate()
        raise
    return subprocess.CompletedProcess(argv, proc.returncode, out, err)


class Runner:
    def __init__(self, workspace, state, manifest, run=command, now=time.time):
        self.workspace = Path(workspace).resolve()
        self.state = Path(state).resolve()
        self.manifest = json.loads(Path(manifest).read_text(encoding='utf-8'))
        self.run, self.now = run, now
        if (self.state.is_relative_to(self.workspace) or not (self.workspace / '.git').is_dir()
                or (self.workspace / '.git').is_symlink()):
            raise ValueError('isolated_git_workspace_required')
        if (self.manifest.get('concurrency') != 1 or len(self.manifest.get('roles', [])) != 10
                or self.manifest.get('allow_deploy') is not False
                or self.manifest.get('allow_migration') is not False
                or self.manifest.get('allow_external_messages') is not False
                or self.manifest.get('allow_push') is not False):
            raise ValueError('unsafe_policy')
        self.state.mkdir(parents=True, exist_ok=True)

    def save(self, data):
        data['observed_at'] = self.now()
        data.setdefault('run_id', 'engineering-' + uuid.uuid4().hex)
        atomic(self.state / 'checkpoint.json', data)
        status = data.get('status', 'starting')
        reasons = {'quota': 'quota', 'daily_limit': 'quota', 'auth': 'authentication',
                   'checks_failed': 'checks', 'protected_git_change': 'conflict',
                   'scope_violation': 'conflict', 'private_workspace': 'configuration',
                   'private_or_oversized_output': 'configuration', 'paused': 'manual'}
        source = data.get('source_commit', '')
        valid_source = isinstance(source, str) and re.fullmatch(r'[a-f0-9]{40}', source) and source != '0' * 40
        progress = data.get('progress_at')
        reason = None
        if not valid_source:
            heartbeat_status, reason = 'blocked', 'configuration'
            source = '0' * 40
        elif status in ('task_verified', 'proposal_ready'):
            heartbeat_status = 'succeeded'
        elif status in ('running', 'starting'):
            heartbeat_status = 'running' if progress is not None else 'starting'
        else:
            heartbeat_status, reason = 'blocked', reasons.get(status, 'dependency')
        iso = lambda value: datetime.fromtimestamp(value, timezone.utc).isoformat()
        atomic(self.state / 'heartbeat.json', dict(schema_version=1, run_id=data['run_id'],
            module_id=data.get('current_task', 'unassigned'), status=heartbeat_status,
            updated_at=iso(data['observed_at']), progress_at=None if progress is None else iso(progress),
            pid=os.getpid() if heartbeat_status in ('starting', 'running') else None,
            blocked_reason=reason, source_commit=source))

    def tick(self):
        # Linux flock releases on crash. Windows unit tests use cycle directly.
        import fcntl
        with (self.state / 'runner.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {'status': 'locked'}
            return self.cycle()

    def cycle(self):
        path = self.state / 'checkpoint.json'
        data = json.loads(path.read_text()) if path.exists() else {'completed': [], 'calls_today': 0}
        if not self.manifest.get('enabled') or (self.state / 'PAUSE').exists():
            data['status'] = 'paused'
            self.save(data)
            return {'status': 'paused'}
        if data.get('status') in ('scope_violation', 'private_or_oversized_output', 'checks_failed', 'blocked',
                                  'protected_git_change', 'private_workspace'):
            self.save(data)
            return {'status': data['status']}
        if data.get('cooldown_until', 0) > self.now():
            self.save(data)
            return {'status': 'cooldown'}
        day = time.strftime('%Y-%m-%d', time.gmtime(self.now()))
        if data.get('day') != day:
            data.update(day=day, calls_today=0)
        if data['calls_today'] >= 12:
            data['status'] = 'daily_limit'
            self.save(data)
            return {'status': 'daily_limit'}
        pending = [t for t in self.manifest['tasks'] if t['id'] not in data['completed']]
        if not pending:
            data['status'] = 'proposal_ready'
            self.save(data)
            return {'status': 'proposal_ready'}
        task = pending[0]
        allowed = set(self.manifest['allowed_paths'])
        try:
            branch = self.run(['git', 'branch', '--show-current'], cwd=self.workspace)
            if branch.returncode or not branch.stdout.strip().startswith('codex/'):
                raise ValueError('proposal_branch_required')
            validate_paths(self.workspace, changed_paths(self.workspace, self.run), allowed)
            for private in self.workspace.rglob('.env*'):
                if private.name != '.env.example' and '.git' not in private.parts and 'node_modules' not in private.parts:
                    raise ValueError('private_workspace')
            head = self.run(['git', 'rev-parse', 'HEAD'], cwd=self.workspace)
            if head.returncode or not re.fullmatch(r'[a-f0-9]{40}', head.stdout.strip()) or head.stdout.strip() == '0' * 40:
                raise ValueError('source_commit_unavailable')
            data['source_commit'] = head.stdout.strip()
            config_path = self.workspace / '.git/config'
            config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest() if config_path.exists() else None
            auth = self.run(['codex', 'login', 'status'], cwd=self.workspace, timeout=15)
            if auth.returncode:
                data.update(status='auth', cooldown_until=self.now() + 1800)
                self.save(data)
                return {'status': 'auth'}
            for check in task['checks']:
                if check not in CHECKS:
                    raise ValueError('untrusted_check')
            data.update(status='running', current_task=task['id'], calls_today=data['calls_today'] + 1,
                        started_at=self.now(), heartbeat_at=self.now())
            self.save(data)
            atomic(self.state / 'result-schema.json', SCHEMA)
            # Checkpoint context resumes the same task after interruption. No inferred session ID.
            prompt = ('Execute only this authorized Flow proposal task: ' + task['instruction'] +
                      '\nAllowed files: ' + json.dumps(sorted(allowed)) +
                      '\nNo deploy, migrations, external messages, credentials, git commits or push. '
                      'Use synthetic data only. Never modify runtime or controller state. '
                      'Previous completed task IDs: ' + json.dumps(data['completed']) +
                      '\nReturn blocked if a real dependency is missing. Evidence paths must be in the allowlist.')
            result_file = self.state / 'result.json'
            if result_file.exists():
                result_file.unlink()
            argv = ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--sandbox', 'workspace-write',
                    '-c', 'approval_policy="never"', '--json', '--cd', str(self.workspace),
                    '--output-schema', str(self.state / 'result-schema.json'),
                    '--output-last-message', str(result_file), prompt]
            if self.run is command:
                result = self.model(argv, data)
            else:
                result = self.run(argv, cwd=self.workspace, timeout=900)
            if result.returncode:
                category = classify(result.stdout + result.stderr)
                data.update(status=category, cooldown_until=self.now() + (21600 if category == 'quota' else 1800))
                self.save(data)
                return {'status': category}
            after_head = self.run(['git', 'rev-parse', 'HEAD'], cwd=self.workspace)
            after_config = hashlib.sha256(config_path.read_bytes()).hexdigest() if config_path.exists() else None
            if head.returncode or after_head.returncode or head.stdout != after_head.stdout or config_hash != after_config:
                raise ValueError('protected_git_change')
            report = json.loads(result_file.read_text(encoding='utf-8'))
            if (set(report) != set(SCHEMA['required']) or report['status'] not in ('completed', 'blocked')
                    or not isinstance(report['summary'], str) or len(report['summary']) > 2000
                    or not isinstance(report['evidence_paths'], list) or secret_like(json.dumps(report))):
                raise ValueError('invalid_result')
            paths = changed_paths(self.workspace, self.run)
            validate_paths(self.workspace, paths | set(report['evidence_paths']), allowed)
            if any(not (self.workspace / p).is_file() for p in report['evidence_paths']):
                raise ValueError('missing_evidence')
            if report['status'] == 'blocked':
                data['status'] = 'blocked'
            else:
                for check in task['checks']:
                    checked = self.run(CHECKS[check], cwd=self.workspace, timeout=900)
                    if checked.returncode:
                        raise ValueError('checks_failed')
                validate_paths(self.workspace, changed_paths(self.workspace, self.run), allowed)
                # Evidence hash/diff proves progress; heartbeat/PID only proves observation.
                diff = self.run(['git', 'diff', '--binary', 'HEAD', '--', *sorted(paths)], cwd=self.workspace)
                if diff.returncode or secret_like(diff.stdout):
                    raise ValueError('unsafe_patch')
                patch = self.state / (task['id'] + '.patch')
                patch.write_text(diff.stdout, encoding='utf-8')
                # git diff excludes untracked additions; preserve every allowlisted changed file too.
                for name in paths:
                    source = self.workspace / name
                    if source.is_file():
                        snapshot = self.state / 'artifacts' / task['id'] / name
                        snapshot.parent.mkdir(parents=True, exist_ok=True)
                        snapshot.write_bytes(source.read_bytes())
                evidence = {p: hashlib.sha256((self.workspace / p).read_bytes()).hexdigest()
                            for p in report['evidence_paths']}
                atomic(self.state / (task['id'] + '.json'), dict(report, evidence_hashes=evidence,
                       patch_sha256=hashlib.sha256(diff.stdout.encode()).hexdigest(), checks=task['checks']))
                if not paths and not evidence:
                    raise ValueError('no_progress_evidence')
                data['completed'].append(task['id'])
                data.update(status='task_verified', progress_at=self.now(), cooldown_until=0)
            self.save(data)
            return {'status': data['status'], 'task': task['id']}
        except subprocess.TimeoutExpired:
            data.update(status='timeout', cooldown_until=self.now() + 1800)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            safe = str(exc) if str(exc) in {'scope_violation', 'private_or_oversized_output', 'checks_failed',
                'invalid_result', 'missing_evidence', 'no_progress_evidence', 'proposal_branch_required',
                'unsafe_patch', 'untrusted_check', 'private_workspace', 'protected_git_change', 'source_commit_unavailable'} else 'runner_error'
            data.update(status=safe, cooldown_until=self.now() + 1800)
        self.save(data)
        return {'status': data['status']}

    def model(self, argv, data):
        env = {k: os.environ[k] for k in ('PATH', 'HOME', 'CODEX_HOME', 'LANG', 'TMPDIR') if k in os.environ}
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            process = subprocess.Popen(argv, cwd=self.workspace, env=env, stdout=out, stderr=err,
                                       start_new_session=True)
            started = self.now()
            try:
                while process.poll() is None:
                    if self.now() - started >= 900:
                        raise subprocess.TimeoutExpired('codex', 900)
                    data['heartbeat_at'] = self.now()
                    self.save(data)
                    time.sleep(30)
            except BaseException:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
            out.seek(0); err.seek(0)
            return subprocess.CompletedProcess(argv, process.returncode,
                out.read(2_000_000).decode(errors='replace'), err.read(2_000_000).decode(errors='replace'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--state', required=True)
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    report = Runner(args.workspace, args.state, args.manifest).tick()
    print(json.dumps(report))
    return 0 if report['status'] in ('task_verified', 'proposal_ready', 'cooldown', 'locked', 'daily_limit', 'paused') else 2


if __name__ == '__main__':
    raise SystemExit(main())
