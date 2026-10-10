import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

source = Path(__file__).resolve().parents[2] / 'scripts/ops/engineering_runner.py'
spec = importlib.util.spec_from_file_location('uid_runner', source)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class IdentityTests(unittest.TestCase):
    def test_controller_drops_model_uid_gid_and_every_supplementary_group(self):
        password = SimpleNamespace(getpwnam=lambda name: SimpleNamespace(pw_uid=999, pw_gid=998))
        with mock.patch.object(runner.os, 'name', 'posix'), \
             mock.patch.object(runner.os, 'getuid', return_value=0, create=True), \
             mock.patch.dict('sys.modules', {'pwd': password}):
            self.assertEqual(runner.untrusted_identity(), {'user': 999, 'group': 998, 'extra_groups': []})

    def test_no_wildcard_git_trust_or_external_hook_execution(self):
        argv = runner.controller_git(['git', 'commit', '-m', 'fixed'], '/specific/workspace')
        self.assertIn('safe.directory=/specific/workspace', argv)
        self.assertNotIn('safe.directory=*', argv)
        self.assertIn('core.hooksPath=/dev/null', argv)
        self.assertIn('core.fsmonitor=false', argv)


if __name__ == '__main__':
    unittest.main()
