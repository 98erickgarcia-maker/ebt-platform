import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('continue_chat', Path(__file__).resolve().parents[2] / 'scripts/ops/continue_chat.py')
routine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routine)

class ContinueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / 'state.json'
        self.config = {'version': 1, 'authorized': True, 'text': 'CONTINUE',
                       'interval_seconds': 900, 'url': 'https://chatgpt.com/c/00000000-0000-4000-8000-000000000001'}
        self.calls = []
        self.ready = {'status': 'inspected', 'composer': True, 'busy': False,
                      'draft_present': False, 'extra_high': True, 'workspace_limit_notice': False}
    def execute(self, payload):
        self.calls.append(payload)
        return self.ready if payload['action'] == 'inspect' else {'status': 'submission_observed'}
    def tick(self, now=1000, dry=False):
        return routine.tick(self.config, self.state, self.execute, now=now, dry_run=dry)
    def test_explicit_fixed_scope(self):
        for key, value in [('authorized', False), ('text', 'Outro texto'), ('interval_seconds', 30), ('url', 'https://example.org')]:
            config = dict(self.config, **{key: value})
            with self.assertRaises(ValueError): routine.validate(config)
        self.assertEqual(self.calls, [])
    def test_dry_check_never_sends_or_creates_state(self):
        self.assertEqual(self.tick(dry=True)['status'], 'ready_dry_run')
        self.assertEqual([p['action'] for p in self.calls], ['inspect'])
        self.assertFalse(self.state.exists())
    def test_send_and_spacing_are_persistent(self):
        self.assertEqual(self.tick()['status'], 'submission_observed')
        self.assertEqual(self.calls[-1], {'action': 'send', 'url': self.config['url'], 'text': 'CONTINUE'})
        self.assertEqual(self.tick(now=1100)['status'], 'waiting_interval')
        self.assertEqual(sum(p['action']=='send' for p in self.calls), 1)
        self.assertEqual(self.tick(now=1900)['status'], 'submission_observed')
    def test_busy_is_skipped_without_queue_or_send(self):
        self.ready['busy'] = True
        self.assertEqual(self.tick()['status'], 'skipped_busy')
        self.assertEqual([p['action'] for p in self.calls], ['inspect'])
    def test_quota_draft_and_auth_block_until_manual_action(self):
        for field in ['workspace_limit_notice', 'draft_present', 'composer', 'extra_high']:
            with self.subTest(field=field):
                self.state.unlink(missing_ok=True)
                self.ready.update(composer=True, extra_high=True, workspace_limit_notice=False, draft_present=False)
                self.ready[field] = field in ['workspace_limit_notice', 'draft_present']
                self.assertEqual(self.tick()['status'], 'paused')
                self.ready.update(composer=True, extra_high=True, workspace_limit_notice=False, draft_present=False)
                self.assertEqual(self.tick(now=2000)['status'], 'paused')
        self.assertFalse(any(p['action']=='send' for p in self.calls))
    def test_uncertain_submission_never_retries(self):
        def failing(payload):
            self.calls.append(payload)
            return self.ready if payload['action']=='inspect' else {'error':'submission_unconfirmed_no_retry'}
        result = routine.tick(self.config, self.state, failing, now=1000)
        self.assertEqual(result['status'], 'paused')
        self.assertEqual(self.tick(now=2000)['status'], 'paused')
        self.assertEqual(sum(p['action']=='send' for p in self.calls), 1)
    def test_crashed_inflight_attempt_requires_manual_review(self):
        self.state.write_text(json.dumps({'status':'sending', 'last_attempt':1000}))
        self.assertEqual(self.tick(now=3000)['status'], 'paused')
        self.assertEqual(self.calls, [])
    def test_changing_valid_destination_requires_new_review(self):
        self.tick()
        self.calls.clear()
        self.config['url'] = 'https://chatgpt.com/c/00000000-0000-4000-8000-000000000002'
        self.assertEqual(self.tick(now=3000)['reason'], 'scope_changed_requires_review')
        self.assertEqual(self.calls, [])

if __name__ == '__main__': unittest.main()
