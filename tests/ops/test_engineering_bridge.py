import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2] / 'scripts/ops/engineering_bridge.py'
spec = importlib.util.spec_from_file_location('engineering_bridge', SOURCE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'checkpoint.json'
        self.path.write_text(json.dumps(dict(status='quota', current_task='FLOW-01',
            cooldown_until=200, completed=[], calls_today=1, secret='not exported')))
        self.commands = []
        self.app = bridge.Bridge(self.path, 'a'*48, run=self.commands.append, now=lambda:100)

    def test_invalid_auth_never_dispatches(self):
        status, _ = self.app.handle('POST', '/api/tick', 'wrong', b'{}')
        self.assertEqual(status, 401)
        self.assertEqual(self.commands, [])

    def test_quota_only_refreshes_observer(self):
        status, response = self.app.handle('POST', '/api/tick', 'a'*48, b'{}')
        self.assertEqual(status, 202)
        self.assertFalse(response['runnerQueued'])
        self.assertEqual(self.commands, [['systemctl','start','--no-block','ebt-engineering-watch.service']])
        self.assertNotIn('secret', json.dumps(response))

    def test_ready_queues_only_fixed_services(self):
        self.path.write_text(json.dumps(dict(status='task_verified', cooldown_until=0)))
        status, response = self.app.handle('POST', '/api/tick', 'a'*48, b'{}')
        self.assertEqual(status, 202)
        self.assertTrue(response['runnerQueued'])
        self.assertEqual(self.commands[-1][-1], 'ebt-engineering-runner.service')

    def test_arbitrary_command_body_rejected(self):
        status, _ = self.app.handle('POST', '/api/tick', 'a'*48, b'{"command":"rm"}')
        self.assertEqual(status, 400)
        self.assertEqual(self.commands, [])

    def test_missing_state_fails_closed(self):
        self.path.unlink()
        status, _ = self.app.handle('POST', '/api/tick', 'a'*48, b'{}')
        self.assertEqual(status, 503)
        self.assertEqual(self.commands, [])

    def test_repeated_tick_is_throttled(self):
        self.app.handle('POST', '/api/tick', 'a'*48, b'{}')
        self.assertEqual(self.app.handle('POST', '/api/tick', 'a'*48, b'{}')[0], 429)

    def test_status_read_only_and_private_fields_omitted(self):
        status, response = self.app.handle('GET','/api/status','a'*48,b'')
        self.assertEqual(status,200)
        self.assertEqual(self.commands,[])
        self.assertEqual(response['state'],'quota')
        self.assertNotIn('secret',response)

    def test_unknown_path_and_large_body_denied(self):
        self.assertEqual(self.app.handle('POST','/api/execute','a'*48,b'{}')[0],404)
        self.assertEqual(self.app.handle('POST','/api/tick','a'*48,b'x'*1025)[0],413)
        self.assertEqual(self.commands,[])
