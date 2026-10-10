import importlib.util
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('linux_chat', Path(__file__).resolve().parents[2] / 'scripts/ops/linux_chat.py')
chat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat)


class LinuxChatTests(unittest.TestCase):
    def test_chat_url_requires_exact_https_origin_without_secrets(self):
        for url in ['https://chatgpt.com/', 'https://chatgpt.com/c/00000000-0000-4000-8000-000000000001']:
            self.assertEqual(chat.validate_url(url), url)
        for url in ['http://chatgpt.com/', 'https://chatgpt.com.evil.invalid/',
                    'https://' + 'user:password@' + 'chatgpt.com/', 'https://chatgpt.com:444/',
                    'https://chatgpt.com/?token=private', 'https://chatgpt.com/#private',
                    'https://chatgpt.com/;touch-private', 'https://chatgpt.com/\n']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                chat.validate_url(url)

    def test_refuses_public_or_additional_remote_desktop_ports(self):
        valid = {'7900/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '5800'}]}
        chat.verify_bindings(valid)
        for bindings in [{}, {'7900/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '5800'}]},
                         {**valid, '5900/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '5900'}]}]:
            with self.subTest(bindings=bindings), self.assertRaises(ValueError):
                chat.verify_bindings(bindings)

    def test_manual_open_never_claims_authentication_or_submits_prompt(self):
        def run(argv, **kwargs):
            self.assertNotIn('shell', kwargs)
            if argv[1] == 'inspect':
                return types.SimpleNamespace(returncode=0, stdout=json.dumps([{
                    'State': {'Running': True},
                    'HostConfig': {'PortBindings': {'7900/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '5800'}]}},
                }]))
            return types.SimpleNamespace(returncode=0, stdout='')
        with patch.object(chat.subprocess, 'run', side_effect=run) as calls:
            report = chat.open_chat('https://chatgpt.com/')
        self.assertEqual(report['status'], 'browser_open_requested')
        self.assertFalse(report['authentication_verified'])
        self.assertFalse(report['prompt_submitted'])
        self.assertNotIn('--force-recreate', calls.call_args_list[0].args[0])
        self.assertTrue(any(call.args[0][1] == 'exec' and call.args[0][-1] == 'https://chatgpt.com/'
                            for call in calls.call_args_list))
        self.assertFalse(report['browser_recreated'])

    def test_rejects_bad_url_before_any_process_or_docker_start(self):
        with patch.object(chat.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                chat.open_chat('https://other.invalid/')
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()

