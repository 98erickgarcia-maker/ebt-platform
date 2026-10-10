import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('scope_runner_fixtures', Path(__file__).with_name('test_engineering_runner.py'))
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class TaskScopeTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    fake = fixtures.RunnerTests.fake
    runner = fixtures.RunnerTests.runner

    def configure(self, paths=None, maximum=None, dependencies=None):
        self.policy['allowed_paths'] = ['proof.md', 'previous.md']
        self.policy['tasks'][0].update(write_paths=paths or ['proof.md'],
            max_changed_files=1 if maximum is None else maximum,
            depends_on=[] if dependencies is None else dependencies)
        self.manifest.write_text(json.dumps(self.policy), encoding='utf-8')

    def assert_not_completed(self):
        self.assertEqual(json.loads((self.state / 'checkpoint.json').read_text())['completed'], [])

    def test_missing_dependency_stops_before_model_or_auth(self):
        self.configure(dependencies=['T2'])
        self.assertEqual(self.runner().cycle()['status'], 'dependency_missing')
        self.assertEqual(self.calls, [])
        self.assert_not_completed()

    def test_unknown_dependency_policy_rejected_before_model(self):
        self.configure(dependencies=['missing-task'])
        self.assertEqual(self.runner().cycle()['status'], 'invalid_task_policy')
        self.assertEqual(self.calls, [])

    def test_globally_allowed_but_outside_task_change_is_denied(self):
        self.configure()
        def outside(argv, **kwargs):
            result = self.fake(argv, **kwargs)
            if argv[:2] == ['codex', 'exec']:
                (self.workspace / 'previous.md').write_text('out of assigned scope')
            return result
        self.assertEqual(self.runner(outside).cycle()['status'], 'task_scope_violation')
        self.assert_not_completed()
        self.assertFalse((self.state / 'T1.json').exists())

    def test_max_changed_files_denies_two_assigned_files(self):
        self.configure(paths=['proof.md', 'previous.md'], maximum=1)
        def too_many(argv, **kwargs):
            result = self.fake(argv, **kwargs)
            if argv[:2] == ['codex', 'exec']:
                (self.workspace / 'previous.md').write_text('second assigned file')
            return result
        self.assertEqual(self.runner(too_many).cycle()['status'], 'task_file_limit')
        self.assert_not_completed()

    def test_preexisting_dirty_file_is_not_this_invocation_delta(self):
        self.configure()
        (self.workspace / 'previous.md').write_text('previous task content')
        def previous_dirty(argv, **kwargs):
            if argv[:3] == ['git', 'ls-files', '--others']:
                files = [p for p in self.policy['allowed_paths'] if (self.workspace / p).exists()]
                return fixtures.subprocess.CompletedProcess(argv, 0, '\n'.join(files), '')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(previous_dirty).cycle()['status'], 'task_verified')
        record = json.loads((self.state / 'T1.json').read_text())
        self.assertEqual(record['changed_paths'], ['proof.md'])
        self.assertEqual(record['before_hashes'], {'proof.md': None})
        self.assertTrue(record['after_hashes']['proof.md'])
        self.assertFalse((self.state / 'artifacts/T1/previous.md').exists())

    def test_deletion_outside_task_counts_as_change(self):
        self.configure()
        (self.workspace / 'previous.md').write_text('preserve prior file')
        def deleted(argv, **kwargs):
            result = self.fake(argv, **kwargs)
            if argv[:2] == ['codex', 'exec']:
                (self.workspace / 'previous.md').unlink()
            return result
        self.assertEqual(self.runner(deleted).cycle()['status'], 'task_scope_violation')
        self.assert_not_completed()

    def test_model_error_does_not_hide_scope_violation(self):
        self.configure()
        def failed_with_change(argv, **kwargs):
            if argv[:2] == ['codex', 'exec']:
                (self.workspace / 'previous.md').write_text('unauthorized on quota failure')
                return fixtures.subprocess.CompletedProcess(argv, 1, '', '429')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(failed_with_change).cycle()['status'], 'task_scope_violation')
        self.assert_not_completed()

    def test_checks_cannot_modify_another_tasks_files(self):
        self.configure()
        def check_change(argv, **kwargs):
            result = self.fake(argv, **kwargs)
            if argv == ['git', 'diff', '--check']:
                (self.workspace / 'previous.md').write_text('unexpected check output')
            return result
        self.assertEqual(self.runner(check_change).cycle()['status'], 'task_scope_violation')
        self.assert_not_completed()


if __name__ == '__main__':
    unittest.main()
