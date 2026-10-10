from datetime import datetime, timezone, timedelta
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('engineering_watch', Path(__file__).resolve().parents[2] / 'scripts/ops/engineering_watch.py')
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)
NOW = datetime(2026, 10, 9, 20, tzinfo=timezone.utc)


def heartbeat(**updates):
    value = dict(schema_version=1, run_id='run-001', module_id='PAC-07', status='running',
                 updated_at=NOW.isoformat(), progress_at=NOW.isoformat(), pid=42,
                 blocked_reason=None, source_commit='a' * 40)
    value.update(updates)
    return value


class EngineeringWatchTests(unittest.TestCase):
    def test_current_process_probe_read_only(self):
        self.assertTrue(watch.process_alive(os.getpid()))

    def test_progress(self):
        report = watch.evaluate(heartbeat(), NOW, pid_probe=lambda pid: True)
        self.assertEqual(report['state'], 'progressing')

    def test_starting_alive(self):
        report = watch.evaluate(heartbeat(status='starting', progress_at=None), NOW, pid_probe=lambda pid: True)
        self.assertEqual(report['state'], 'alive')

    def test_live_process_without_progress_is_stalled(self):
        report = watch.evaluate(heartbeat(progress_at=(NOW - timedelta(minutes=31)).isoformat()), NOW, pid_probe=lambda pid: True)
        self.assertEqual((report['state'], report['code']), ('stalled', 'progress_stale'))
        self.assertTrue(report['process_alive'])

    def test_dead_process(self):
        self.assertEqual(watch.evaluate(heartbeat(), NOW, pid_probe=lambda pid: False)['code'], 'process_missing')

    def test_expired_lease(self):
        old = (NOW - timedelta(minutes=31)).isoformat()
        self.assertEqual(watch.evaluate(heartbeat(updated_at=old, progress_at=old), NOW, pid_probe=lambda pid: True)['code'], 'lease_expired')

    def test_future_and_naive_timestamps_rejected(self):
        for date in ((NOW + timedelta(seconds=1)).isoformat(), '2026-10-09T20:00:00'):
            with self.assertRaises(ValueError):
                watch.evaluate(heartbeat(updated_at=date), NOW)

    def test_progress_after_heartbeat_rejected(self):
        with self.assertRaises(ValueError):
            watch.evaluate(heartbeat(updated_at=(NOW - timedelta(seconds=1)).isoformat()), NOW)

    def test_blocked_and_succeeded_do_not_probe_pid(self):
        def forbidden(pid):
            raise AssertionError('terminal state must not probe')
        self.assertEqual(watch.evaluate(heartbeat(status='blocked', blocked_reason='quota', pid=None), NOW, pid_probe=forbidden)['state'], 'blocked')
        self.assertEqual(watch.evaluate(heartbeat(status='succeeded', pid=None), NOW, pid_probe=forbidden)['state'], 'succeeded')

    def test_schema_and_private_text_rejected(self):
        for changes in ({'schema_version': True}, {'pid': True}, {'source_commit': 'token-secret'},
                        {'run_id': 'secret with spaces'}, {'blocked_reason': 'password=secret'},
                        {'status': 'unknown'}, {'unexpected': 'private'}):
            with self.assertRaises((ValueError, TypeError)):
                watch.evaluate(heartbeat(**changes), NOW)

    def test_missing_heartbeat_preserves_last_valid_and_sanitizes(self):
        with tempfile.TemporaryDirectory() as temp:
            source, state = Path(temp) / 'heartbeat.json', Path(temp) / 'state.json'
            source.write_text(json.dumps(heartbeat()), encoding='utf-8')
            first = watch.observe(source, state, NOW, pid_probe=lambda pid: True)
            self.assertTrue(first['changed'])
            again = watch.observe(source, state, NOW, pid_probe=lambda pid: True)
            self.assertFalse(again['changed'])
            source.write_text('{private-password', encoding='utf-8')
            result = watch.observe(source, state, NOW)
            self.assertEqual(result['state'], 'monitor_error')
            self.assertNotIn('private-password', json.dumps(result))
            checkpoint = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(checkpoint['last_valid_observation']['state'], 'progressing')
            source.unlink()
            self.assertEqual(watch.observe(source, state, NOW)['state'], 'monitor_error')

    def test_corrupt_checkpoint_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            source, state = Path(temp) / 'heartbeat.json', Path(temp) / 'state.json'
            source.write_text(json.dumps(heartbeat()), encoding='utf-8')
            state.write_text('{corrupt', encoding='utf-8')
            self.assertEqual(watch.observe(source, state, NOW, pid_probe=lambda pid: True)['code'], 'checkpoint_unavailable_or_invalid')
            self.assertEqual(state.read_text(encoding='utf-8'), '{corrupt')

    def test_same_path_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'heartbeat.json'
            original = json.dumps(heartbeat())
            path.write_text(original, encoding='utf-8')
            self.assertEqual(watch.observe(path, path, NOW)['state'], 'monitor_error')
            self.assertEqual(path.read_text(encoding='utf-8'), original)


if __name__ == '__main__':
    unittest.main()
