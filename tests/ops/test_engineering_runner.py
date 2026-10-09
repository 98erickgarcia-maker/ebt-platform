import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

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
            (self.state / 'result.json').write_text(json.dumps(
                {'status': 'completed', 'summary': 'reviewed', 'evidence_paths': ['proof.md']}))
        return subprocess.CompletedProcess(argv, 0, out, '')

    def runner(self, fake=None):
        return mod.Runner(self.workspace, self.state, self.manifest, fake or self.fake, now=lambda: 100000)

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
                (self.state / 'result.json').write_text(json.dumps(
                    {'status': 'completed', 'summary': 'done', 'evidence_paths': []}))
                return subprocess.CompletedProcess(argv, 0, '', '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(empty).cycle()['status'], 'no_progress_evidence')

    def test_error_classification(self):
        self.assertEqual(mod.classify('401 Unauthorized'), 'auth')
        self.assertEqual(mod.classify('stream disconnected'), 'network')
        self.assertEqual(mod.classify('other private info'), 'model_failed')

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
