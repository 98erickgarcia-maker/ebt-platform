"""Read-only local engineering heartbeat monitor; never starts an agent."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile

FIELDS = {'schema_version', 'run_id', 'module_id', 'status', 'updated_at',
          'progress_at', 'pid', 'blocked_reason', 'source_commit'}
REASONS = {'quota', 'authentication', 'dependency', 'checks', 'conflict', 'manual', 'configuration'}
STATES = {'alive', 'progressing', 'stalled', 'blocked', 'succeeded', 'monitor_error'}


def timestamp(value, now):
    if not isinstance(value, str):
        raise ValueError('timestamp')
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp > now:
        raise ValueError('timestamp')
    return stamp


def process_alive(pid):
    if os.name == 'nt':
        import ctypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        kernel.GetExitCodeProcess.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
        kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            if ctypes.get_last_error() == 5:
                return True
            if ctypes.get_last_error() == 87:
                return False
            raise OSError('process_probe')
        try:
            code = ctypes.c_ulong()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                raise OSError('process_probe')
            return code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def evaluate(heartbeat, now, *, pid_probe=process_alive, lease_seconds=1800, progress_seconds=1800):
    if not isinstance(heartbeat, dict) or set(heartbeat) != FIELDS:
        raise ValueError('schema')
    if type(heartbeat['schema_version']) is not int or heartbeat['schema_version'] != 1:
        raise ValueError('version')
    for name in ('run_id', 'module_id'):
        if not isinstance(heartbeat[name], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', heartbeat[name]):
            raise ValueError('identifier')
    if not isinstance(heartbeat['source_commit'], str) or not re.fullmatch(r'[a-f0-9]{40}', heartbeat['source_commit']):
        raise ValueError('commit')
    status = heartbeat['status']
    if status not in ('starting', 'running', 'blocked', 'succeeded'):
        raise ValueError('status')
    reason = heartbeat['blocked_reason']
    if reason is not None and reason not in REASONS:
        raise ValueError('reason')
    if (status == 'blocked') != (reason is not None):
        raise ValueError('reason')
    pid = heartbeat['pid']
    if pid is not None and (type(pid) is not int or pid <= 1):
        raise ValueError('pid')
    if status in ('starting', 'running') and pid is None:
        raise ValueError('pid')
    updated = timestamp(heartbeat['updated_at'], now)
    progress = None if heartbeat['progress_at'] is None else timestamp(heartbeat['progress_at'], now)
    if progress is not None and progress > updated:
        raise ValueError('progress')
    if status == 'running' and progress is None:
        raise ValueError('progress')
    lease_valid = (now - updated).total_seconds() <= lease_seconds
    alive = pid_probe(pid) if pid is not None and status in ('starting', 'running') else None
    if status == 'succeeded':
        state, code = 'succeeded', 'terminal_checkpoint'
    elif status == 'blocked':
        state, code = 'blocked', reason
    elif not lease_valid:
        state, code = 'stalled', 'lease_expired'
    elif not alive:
        state, code = 'stalled', 'process_missing'
    elif progress is not None and (now - progress).total_seconds() > progress_seconds:
        state, code = 'stalled', 'progress_stale'
    else:
        state, code = ('alive', 'starting') if progress is None else ('progressing', 'progress_recent')
    return {'schema_version': 1, 'state': state, 'code': code,
            'observed_at': now.isoformat(), 'run_id': heartbeat['run_id'],
            'module_id': heartbeat['module_id'], 'source_commit': heartbeat['source_commit'],
            'process_alive': alive, 'lease_valid': lease_valid,
            'updated_at': updated.isoformat(), 'progress_at': None if progress is None else progress.isoformat()}


def read_json(path):
    path = Path(path)
    if path.is_symlink() or path.stat().st_size > 16384:
        raise ValueError('file')
    return json.loads(path.read_text(encoding='utf-8'))


def signature(report):
    return [report.get(key) for key in ('state', 'code', 'run_id', 'module_id', 'source_commit')]


def persist(path, report):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('checkpoint')
    previous = read_json(path) if path.exists() else {}
    if not isinstance(previous, dict) or (previous and set(previous) != {'schema_version', 'signature', 'last_observation', 'last_valid_observation'}):
        raise ValueError('checkpoint')
    last_valid = previous.get('last_valid_observation')
    if last_valid is not None:
        allowed = {'schema_version', 'state', 'code', 'observed_at', 'run_id', 'module_id', 'source_commit', 'process_alive', 'lease_valid', 'updated_at', 'progress_at'}
        if not isinstance(last_valid, dict) or set(last_valid) != allowed or last_valid.get('state') not in STATES - {'monitor_error'}:
            raise ValueError('checkpoint')
        # Never echo a previous arbitrary record; reconstruct through heartbeat validation.
        reconstructed = dict(schema_version=1, run_id=last_valid['run_id'], module_id=last_valid['module_id'],
            source_commit=last_valid['source_commit'], status='blocked' if last_valid['state'] == 'blocked' else 'succeeded',
            blocked_reason=last_valid['code'] if last_valid['state'] == 'blocked' else None,
            pid=None, updated_at=last_valid['updated_at'], progress_at=last_valid['progress_at'])
        evaluate(reconstructed, timestamp(report['observed_at'], datetime.max.replace(tzinfo=timezone.utc)))
        if last_valid['code'] not in REASONS | {'starting', 'progress_recent', 'progress_stale', 'lease_expired', 'process_missing', 'terminal_checkpoint'}:
            raise ValueError('checkpoint')
        if type(last_valid['lease_valid']) is not bool or (last_valid['process_alive'] is not None and type(last_valid['process_alive']) is not bool):
            raise ValueError('checkpoint')
        timestamp(last_valid['observed_at'], datetime.max.replace(tzinfo=timezone.utc))
    result = dict(report, changed=previous.get('signature') != signature(report))
    state = dict(schema_version=1, signature=signature(report), last_observation=report,
                 last_valid_observation=last_valid if report['state'] == 'monitor_error' else report)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as handle:
            temporary = handle.name
            os.chmod(temporary, 0o600)
            json.dump(state, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
    return result


def observe(heartbeat_path, state_path, now, **options):
    try:
        if Path(heartbeat_path).resolve() == Path(state_path).resolve():
            raise ValueError('paths')
        report = evaluate(read_json(heartbeat_path), now, **options)
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        report = dict(schema_version=1, state='monitor_error', code='heartbeat_unavailable_or_invalid', observed_at=now.isoformat())
    try:
        if Path(heartbeat_path).resolve() == Path(state_path).resolve():
            raise ValueError('paths')
        return persist(state_path, report)
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        return dict(schema_version=1, state='monitor_error', code='checkpoint_unavailable_or_invalid', observed_at=now.isoformat(), changed=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--heartbeat', required=True)
    parser.add_argument('--state', required=True)
    parser.add_argument('--lease-seconds', type=int, default=1800)
    parser.add_argument('--progress-seconds', type=int, default=1800)
    args = parser.parse_args()
    if args.lease_seconds < 1 or args.progress_seconds < 1:
        parser.error('thresholds must be positive')
    report = observe(args.heartbeat, args.state, datetime.now(timezone.utc),
                     lease_seconds=args.lease_seconds, progress_seconds=args.progress_seconds)
    print(json.dumps(report, ensure_ascii=True))
    return 3 if report['state'] == 'monitor_error' else 2 if report['state'] in ('stalled', 'blocked') else 0


if __name__ == '__main__':
    raise SystemExit(main())
