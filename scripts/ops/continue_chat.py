"""Explicitly authorized, fixed CONTINUE on one chat. No model API calls or queue writes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

URL = re.compile(r'https://chatgpt\.com/c/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')

def validate(config):
    if (set(config) != {'version', 'authorized', 'text', 'interval_seconds', 'url'}
        or config['version'] != 1 or config['authorized'] is not True
        or config['text'] != 'CONTINUE' or config['interval_seconds'] != 900
        or not isinstance(config['url'], str) or not URL.fullmatch(config['url'])):
        raise ValueError('explicit_fixed_scope_required')
    return config

def save(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.new')
    temporary.write_text(json.dumps(state, ensure_ascii=True) + '\n', encoding='utf-8')
    temporary.replace(path)

def tick(config, path, execute, now=None, dry_run=False):
    validate(config)
    now = time.time() if now is None else now
    path = Path(path)
    state = json.loads(path.read_text()) if path.exists() else {}
    fingerprint = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    def paused(reason):
        result = dict(state, status='paused', reason=reason, checked_at=now)
        if not dry_run: save(path, result)
        return result
    if state.get('status') == 'paused': return state
    if state.get('status') == 'sending': return paused('previous_attempt_uncertain_no_retry')
    if state.get('config_sha256', fingerprint) != fingerprint: return paused('scope_changed_requires_review')
    if now - state.get('last_attempt', -900) < 900:
        return dict(state, status='waiting_interval')
    try:
        ready = execute({'action': 'inspect', 'url': config['url']})
    except Exception:
        return paused('browser_unavailable')
    if ready.get('status') != 'inspected': return paused('browser_unavailable')
    if ready.get('workspace_limit_notice'): return paused('workspace_limit_notice')
    if ready.get('busy'):
        result = dict(state, status='skipped_busy', checked_at=now, config_sha256=fingerprint)
        if not dry_run: save(path, result)
        return result
    if ready.get('draft_present'): return paused('draft_present')
    if not ready.get('extra_high'): return paused('select_extra_high')
    if not ready.get('composer'): return paused('composer_or_session_missing')
    if dry_run: return {'status': 'ready_dry_run', 'model_calls': False}
    # Persist before side effects: a crash cannot trigger automatic retransmission.
    state = dict(state, status='sending', last_attempt=now, checked_at=now, config_sha256=fingerprint)
    save(path, state)
    try:
        result = execute({'action': 'send', 'url': config['url'], 'text': 'CONTINUE'})
    except Exception:
        return paused('submission_uncertain_no_retry')
    if result.get('status') != 'submission_observed':
        return paused('submission_uncertain_no_retry')
    state.update(status='submission_observed', last_observed=now, reason=None,
                 observed_count=state.get('observed_count', 0) + 1, task_completed=False)
    save(path, state)
    return state

def browser(payload):
    result = subprocess.run(['docker', 'exec', '-i', 'ebt-linux-chat', '/opt/ebt-node', '/opt/ebt-insert-chat.mjs'],
                            input=json.dumps(payload), text=True, capture_output=True, timeout=35)
    if len(result.stdout) > 16000: raise ValueError('browser_unavailable')
    return json.loads(result.stdout)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='/etc/ebt-continue-chat.json')
    parser.add_argument('--state', default='/var/lib/ebt-chat-continue/state.json')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Only after manually reviewing the chat; never sends now.')
    args = parser.parse_args()
    # Local Linux lock serializes timer/CLI execution, independent of browser send lock.
    import fcntl
    path = Path(args.state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({'status':'skipped_locked'})); return
        config = validate(json.loads(Path(args.config).read_text()))
        if args.resume:
            state = json.loads(path.read_text()) if path.exists() else {}
            state.update(status='idle', reason=None,
                         config_sha256=hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest())
            save(path, state)
            print(json.dumps({'status':'resumed_without_send'})); return
        result = tick(config, path, browser, dry_run=args.dry_run)
        print(json.dumps({k: result[k] for k in ['status', 'reason', 'checked_at', 'last_observed', 'observed_count'] if k in result}))

if __name__ == '__main__': main()
