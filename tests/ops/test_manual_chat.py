import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('manual_chat', Path(__file__).resolve().parents[2] / 'scripts/ops/manual_chat.py')
manual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manual)


class ManualChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        directory = Path(self.tmp.name)
        self.manifest = directory / 'manifest.json'
        self.checkpoint = directory / 'checkpoint.json'
        self.manifest.write_text(json.dumps({'repository': '98erickgarcia-maker/ebt-platform',
            'branch': 'codex/flow-test', 'roles': ['scope'], 'tasks': [
                {'id': 'FLOW-01', 'role': 'scope', 'instruction': 'Documentar proposta sintética.'}]}))
        self.checkpoint.write_text(json.dumps({'current_task': 'FLOW-01', 'completed': [], 'status': 'quota'}))
        self.calls = []
        self.now = 100
        self.gate = manual.ManualGate(self.manifest, self.checkpoint,
            execute=lambda payload: self.calls.append(payload) or {'status': 'submission_observed'},
            clock=lambda: self.now)
        self.target = 'https://chatgpt.com/c/00000000-0000-4000-8000-000000000001'

    def preview(self):
        return self.gate.preview(self.target)

    def approve(self, preview, **overrides):
        request = {'approval_id': preview['approval_id'], 'sha256': preview['sha256'],
                   'approved': True, 'action': 'send'}
        request.update(overrides)
        return self.gate.approve(request)

    def test_preview_never_executes_or_advances_checkpoint(self):
        before = self.checkpoint.read_bytes()
        p = self.preview()
        self.assertIn('180h', p['text'])
        self.assertIn('20h', p['text'])
        self.assertIn('FLOW-01', p['text'])
        self.assertEqual(self.calls, [])
        self.assertEqual(before, self.checkpoint.read_bytes())

    def test_specific_approval_sends_only_frozen_preview_once(self):
        p = self.preview()
        self.assertEqual(self.approve(p)['status'], 'submission_observed')
        self.assertEqual(self.calls[0]['text'], p['text'])
        self.assertEqual(self.calls[0]['url'], self.target)
        self.assertEqual(self.calls[0]['action'], 'send')
        with self.assertRaises(ValueError):
            self.approve(p)
        self.assertEqual(len(self.calls), 1)

    def test_missing_approval_or_changed_hash_cannot_execute(self):
        for override in [{'approved': False}, {'approved': 'true'}, {'sha256': '0'*64},
                         {'action': 'deploy'}, {'text': 'replace reviewed text'}]:
            p = self.preview()
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.approve(p, **override)
        self.assertEqual(self.calls, [])

    def test_expired_or_changed_state_requires_new_approval(self):
        p = self.preview()
        self.now += 301
        with self.assertRaises(ValueError):
            self.approve(p)
        p = self.preview()
        self.checkpoint.write_text(json.dumps({'current_task': 'FLOW-02'}))
        with self.assertRaises(ValueError):
            self.approve(p)
        self.assertEqual(self.calls, [])

    def test_rejects_external_url_or_secret_before_preview(self):
        for url in ['https://example.invalid/', 'http://chatgpt.com/',
                    'https://chatgpt.com/?token=secret', 'https://chatgpt.com/']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.gate.preview(url)
        data = json.loads(self.manifest.read_text())
        data['tasks'][0]['instruction'] = 'sk-' + 'syntheticNOTREALsecret123456789'
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.preview()

    def test_cross_origin_host_or_content_type_is_rejected(self):
        manual.check_request('127.0.0.1:5810', 'http://127.0.0.1:5810', 'application/json')
        for args in [('evil.invalid:5810', 'http://evil.invalid:5810', 'application/json'),
                     ('127.0.0.1:5810', 'https://evil.invalid', 'application/json'),
                     ('127.0.0.1:5810', None, 'application/json'),
                     ('127.0.0.1:5810', 'http://127.0.0.1:5810', 'text/plain')]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                manual.check_request(*args)


if __name__ == '__main__':
    unittest.main()

