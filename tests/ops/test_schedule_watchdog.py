import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts' / 'ops'))
from schedule_watchdog import evaluate, collect, persist
import tempfile
import json

NOW = datetime(2026, 10, 9, 18, 30, tzinfo=timezone.utc)

def run(**changes):
    row = dict(id=1, event='schedule', head_branch='main', created_at='2026-10-09T17:30:00Z',
               head_sha='abc', html_url='https://github.com/example/run/1', status='completed', conclusion='success')
    row.update(changes)
    return row

class WatchdogTests(unittest.TestCase):
    def test_empty_is_failure(self):
        self.assertIn('schedule_missing', evaluate([], [], NOW)['alerts'])

    def test_manual_and_other_branch_never_recover(self):
        self.assertIn('schedule_missing', evaluate([run(event='workflow_dispatch'), run(head_branch='dev')], [], NOW)['alerts'])

    def test_threshold_strictly_over_90(self):
        self.assertNotIn('schedule_stale', evaluate([run(created_at='2026-10-09T17:00:00Z')], [], NOW)['alerts'])
        self.assertIn('schedule_stale', evaluate([run(created_at='2026-10-09T16:59:59Z')], [], NOW)['alerts'])

    def test_failed_and_cancelled(self):
        for conclusion in ['failure', 'cancelled', 'timed_out', 'skipped']:
            self.assertIn('schedule_' + conclusion, evaluate([run(conclusion=conclusion)], [], NOW)['alerts'])

    def test_queued_is_not_success(self):
        self.assertIn('schedule_incomplete', evaluate([run(status='queued', conclusion=None)], [], NOW)['alerts'])

    def test_previous_failure_remains_visible(self):
        self.assertIn('run_2_failure', evaluate([run(), run(id=2, event='push', conclusion='failure')], [], NOW)['alerts'])

    def test_incidents_and_persistent_dedup(self):
        issues = [dict(number=19, title='[EBT OPS] missing', state='open'), dict(number=20, title='ordinary', state='open')]
        report = evaluate([run()], issues, NOW)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            first = persist(target, report)
            self.assertEqual(first['new_incidents'], [19])
            self.assertEqual(persist(target, report)['new_incidents'], [])
            self.assertEqual(json.loads(target.read_text())['seen_incidents'], [19])

    def test_network_failure_is_distinct(self):
        def get(_): raise ConnectionError('secret must not be logged')
        self.assertEqual(collect(get, NOW)['status'], 'CONNECTION_ERROR')

    def test_malformed_is_monitor_error(self):
        self.assertEqual(collect(lambda _: {}, NOW)['status'], 'MONITOR_ERROR')

    def test_null_timestamp_is_monitor_error(self):
        self.assertEqual(collect(lambda p: [] if 'issues?' in p else dict(workflow_runs=[run(created_at=None)]), NOW)['status'], 'MONITOR_ERROR')

    def test_connection_failure_preserves_last_valid_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            persist(target, evaluate([run()], [], NOW))
            persist(target, dict(status='CONNECTION_ERROR', utc=NOW.isoformat()))
            state = json.loads(target.read_text())
            self.assertEqual(state['last_valid_observation']['status'], 'PASS')
            self.assertEqual(state['last_observation']['status'], 'CONNECTION_ERROR')

    def test_pagination_reaches_older_schedule(self):
        def get(url):
            if 'issues?' in url: return []
            if 'page=2' in url: return dict(workflow_runs=[run()])
            return dict(workflow_runs=[run(event='push', id=x) for x in range(100)])
        self.assertEqual(collect(get, NOW)['status'], 'PASS')

    def test_future_timestamp_is_invalid(self):
        self.assertEqual(collect(lambda p: [] if 'issues?' in p else dict(workflow_runs=[run(created_at='2027-01-01T00:00:00Z')]), NOW)['status'], 'MONITOR_ERROR')

    def test_corrupt_state_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            target.write_text('broken')
            with self.assertRaises(ValueError): persist(target, evaluate([run()], [], NOW))
            self.assertEqual(target.read_text(), 'broken')

if __name__ == '__main__': unittest.main()
