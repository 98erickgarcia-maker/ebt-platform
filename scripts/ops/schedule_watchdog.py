"""Independent read-only GitHub monitor. No remote mutations or notifications."""
import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.request

REPO = '98erickgarcia-maker/ebt-platform'
PREFIX = f'https://api.github.com/repos/{REPO}/'
BRASILIA = timezone(timedelta(hours=-3))
MAX_SCHEDULE_AGE = timedelta(minutes=45)
MAX_SCHEDULE_GAP = timedelta(minutes=45)
RECENT_FAILURE_WINDOW = timedelta(minutes=90)

def evaluate(runs, issues, now):
    schedules = [r for r in runs if r['event'] == 'schedule' and r['head_branch'] == 'main']
    def timestamp(row):
        stamp = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
        if stamp.tzinfo is None or stamp > now: raise ValueError('invalid timestamp')
        return stamp
    schedules.sort(key=timestamp, reverse=True)
    latest = schedules[0] if schedules else None
    previous = schedules[1] if len(schedules) > 1 else None
    alerts = []
    if latest is None:
        alerts.append('schedule_missing')
    else:
        if now - timestamp(latest) > MAX_SCHEDULE_AGE: alerts.append('schedule_stale')
        if latest['status'] != 'completed': alerts.append('schedule_incomplete')
        elif latest['conclusion'] != 'success': alerts.append('schedule_' + str(latest['conclusion']))
        if previous is None:
            alerts.append('schedule_history_insufficient')
        elif timestamp(latest) - timestamp(previous) > MAX_SCHEDULE_GAP:
            alerts.append('schedule_gap')
    for row in runs:
        if row.get('head_branch') != 'main' or row.get('conclusion') not in ('failure', 'cancelled', 'timed_out'):
            continue
        try:
            observed = timestamp(row)
        except (ValueError, KeyError, TypeError, AttributeError):
            alerts.append('run_timestamp_invalid')
            continue
        if now - observed <= RECENT_FAILURE_WINDOW:
            alerts.append(f"run_{row['id']}_{row['conclusion']}")
    incidents = sorted(i['number'] for i in issues if i['state'] == 'open' and i['title'].startswith('[EBT OPS]') and 'pull_request' not in i)
    return dict(status='FAIL' if alerts else 'PASS', utc=now.isoformat(), brasilia=now.astimezone(BRASILIA).isoformat(),
                alerts=sorted(set(alerts)), incidents=incidents, latest_schedule=None if latest is None else
                {**{k: latest[k] for k in ('id', 'created_at', 'head_sha', 'html_url', 'status', 'conclusion')},
                 'previous_created_at': None if previous is None else previous['created_at'],
                 'gap_seconds': None if previous is None else int((timestamp(latest) - timestamp(previous)).total_seconds())})

def collect(get, now):
    try:
        runs, issues = [], []
        # Bounded pagination; absence never becomes success when history is exhausted.
        for page in range(1, 11):
            batch = get(PREFIX + f'actions/workflows/ebt-production-watch.yml/runs?per_page=100&page={page}')['workflow_runs']
            if not isinstance(batch, list): raise ValueError('invalid runs')
            runs.extend(batch)
            schedule_count = sum(1 for r in runs if r.get('event') == 'schedule' and r.get('head_branch') == 'main')
            if schedule_count >= 2 or len(batch) < 100: break
        for page in range(1, 11):
            batch = get(PREFIX + f'issues?state=open&per_page=100&page={page}')
            if not isinstance(batch, list): raise ValueError('invalid issues')
            issues.extend(batch)
            if len(batch) < 100: break
        else: raise ValueError('issue pagination exhausted')
        return evaluate(runs, issues, now)
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return dict(status='CONNECTION_ERROR', utc=now.isoformat(), brasilia=now.astimezone(BRASILIA).isoformat())
    except (ValueError, KeyError, TypeError, AttributeError):
        return dict(status='MONITOR_ERROR', utc=now.isoformat(), brasilia=now.astimezone(BRASILIA).isoformat())

def persist(path, report):
    path = Path(path)
    state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if not isinstance(state, dict) or not isinstance(state.get('seen_incidents', []), list): raise ValueError('invalid state')
    seen = set(state.get('seen_incidents', []))
    result = dict(report, changed=state.get('signature') != [report['status'], report.get('alerts', []), report.get('incidents', [])],
                  new_incidents=sorted(set(report.get('incidents', [])) - seen))
    seen.update(report.get('incidents', []))
    state.update(seen_incidents=sorted(seen), signature=[report['status'], report.get('alerts', []), report.get('incidents', [])], last_observation=report)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace atomically; a failed collection preserves the last known successful observation.
    if report['status'] in ('PASS', 'FAIL'): state['last_valid_observation'] = report
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as file:
            temporary = file.name
            json.dump(state, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary): os.unlink(temporary)
    return result

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs): return None

def github_get(url):
    if not url.startswith(PREFIX): raise ValueError('unexpected API URL')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'EBT-schedule-watchdog'}
    token = os.environ.get('GH_TOKEN')
    if token: headers['Authorization'] = 'Bearer ' + token
    with urllib.request.build_opener(NoRedirect).open(urllib.request.Request(url, headers=headers), timeout=20) as response:
        return json.load(response)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True)
    args = parser.parse_args()
    report = collect(github_get, datetime.now(timezone.utc))
    try: report = persist(args.state, report)
    except (OSError, ValueError, TypeError):
        report = dict(status='MONITOR_ERROR', utc=report['utc'], brasilia=report['brasilia'], code='state_persistence_failed')
    print(json.dumps(report, ensure_ascii=True))
    return 0 if report['status'] == 'PASS' else 2 if report['status'] == 'FAIL' else 3

if __name__ == '__main__': raise SystemExit(main())
