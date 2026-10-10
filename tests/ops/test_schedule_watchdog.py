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
    row = dict(id=1, event='schedule', head_branch='main', created_at='2026-10-09T18:22:00Z',
               head_sha='abc', html_url='https://github.com/example/run/1', status='completed', conclusion='success')
    row.update(changes)
    return row


def healthy_runs():
    return [
        run(),
        run(id=2, created_at='2026-10-09T18:07:00Z', html_url='https://github.com/example/run/2'),
    ]


class WatchdogTests(unittest.TestCase):
    def test_empty_is_failure(self):
        self.assertIn('schedule_missing', evaluate([], [], NOW)['alerts'])

    def test_manual_and_other_branch_never_recover(self):
        self.assertIn('schedule_missing', evaluate([run(event='workflow_dispatch'), run(head_branch='dev')], [], NOW)['alerts'])

    def test_single_schedule_is_not_enough_to_prove_cadence(self):
        self.assertIn('schedule_history_insufficient', evaluate([run()], [], NOW)['alerts'])

    def test_age_threshold_strictly_over_45_minutes(self):
        at_limit = [
            run(created_at='2026-10-09T17:45:00Z'),
            run(id=2, created_at='2026-10-09T17:30:00Z'),
        ]
        over_limit = [
            run(created_at='2026-10-09T17:44:59Z'),
            run(id=2, created_at='2026-10-09T17:29:59Z'),
        ]
        self.assertNotIn('schedule_stale', evaluate(at_limit, [], NOW)['alerts'])
        self.assertIn('schedule_stale', evaluate(over_limit, [], NOW)['alerts'])

    def test_gap_threshold_strictly_over_45_minutes(self):
        at_limit = [
            run(created_at='2026-10-09T18:22:00Z'),
            run(id=2, created_at='2026-10-09T17:37:00Z'),
        ]
        over_limit = [
            run(created_at='2026-10-09T18:22:00Z'),
            run(id=2, created_at='2026-10-09T17:36:59Z'),
        ]
        self.assertNotIn('schedule_gap', evaluate(at_limit, [], NOW)['alerts'])
        report = evaluate(over_limit, [], NOW)
        self.assertIn('schedule_gap', report['alerts'])
        self.assertEqual(report['latest_schedule']['gap_seconds'], 2701)

    def test_observed_multi_hour_gap_remains_failure_even_after_recent_schedule(self):
        report = evaluate([
            run(created_at='2026-10-09T18:19:25Z'),
            run(id=2, created_at='2026-10-09T14:37:42Z'),
        ], [], NOW)
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('schedule_gap', report['alerts'])

    def test_failed_and_cancelled_latest_schedule(self):
        for conclusion in ['failure', 'cancelled', 'timed_out', 'skipped']:
            rows = healthy_runs()
            rows[0] = run(conclusion=conclusion)
            self.assertIn('schedule_' + conclusion, evaluate(rows, [], NOW)['alerts'])

    def test_queued_is_not_success(self):
        rows = healthy_runs()
        rows[0] = run(status='queued', conclusion=None)
        self.assertIn('schedule_incomplete', evaluate(rows, [], NOW)['alerts'])

    def test_recent_failure_is_visible_but_old_failure_expires(self):
        recent = run(id=3, event='push', created_at='2026-10-09T17:45:00Z', conclusion='failure')
        old = run(id=4, event='push', created_at='2026-10-09T16:00:00Z', conclusion='failure')
        alerts = evaluate(healthy_runs() + [recent, old], [], NOW)['alerts']
        self.assertIn('run_3_failure', alerts)
        self.assertNotIn('run_4_failure', alerts)

    def test_incidents_and_persistent_dedup(self):
        issues = [dict(number=19, title='[EBT OPS] missing', state='open'), dict(number=20, title='ordinary', state='open')]
        report = evaluate(healthy_runs(), issues, NOW)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            first = persist(target, report)
            self.assertEqual(first['new_incidents'], [19])
            self.assertEqual(persist(target, report)['new_incidents'], [])
            self.assertEqual(json.loads(target.read_text())['seen_incidents'], [19])

    def test_network_failure_is_distinct(self):
        def get(_):
            raise ConnectionError('secret must not be logged')
        self.assertEqual(collect(get, NOW)['status'], 'CONNECTION_ERROR')

    def test_malformed_is_monitor_error(self):
        self.assertEqual(collect(lambda _: {}, NOW)['status'], 'MONITOR_ERROR')

    def test_null_timestamp_is_monitor_error(self):
        self.assertEqual(
            collect(lambda p: [] if 'issues?' in p else dict(workflow_runs=[run(created_at=None)]), NOW)['status'],
            'MONITOR_ERROR',
        )

    def test_connection_failure_preserves_last_valid_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            persist(target, evaluate(healthy_runs(), [], NOW))
            persist(target, dict(status='CONNECTION_ERROR', utc=NOW.isoformat()))
            state = json.loads(target.read_text())
            self.assertEqual(state['last_valid_observation']['status'], 'PASS')
            self.assertEqual(state['last_observation']['status'], 'CONNECTION_ERROR')

    def test_pagination_reaches_second_schedule_on_later_page(self):
        def get(url):
            if 'issues?' in url:
                return []
            if 'page=2' in url:
                return dict(workflow_runs=[run(id=2, created_at='2026-10-09T18:07:00Z')])
            batch = [run()] + [run(event='push', id=x + 10) for x in range(99)]
            return dict(workflow_runs=batch)
        report = collect(get, NOW)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['latest_schedule']['gap_seconds'], 900)

    def test_future_timestamp_is_invalid(self):
        rows = healthy_runs()
        rows[0] = run(created_at='2027-01-01T00:00:00Z')
        self.assertEqual(
            collect(lambda p: [] if 'issues?' in p else dict(workflow_runs=rows), NOW)['status'],
            'MONITOR_ERROR',
        )

    def test_invalid_failure_timestamp_is_alert_not_crash(self):
        rows = healthy_runs() + [run(id=9, event='push', created_at=None, conclusion='failure')]
        report = evaluate(rows, [], NOW)
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('run_timestamp_invalid', report['alerts'])

    def test_corrupt_state_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            target.write_text('broken')
            with self.assertRaises(ValueError):
                persist(target, evaluate(healthy_runs(), [], NOW))
            self.assertEqual(target.read_text(), 'broken')


if __name__ == '__main__':
    unittest.main()
