#!/usr/bin/env python3
"""Open ChatGPT in the persistent Linux browser; never submit messages or move credentials."""
import argparse
import json
import re
import subprocess
from urllib.parse import urlsplit

COMPOSE = '/opt/ebt-engineering/linux-chat/compose.yaml'
CONTAINER = 'ebt-linux-chat'


def validate_url(url):
    if not isinstance(url, str) or any(ord(char) < 33 for char in url):
        raise ValueError('invalid_chat_url')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.netloc != 'chatgpt.com'
            or parsed.query or parsed.fragment
            or not re.fullmatch(r'/(?:c/[0-9a-fA-F-]{36})?', parsed.path)):
        raise ValueError('only_chatgpt_home_or_conversation_allowed')
    return url


def verify_bindings(bindings):
    active = {key: value for key, value in bindings.items() if value}
    if active != {'7900/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '5800'}]}:
        raise ValueError('remote_desktop_must_remain_loopback_only')


def execute(argv, timeout=30, env=None):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
    if result.returncode:
        raise ValueError('linux_browser_command_failed_private_output_omitted')
    return result.stdout


def status():
    container = json.loads(execute(['docker', 'inspect', CONTAINER]))[0]
    verify_bindings(container['HostConfig']['PortBindings'])
    if not container['State']['Running']:
        raise ValueError('linux_browser_not_running')
    execute(['docker', 'exec', CONTAINER, 'pgrep', '-x', 'chrome'])
    return {'status': 'browser_running', 'viewer_on_vps': 'http://127.0.0.1:5800/vnc.html?autoconnect=1&resize=scale',
            'authentication_verified': False, 'prompt_submitted': False,
            'session_storage': 'private_linux_profile', 'automatic_quota_bypass': False}


def open_chat(url):
    validate_url(url)
    # Keep the window and drafts. Chrome uses its normal profile IPC to open a tab.
    execute(['docker', 'compose', '-f', COMPOSE, 'up', '-d',
             '--wait', '--wait-timeout', '60'], timeout=75)
    report = status()
    execute(['docker', 'exec', '-d', CONTAINER, '/usr/bin/google-chrome',
             '--user-data-dir=/home/seluser/ebt-profile', '--no-first-run', '--new-tab', url])
    report['status'] = 'browser_open_requested'
    report['browser_recreated'] = False
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://chatgpt.com/')
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    try:
        report = status() if args.status else open_chat(args.url)
    except (ValueError, OSError, subprocess.TimeoutExpired, KeyError, IndexError):
        print(json.dumps({'status': 'browser_unavailable', 'authentication_verified': False,
                          'prompt_submitted': False, 'action': 'check_compose_and_loopback_binding_locally'}))
        return 2
    print(json.dumps(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
