from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import unittest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = Path(__file__).resolve().parents[2]
fixtures = load('runner_fixtures', BASE / 'tests/ops/test_engineering_runner.py')
watch = load('watch_integration', BASE / 'scripts/ops/engineering_watch.py')


class RunnerHeartbeatTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    fake = fixtures.RunnerTests.fake
    runner = fixtures.RunnerTests.runner
    def observed(self):
        value = json.loads((self.state / 'heartbeat.json').read_text(encoding='utf-8'))
        return watch.evaluate(value, datetime.fromtimestamp(100000, timezone.utc), pid_probe=lambda pid: True)

    def test_verified_task_generates_valid_terminal_heartbeat(self):
        self.assertEqual(self.runner().cycle()['status'], 'task_verified')
        report = self.observed()
        self.assertEqual(report['state'], 'succeeded')
        self.assertEqual(report['source_commit'], 'a' * 40)
        self.assertEqual(report['module_id'], 'T1')
        self.assertIsNotNone(report['progress_at'])

    def test_initial_running_has_no_fabricated_progress(self):
        runner = self.runner()
        runner.save(dict(status='running', current_task='T1', source_commit='a' * 40))
        self.assertEqual(self.observed()['state'], 'alive')
        self.assertIsNone(self.observed()['progress_at'])

    def test_cooldown_retains_quota_reason_without_progress(self):
        def quota(argv, **kwargs):
            if argv[:2] == ['codex', 'exec']:
                return fixtures.subprocess.CompletedProcess(argv, 1, '', '429')
            return self.fake(argv, **kwargs)
        runner = self.runner(quota)
        self.assertEqual(runner.cycle()['status'], 'quota')
        self.assertEqual(runner.cycle()['status'], 'cooldown')
        self.assertEqual((self.observed()['state'], self.observed()['code']), ('blocked', 'quota'))
        self.assertIsNone(self.observed()['progress_at'])

    def test_invalid_head_blocks_before_model(self):
        def unavailable(argv, **kwargs):
            if argv == ['git', 'rev-parse', 'HEAD']:
                return fixtures.subprocess.CompletedProcess(argv, 0, '', '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(unavailable).cycle()['status'], 'source_commit_unavailable')
        self.assertEqual(self.observed()['code'], 'configuration')
        self.assertFalse(any(argv[:2] == ['codex', 'exec'] for argv in self.calls))


if __name__ == '__main__':
    unittest.main()
