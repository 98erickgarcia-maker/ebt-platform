import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

spec = importlib.util.spec_from_file_location('models_fixtures', Path(__file__).with_name('test_engineering_runner.py'))
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class ModelRoutingTests(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    fake = fixtures.RunnerTests.fake
    runner = fixtures.RunnerTests.runner

    def configure(self):
        (self.state / 'checkpoint.json').unlink(missing_ok=True)
        self.policy['tasks'][0]['role'] = 'backend'
        self.policy['model_routing'] = dict(provider='openai', allow_paid_api=False,
            quota_fallback='wait', approved_models=['gpt-5.6-sol'],
            roles={'backend': dict(model='gpt-5.6-sol', reasoning_effort='high')})
        self.persist()

    def persist(self):
        self.manifest.write_text(json.dumps(self.policy), encoding='utf-8')

    def test_selected_model_is_in_command_checkpoint_and_evidence(self):
        self.configure()
        self.assertEqual(self.runner().cycle()['status'], 'task_verified')
        argv = next(a for a in self.calls if a[:2] == ['codex', 'exec'])
        self.assertEqual(argv[argv.index('--model') + 1], 'gpt-5.6-sol')
        self.assertIn('model_reasoning_effort="high"', argv)
        for name in ('checkpoint.json', 'T1.json'):
            self.assertEqual(json.loads((self.state / name).read_text())['selected_model']['model'], 'gpt-5.6-sol')

    def test_unapproved_or_injected_model_rejected_before_call(self):
        for name in ('other-model', 'gpt-5.6-sol;echo secret'):
            self.configure()
            self.policy['model_routing']['roles']['backend']['model'] = name
            self.persist()
            self.calls.clear()
            self.assertEqual(self.runner().cycle()['status'], 'invalid_model_policy')
            self.assertFalse(any(a[0] == 'codex' for a in self.calls))

    def test_paid_api_or_alternative_provider_is_rejected(self):
        for key, value in (('allow_paid_api', True), ('provider', 'external'), ('quota_fallback', 'switch')):
            self.configure()
            self.policy['model_routing'][key] = value
            self.persist()
            self.calls.clear()
            self.assertEqual(self.runner().cycle()['status'], 'invalid_model_policy')
            self.assertFalse(any(a[0] == 'codex' for a in self.calls))

    def test_quota_makes_one_call_then_waits_without_switch(self):
        self.configure()
        def limited(argv, **kwargs):
            if argv[:2] == ['codex', 'exec']:
                self.calls.append(argv)
                return subprocess.CompletedProcess(argv, 1, '', 'usage limit')
            return self.fake(argv, **kwargs)
        self.assertEqual(self.runner(limited).cycle()['status'], 'quota')
        self.assertEqual(self.runner(limited).cycle()['status'], 'cooldown')
        self.assertEqual(sum(a[:2] == ['codex', 'exec'] for a in self.calls), 1)


if __name__ == '__main__':
    unittest.main()
