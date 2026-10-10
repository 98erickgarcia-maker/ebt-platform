import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts/ops/install_ebt_engineering_auto.sh"
SERVICE = ROOT / "templates/systemd/ebt-engineering-runner.service"
RUNNER_TIMER = ROOT / "templates/systemd/ebt-engineering-runner.timer"
WATCH_TIMER = ROOT / "templates/systemd/ebt-engineering-watch.timer"
MANIFEST = ROOT / "planejamento/engineering_blocks.json"
BAT = ROOT / "scripts/ops/EBT_AUTO_LINUX.bat"


class LinuxAutomationTests(unittest.TestCase):
    def test_manifest_enables_only_native_verified_sync(self):
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(m["allow_push"])
        self.assertFalse(m["allow_deploy"])
        self.assertFalse(m["allow_migration"])
        self.assertFalse(m["allow_external_messages"])
        self.assertEqual(m["branch"], "codex/flow-history-proposal-vps-20261009")
        self.assertEqual(m["repository"], "98erickgarcia-maker/ebt-platform")

    def test_service_keeps_git_controller_root_and_model_unprivileged(self):
        text = SERVICE.read_text(encoding="utf-8")
        self.assertIn("User=root", text)
        self.assertIn("Group=ebt-scout", text)
        self.assertIn("EnvironmentFile=/etc/ebt-engineering-controller.env", text)
        self.assertIn("CapabilityBoundingSet=CAP_SETUID CAP_SETGID", text)
        self.assertIn("NoNewPrivileges=true", text)

    def test_installer_requires_root_only_transport_material(self):
        text = INSTALLER.read_text(encoding="utf-8")
        for marker in (
            "EXPECTED_SOURCE_SHA",
            "EXPECTED_PROPOSAL_SHA",
            "GIT_KEY_PATH",
            "KNOWN_HOSTS_PATH",
            "root_private_file",
            'SSH_REMOTE="git@github.com:${REPOSITORY}.git"',
            "Remote proposal branch moved during installation.",
            "Workspace proposal SHA differs from approved SHA.",
            'chmod 0700 "$WORKSPACE/.git"',
            'install -d -o root -g "$SERVICE_USER" -m 0770 "$STATE/model-io"',
        ):
            self.assertIn(marker, text)
        for forbidden in ("push --force", "reset --hard", "az containerapp", "sqlcmd", "PRIVATE KEY-----", "github_pat_"):
            self.assertNotIn(forbidden, text)

    def test_proposal_sha_is_rechecked_before_systemd_enable(self):
        text = INSTALLER.read_text(encoding="utf-8")
        remote_check = text.index('Remote proposal branch moved during installation.')
        enable = text.index('systemctl enable --now ebt-engineering-runner.timer')
        self.assertLess(remote_check, enable)
        self.assertIn('[[ "$remote_proposal" == "$EXPECTED_PROPOSAL_SHA" ]]', text)
        self.assertIn('[[ "$workspace_head" == "$EXPECTED_PROPOSAL_SHA" ]]', text)

    def test_only_native_fifteen_minute_timers_are_used(self):
        runner = RUNNER_TIMER.read_text(encoding="utf-8")
        watch = WATCH_TIMER.read_text(encoding="utf-8")
        bat = BAT.read_text(encoding="utf-8")
        self.assertIn("OnUnitInactiveSec=15min", runner)
        self.assertIn("OnCalendar=*-*-* *:0/15:00", watch)
        self.assertIn("ebt-engineering-runner.service", bat)
        self.assertNotIn("ebt-engineering-auto.service", bat)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "bash syntax check requires Linux/macOS")
    def test_installer_bash_syntax(self):
        result = subprocess.run(["bash", "-n", str(INSTALLER)], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
