import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

MODULE = Path(__file__).resolve().parents[2] / 'scripts/ops/engineering_runner.py'
spec = importlib.util.spec_from_file_location('engineering_runner', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        (self.workspace / '.git').mkdir()
        self.state = self.root / 'state'
        self.manifest = self.root / 'manifest.json'
        self.policy = {'enabled': True, 'concurrency': 1, 'roles': list(range(10)),
                       'allow_deploy': False, 'allow_migration': False,
                       'allow_external_messages': False, 'allow_push': False,
                       'branch': 'codex/proposal',
                       'allowed_paths': ['proof.md'],
                       'tasks': [{'id': 'T1', 'instruction': 'review', 'checks': ['diff']},
                                 {'id': 'T2', 'instruction': 'review', 'checks': ['diff']}]}
        self.manifest.write_text(json.dumps(self.policy))
        self.calls = []

    def fake(self, argv, **kwargs):
        self.calls.append(argv)
        out = ''
        if argv[:3] == ['git', 'branch', '--show-current']:
            out = 'codex/proposal\n'
        if argv == ['git', 'rev-parse', 'HEAD']:
            out = 'a' * 40 + '\n'
        if argv[:3] == ['git', 'ls-files', '--others']:
            out = 'proof.md\n' if (self.workspace / 'proof.md').exists() else ''
        if argv[:2] == ['codex', 'exec']:
            (self.workspace / 'proof.md').write_text('synthetic evidence')
            (self.state / 'model-io/result.json').write_text(json.dumps(
                {'status': 'completed', 'summary': 'reviewed', 'evidence_paths': ['proof.md']}))
        return subprocess.CompletedProcess(argv, 0, out, '')

    def runner(self, fake=None):
        return mod.Runner(self.workspace, self.state, self.manifest, fake or self.fake, now=lambda: 100000)

    def test_wrong_proposal_branch_is_rejected(self):
        def wrong_branch(argv, **kwargs):
            if argv[:3] == ['git', 'branch', '--show-current']:
                return subprocess.CompletedProcess(argv, 0, 'codex/other\n', '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(wrong_branch).cycle()['status'], 'proposal_branch_required')
        self.assertFalse(any(argv[:2] == ['codex', 'exec'] for argv in self.calls))

    def test_flow_backend_check_is_dedicated(self):
        self.assertEqual(mod.CHECKS['flow_backend'],
            ['dotnet', 'run', '--project', 'tests/WazVox.ProtocolTests', '--no-restore', '--', '--flow-history'])

    def test_flow_backend_gate_rejects_generic_harness(self):
        self.policy['tasks'][0]['checks'] = ['flow_backend']
        self.manifest.write_text(json.dumps(self.policy))
        self.assertEqual(self.runner().cycle()['status'], 'flow_gate_missing')
        self.assertFalse(any(argv[:2] == ['dotnet', 'run'] for argv in self.calls))

    def test_one_task_per_tick_and_no_publish(self):
        self.assertEqual(self.runner().cycle()['status'], 'task_verified')
        data = json.loads((self.state / 'checkpoint.json').read_text())
        self.assertEqual(data['completed'], ['T1'])
        self.assertEqual(sum(argv[:2] == ['codex', 'exec'] for argv in self.calls), 1)
        self.assertFalse(any('push' in argv or 'commit' in argv for argv in self.calls))
        self.assertEqual((self.state / 'artifacts/T1/proof.md').read_text(), 'synthetic evidence')

    def test_quota_backoff_and_output_not_persisted(self):
        def fail(argv, **kwargs):
            if argv[:2] == ['codex', 'exec']:
                return subprocess.CompletedProcess(argv, 1, '', '429 usage limit private provider detail')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(fail).cycle()['status'], 'quota')
        data = json.loads((self.state / 'checkpoint.json').read_text())
        self.assertEqual(data['cooldown_until'], 121600)
        self.assertNotIn('private provider', json.dumps(data))
        self.assertEqual(self.runner(fail).cycle()['status'], 'cooldown')

    def test_outside_allowlist_stops_before_model(self):
        def wrong(argv, **kwargs):
            if argv[:3] == ['git', 'ls-files', '--others']:
                return subprocess.CompletedProcess(argv, 0, 'unauthorized.txt\n', '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(wrong).cycle()['status'], 'scope_violation')
        self.assertFalse(any(argv[:2] == ['codex', 'exec'] for argv in self.calls))

    def test_failed_check_not_completed(self):
        def fail(argv, **kwargs):
            if argv == ['git', 'diff', '--check']:
                return subprocess.CompletedProcess(argv, 1, '', '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(fail).cycle()['status'], 'checks_failed')
        self.assertEqual(json.loads((self.state / 'checkpoint.json').read_text())['completed'], [])

    def test_unsafe_policy_rejected(self):
        self.policy['allow_deploy'] = True
        self.manifest.write_text(json.dumps(self.policy))
        with self.assertRaisesRegex(ValueError, 'unsafe_policy'):
            self.runner()

    def test_summary_does_not_prove_progress(self):
        def empty(argv, **kwargs):
            if argv[:2] == ['codex', 'exec']:
                (self.state / 'model-io/result.json').write_text(json.dumps(
                    {'status': 'completed', 'summary': 'done', 'evidence_paths': []}))
                return subprocess.CompletedProcess(argv, 0, '', '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(empty).cycle()['status'], 'no_progress_evidence')

    def test_error_classification(self):
        self.assertEqual(mod.classify('401 Unauthorized'), 'auth')
        self.assertEqual(mod.classify('stream disconnected'), 'network')
        self.assertEqual(mod.classify('other private info'), 'model_failed')

    def test_controller_git_disables_hooks_and_fsmonitor(self):
        argv = mod.controller_git(['git', 'push', 'origin', 'sha:ref'], self.workspace)
        self.assertIn('core.hooksPath=/dev/null', argv)
        self.assertIn('core.fsmonitor=false', argv)
        self.assertIn('commit.gpgsign=false', argv)
        self.assertEqual(argv[-3:], ['push', 'origin', 'sha:ref'])

    def test_generated_check_drops_identity_and_key_environment(self):
        process = mock.Mock()
        process.communicate.return_value = ('synthetic', '')
        process.returncode = 0
        with mock.patch.object(mod, 'untrusted_identity', return_value={'user': 111, 'group': 222, 'extra_groups': []}), \
             mock.patch.object(mod.subprocess, 'Popen', return_value=process) as spawn, \
             mock.patch.dict(mod.os.environ, {'EBT_ENGINEERING_GIT_KEY': '/outside/private-fixture',
                                            'DATABASE_PASSWORD': 'private-fixture'}):
            mod.command(['dotnet', 'run', '--project', 'synthetic'], cwd=self.workspace)
        kwargs = spawn.call_args.kwargs
        self.assertEqual(kwargs['user'], 111)
        self.assertEqual(kwargs['group'], 222)
        self.assertEqual(kwargs['extra_groups'], [])
        self.assertNotIn('EBT_ENGINEERING_GIT_KEY', kwargs['env'])
        self.assertNotIn('DATABASE_PASSWORD', kwargs['env'])

    def test_git_controller_not_dropped_and_hooks_disabled(self):
        process = mock.Mock()
        process.communicate.return_value = ('', '')
        process.returncode = 0
        with mock.patch.object(mod.subprocess, 'Popen', return_value=process) as spawn:
            mod.command(['git', 'commit', '-m', 'fixed'], cwd=self.workspace)
        self.assertNotIn('user', spawn.call_args.kwargs)
        self.assertIn('core.hooksPath=/dev/null', spawn.call_args.args[0])

    def enable_push(self):
        self.policy.update(allow_push=True, repository=mod.PUSH_REPO, branch=mod.PUSH_BRANCH)
        self.manifest.write_text(json.dumps(self.policy))

    def push_fake(self, argv, **kwargs):
        if argv == ['git', 'branch', '--show-current']:
            return subprocess.CompletedProcess(argv, 0, mod.PUSH_BRANCH + '\n', '')
        if argv[:3] == ['git', 'remote', 'get-url']:
            return subprocess.CompletedProcess(argv, 0, mod.PUSH_REMOTE + '\n', '')
        if argv[:2] == ['git', 'ls-remote']:
            self.calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, 'a' * 40 + '\trefs/heads/' + mod.PUSH_BRANCH + '\n', '')
        return self.fake(argv, **kwargs)

    def test_controlled_push_advances_only_on_exact_remote(self):
        self.enable_push()
        self.assertEqual(self.runner(self.push_fake).cycle()['status'], 'task_verified')
        data = json.loads((self.state / 'checkpoint.json').read_text())
        self.assertEqual(data['completed'], ['T1'])
        self.assertEqual(data['synced_sha'], 'a' * 40)
        self.assertIn(['git', 'add', '--', 'proof.md'], self.calls)
        self.assertIn(['git', 'push', 'origin', 'a' * 40 + ':refs/heads/' + mod.PUSH_BRANCH], self.calls)
        self.assertFalse(any('--force' in arg for argv in self.calls for arg in argv))

    def test_push_failure_retries_same_commit_without_model(self):
        self.enable_push()
        def failing(argv, **kwargs):
            if argv[:2] == ['git', 'push']:
                return subprocess.CompletedProcess(argv, 1, '', 'network private server detail')
            return self.push_fake(argv, **kwargs)
        self.assertEqual(self.runner(failing).cycle()['status'], 'awaiting_sync')
        self.calls.clear()
        self.assertEqual(self.runner(self.push_fake).cycle()['status'], 'task_verified')
        self.assertFalse(any(argv[:2] in (['codex', 'exec'], ['git', 'commit']) for argv in self.calls))
        self.assertEqual(json.loads((self.state / 'checkpoint.json').read_text())['completed'], ['T1'])

    def test_remote_mismatch_keeps_task_pending(self):
        self.enable_push()
        def wrong(argv, **kwargs):
            if argv[:2] == ['git', 'ls-remote']:
                return subprocess.CompletedProcess(argv, 0, 'b' * 40 + '\trefs/heads/' + mod.PUSH_BRANCH, '')
            return self.push_fake(argv, **kwargs)
        self.assertEqual(self.runner(wrong).cycle()['status'], 'awaiting_sync')
        data = json.loads((self.state / 'checkpoint.json').read_text())
        self.assertEqual(data['completed'], [])
        self.assertEqual(data['sync_error'], 'remote_mismatch')

    def test_wrong_push_remote_never_commits(self):
        self.enable_push()
        def wrong(argv, **kwargs):
            if argv[:3] == ['git', 'remote', 'get-url']:
                return subprocess.CompletedProcess(argv, 0, 'git@github.com:other/repo.git', '')
            return self.push_fake(argv, **kwargs)
        self.assertEqual(self.runner(wrong).cycle()['status'], 'unsafe_push_target')
        self.assertFalse(any(argv[:2] == ['git', 'commit'] for argv in self.calls))

    def test_model_commit_is_rejected(self):
        heads = []
        def changed(argv, **kwargs):
            if argv == ['git', 'rev-parse', 'HEAD']:
                heads.append(1)
                return subprocess.CompletedProcess(argv, 0, 'a' * 40 if len(heads) == 1 else 'b' * 40, '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(changed).cycle()['status'], 'protected_git_change')
        self.assertEqual(json.loads((self.state / 'checkpoint.json').read_text())['completed'], [])

    def test_auth_failure_does_not_call_model(self):
        def fail(argv, **kwargs):
            if argv == ['codex', 'login', 'status']:
                return subprocess.CompletedProcess(argv, 1, '', 'private error')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(fail).cycle()['status'], 'auth')
        self.assertFalse(any(argv[:2] == ['codex', 'exec'] for argv in self.calls))

    def test_private_workspace_is_blocked(self):
        (self.workspace / '.env').write_text('private fixture')
        self.assertEqual(self.runner().cycle()['status'], 'private_workspace')

    def test_daily_cap_does_not_call_model(self):
        runner = self.runner()
        mod.atomic(self.state / 'checkpoint.json', {'completed': [], 'calls_today': 12,
            'day': __import__('time').strftime('%Y-%m-%d', __import__('time').gmtime(100000))})
        self.assertEqual(runner.cycle()['status'], 'daily_limit')
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
