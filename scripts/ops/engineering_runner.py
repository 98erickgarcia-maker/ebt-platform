"""Sequential proposal runner; optional controller-only verified branch sync, no deploy."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shlex
import subprocess
import tempfile
import time
import uuid


def untrusted_identity():
    """Drop all supplementary groups for model and generated-code checks on Linux."""
    if os.name != 'nt' and os.getuid() == 0:
        import pwd
        user = pwd.getpwnam('ebt-scout')
        return dict(user=user.pw_uid, group=user.pw_gid, extra_groups=[])
    return {}


def controller_git(argv, cwd):
    if argv and argv[0] == 'git':
        return ['git', '-c', 'safe.directory=' + str(cwd), '-c', 'core.hooksPath=/dev/null',
                '-c', 'core.fsmonitor=false', '-c', 'commit.gpgsign=false', *argv[1:]]
    return argv

CHECKS = {
    'diff': ['git', 'diff', '--check'],
    'backend': ['dotnet', 'run', '--project', 'tests/WazVox.ProtocolTests', '--no-restore'],
    'frontend': ['npm', '--prefix', 'src/frontend', 'run', 'build'],
}
PUSH_REPO = '98erickgarcia-maker/ebt-platform'
PUSH_BRANCH = 'codex/flow-history-proposal-vps-20261009'
PUSH_REMOTE = 'git@github.com:' + PUSH_REPO + '.git'
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
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'CODEX_HOME', 'LANG', 'TMPDIR', 'GIT_CONFIG_GLOBAL') if k in os.environ}
    env['GIT_TERMINAL_PROMPT'] = '0'
    identity = untrusted_identity() if argv[0] in ('codex', 'dotnet', 'npm') else {}
    if argv[0] == 'git' and os.name != 'nt':
        identity['umask'] = 0o022
    argv = controller_git(argv, cwd)
    proc = subprocess.Popen(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=(os.name != 'nt'), **identity)
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
                or type(self.manifest.get('allow_push')) is not bool):
            raise ValueError('unsafe_policy')
        if self.manifest['allow_push'] and (self.manifest.get('repository') != PUSH_REPO
                or self.manifest.get('branch') != PUSH_BRANCH):
            raise ValueError('unsafe_push_target')
        if self.run is command and self.manifest['allow_push'] and (os.name == 'nt' or os.getuid() != 0):
            raise ValueError('controller_identity_required')
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
        # Sanitized observation is readable by the separate watchdog, never the checkpoint/key.
        os.chmod(self.state / 'heartbeat.json', 0o640)

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
        if data.get('status') == 'awaiting_sync':
            return self.sync(data)
        if data.get('status') == 'preparing_sync':
            # Crash between staging/commit and checkpoint requires explicit recovery, never another model.
            self.save(data)
            return {'status': 'preparing_sync'}
        if data.get('status') in ('scope_violation', 'private_or_oversized_output', 'checks_failed', 'blocked',
                                  'protected_git_change', 'private_workspace', 'task_scope_violation',
                                  'task_file_limit', 'invalid_task_policy'):
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
            dependencies = task.get('depends_on', [])
            task_names = {t['id'] for t in self.manifest['tasks']}
            assigned = task.get('write_paths', sorted(allowed))
            maximum = task.get('max_changed_files', len(assigned) if isinstance(assigned, list) else len(allowed))
            if (not isinstance(dependencies, list) or any(not isinstance(item, str) for item in dependencies)
                    or len(set(dependencies)) != len(dependencies) or not set(dependencies) <= task_names
                    or task['id'] in dependencies or not isinstance(assigned, list)
                    or any(not isinstance(item, str) for item in assigned)
                    or len(set(assigned)) != len(assigned) or not set(assigned) <= allowed
                    or type(maximum) is not int or maximum < 0 or maximum > len(assigned)):
                raise ValueError('invalid_task_policy')
            if not set(dependencies) <= set(data['completed']):
                raise ValueError('dependency_missing')
            assigned = set(assigned)

            def snapshot():
                validate_paths(self.workspace, allowed, allowed)
                return {name: hashlib.sha256((self.workspace / name).read_bytes()).hexdigest()
                        if (self.workspace / name).is_file() else None for name in allowed}

            def task_delta(before):
                current = snapshot()
                delta = {name for name in allowed if current[name] != before[name]}
                if not delta <= assigned:
                    raise ValueError('task_scope_violation')
                if len(delta) > maximum:
                    raise ValueError('task_file_limit')
                return delta, current

            self.isolation_guard()
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
            before_files = snapshot()
            data.update(status='running', current_task=task['id'], calls_today=data['calls_today'] + 1,
                        started_at=self.now(), heartbeat_at=self.now())
            self.save(data)
            io = self.state / 'model-io'
            io.mkdir(exist_ok=True)
            if self.run is command and os.name != 'nt' and os.getuid() == 0:
                import pwd
                account = pwd.getpwnam('ebt-scout')
                info = io.stat()
                if info.st_uid != 0 or info.st_gid != account.pw_gid or info.st_mode & 0o007:
                    raise ValueError('model_io_not_provisioned')
            atomic(io / 'result-schema.json', SCHEMA)
            os.chmod(io / 'result-schema.json', 0o644)
            # Checkpoint context resumes the same task after interruption. No inferred session ID.
            prompt = ('Execute only this authorized Flow proposal task: ' + task['instruction'] +
                      '\nTask writable files: ' + json.dumps(sorted(assigned)) +
                      '\nMaximum changed files for this invocation: ' + str(maximum) +
                      '\nGlobal evidence file allowlist: ' + json.dumps(sorted(allowed)) +
                      '\nNo deploy, migrations, external messages, credentials, git commits or push. '
                      'Use synthetic data only. Never modify runtime or controller state. '
                      'Previous completed task IDs: ' + json.dumps(data['completed']) +
                      '\nReturn blocked if a real dependency is missing. Evidence paths must be in the allowlist.')
            result_file = io / 'result.json'
            if result_file.exists():
                result_file.unlink()
            argv = ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--sandbox', 'workspace-write',
                    '-c', 'approval_policy="never"', '--json', '--cd', str(self.workspace),
                    '--output-schema', str(io / 'result-schema.json'),
                    '--output-last-message', str(result_file), prompt]
            if self.run is command:
                result = self.model(argv, data)
            else:
                result = self.run(argv, cwd=self.workspace, timeout=900)
            validate_paths(self.workspace, changed_paths(self.workspace, self.run), allowed)
            paths, after_files = task_delta(before_files)
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
            validate_paths(self.workspace, changed_paths(self.workspace, self.run) | set(report['evidence_paths']), allowed)
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
                paths, after_files = task_delta(before_files)
                check_head = self.run(['git', 'rev-parse', 'HEAD'], cwd=self.workspace)
                check_config = hashlib.sha256(config_path.read_bytes()).hexdigest() if config_path.exists() else None
                if check_head.returncode or check_head.stdout != head.stdout or check_config != config_hash:
                    raise ValueError('protected_git_change')
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
                       patch_sha256=hashlib.sha256(diff.stdout.encode()).hexdigest(), checks=task['checks'],
                       changed_paths=sorted(paths), before_hashes={p: before_files[p] for p in sorted(paths)},
                       after_hashes={p: after_files[p] for p in sorted(paths)}, dependencies=dependencies))
                if not paths and not evidence:
                    raise ValueError('no_progress_evidence')
                if self.manifest['allow_push']:
                    self.verify_push_target()
                    data.update(status='preparing_sync', sync_task=task['id'])
                    self.save(data)
                    if paths:
                        staged = self.run(['git', 'add', '--', *sorted(paths)], cwd=self.workspace)
                        if staged.returncode:
                            raise ValueError('commit_failed')
                        committed = self.run(['git', 'commit', '-m', 'EBT verified proposal ' + task['id']], cwd=self.workspace)
                        if committed.returncode:
                            raise ValueError('commit_failed')
                    clean = self.run(['git', 'status', '--porcelain'], cwd=self.workspace)
                    if clean.returncode or clean.stdout.strip():
                        raise ValueError('unclean_after_commit')
                    sha = self.run(['git', 'rev-parse', 'HEAD'], cwd=self.workspace)
                    if sha.returncode or not re.fullmatch(r'[0-9a-f]{40}', sha.stdout.strip()):
                        raise ValueError('invalid_commit')
                    data.update(status='awaiting_sync', sync_sha=sha.stdout.strip(), sync_task=task['id'])
                    self.save(data)
                    return self.sync(data)
                data['completed'].append(task['id'])
                data.update(status='task_verified', progress_at=self.now(), cooldown_until=0)
            self.save(data)
            return {'status': data['status'], 'task': task['id']}
        except subprocess.TimeoutExpired:
            data.update(status='timeout', cooldown_until=self.now() + 1800)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            safe = str(exc) if str(exc) in {'scope_violation', 'private_or_oversized_output', 'checks_failed',
                'invalid_result', 'missing_evidence', 'no_progress_evidence', 'proposal_branch_required',
                'unsafe_patch', 'untrusted_check', 'private_workspace', 'protected_git_change', 'source_commit_unavailable',
                'commit_failed', 'unclean_after_commit', 'invalid_commit', 'unsafe_push_target', 'invalid_task_policy',
                'dependency_missing', 'task_scope_violation', 'task_file_limit'} else 'runner_error'
            data.update(status=safe, cooldown_until=self.now() + 1800)
        self.save(data)
        return {'status': data['status']}

    def verify_push_target(self):
        self.isolation_guard()
        if (not self.manifest['allow_push'] or self.manifest.get('repository') != PUSH_REPO
                or self.manifest.get('branch') != PUSH_BRANCH):
            raise ValueError('unsafe_push_target')
        branch = self.run(['git', 'branch', '--show-current'], cwd=self.workspace)
        remote = self.run(['git', 'remote', 'get-url', '--push', 'origin'], cwd=self.workspace)
        read_remote = self.run(['git', 'remote', 'get-url', 'origin'], cwd=self.workspace)
        if branch.returncode or branch.stdout.strip() != PUSH_BRANCH or remote.returncode or read_remote.returncode:
            raise ValueError('unsafe_push_target')
        if remote.stdout.strip() != PUSH_REMOTE or read_remote.stdout.strip() != PUSH_REMOTE:
            raise ValueError('unsafe_push_target')

    def isolation_guard(self):
        if self.run is not command or not self.manifest['allow_push']:
            return
        if os.name == 'nt' or os.getuid() != 0:
            raise ValueError('controller_identity_required')
        for path in (self.state, self.workspace / '.git', *(self.workspace / '.git').rglob('*')):
            info = path.lstat()
            if path.is_symlink() or info.st_uid != 0 or info.st_mode & 0o022:
                raise ValueError('controller_metadata_unprotected')

    def transport(self, argv):
        if self.run is not command:
            return self.run(argv, cwd=self.workspace, timeout=120)
        key = Path(os.environ.get('EBT_ENGINEERING_GIT_KEY', ''))
        known = Path(os.environ.get('EBT_ENGINEERING_KNOWN_HOSTS', ''))
        for path in (key, known):
            if not path.is_absolute() or path.is_symlink() or not path.is_file() or path.resolve().is_relative_to(self.workspace):
                raise ValueError('git_access_unavailable')
            info = path.stat()
            if info.st_mode & 0o077 or info.st_uid != 0 or os.getuid() != 0:
                raise ValueError('git_access_unavailable')
        env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG', 'TMPDIR') if k in os.environ}
        env['GIT_TERMINAL_PROMPT'] = '0'
        env['GIT_SSH_COMMAND'] = ('/usr/bin/ssh -F /dev/null -i ' + shlex.quote(str(key)) + ' -o IdentitiesOnly=yes '
            '-o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=' + shlex.quote(str(known)))
        return subprocess.run(controller_git(argv, self.workspace), cwd=self.workspace, env=env,
                              text=True, capture_output=True, timeout=120, umask=0o022)

    def sync(self, data):
        # Retry this reviewed commit only; never run a model while synchronization is pending.
        try:
            self.verify_push_target()
            if (not re.fullmatch(r'[0-9a-f]{40}', data.get('sync_sha', ''))
                    or data.get('sync_task') not in {t['id'] for t in self.manifest['tasks']}):
                raise ValueError('invalid_sync_checkpoint')
            sha = self.run(['git', 'rev-parse', 'HEAD'], cwd=self.workspace)
            clean = self.run(['git', 'status', '--porcelain'], cwd=self.workspace)
            if sha.returncode or sha.stdout.strip() != data['sync_sha'] or clean.returncode or clean.stdout.strip():
                raise ValueError('sync_workspace_changed')
            pushed = self.transport(['git', 'push', 'origin', data['sync_sha'] + ':refs/heads/' + PUSH_BRANCH])
            if pushed.returncode:
                data['sync_error'] = classify(pushed.stdout + pushed.stderr)
            else:
                remote = self.transport(['git', 'ls-remote', 'origin', 'refs/heads/' + PUSH_BRANCH])
                expected = data['sync_sha'] + '\trefs/heads/' + PUSH_BRANCH
                if remote.returncode or remote.stdout.strip().splitlines() != [expected]:
                    data['sync_error'] = 'remote_mismatch'
                else:
                    if data['sync_task'] not in data['completed']:
                        data['completed'].append(data['sync_task'])
                    data.update(status='task_verified', progress_at=self.now(), cooldown_until=0,
                                synced_sha=data['sync_sha'])
                    data.pop('sync_error', None)
        except (ValueError, OSError, KeyError, subprocess.TimeoutExpired):
            data['sync_error'] = 'sync_access_or_workspace_error'
        self.save(data)
        return {'status': data['status'], 'task': data.get('sync_task')}

    def model(self, argv, data):
        env = {k: os.environ[k] for k in ('PATH', 'HOME', 'CODEX_HOME', 'LANG', 'TMPDIR', 'GIT_CONFIG_GLOBAL') if k in os.environ}
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            process = subprocess.Popen(argv, cwd=self.workspace, env=env, stdout=out, stderr=err,
                                       start_new_session=True, **untrusted_identity())
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
