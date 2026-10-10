import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts/ops/install_ebt_production_watch_vps.sh"
SERVICE = ROOT / "templates/systemd/ebt-production-watch-vps.service"
TIMER = ROOT / "templates/systemd/ebt-production-watch-vps.timer"


class ProductionWatchVpsInstallTests(unittest.TestCase):
    def test_installer_pins_reviewed_checkout_and_runs_source_tests(self):
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn("EXPECTED_SOURCE_SHA", text)
        self.assertIn("git -C \"$SOURCE_ROOT\" rev-parse HEAD", text)
        self.assertIn("status --porcelain --untracked-files=all", text)
        self.assertIn("test_production_watch.py", text)
        self.assertIn("notification must remain disabled", text)

    def test_installer_has_no_remote_write_or_secret_channel(self):
        text = INSTALLER.read_text(encoding="utf-8")
        for forbidden in (
            "GH_TOKEN", "TEAMS_WORKFLOWS_WEBHOOK_URL", "EBT_NOTIFY=true",
            "git push", "az containerapp", "sqlcmd", "systemctl restart",
            "curl ", "wget ", "PRIVATE KEY", "github_pat_",
        ):
            self.assertNotIn(forbidden, text)

    def test_service_is_read_only_and_unprivileged(self):
        text = SERVICE.read_text(encoding="utf-8")
        self.assertIn("User=ebt-watch", text)
        self.assertIn("Environment=EBT_NOTIFY=false", text)
        self.assertIn("NoNewPrivileges=true", text)
        self.assertIn("ProtectSystem=strict", text)
        self.assertIn("ProtectHome=true", text)
        self.assertIn("PrivateDevices=true", text)
        self.assertIn("RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6", text)
        self.assertIn("StateDirectory=ebt-production-watch", text)
        self.assertNotIn("EnvironmentFile=", text)

    def test_timer_is_fifteen_minutes(self):
        text = TIMER.read_text(encoding="utf-8")
        self.assertIn("OnBootSec=2min", text)
        self.assertIn("OnUnitActiveSec=15min", text)
        self.assertIn("AccuracySec=15s", text)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "bash syntax check requires Linux/macOS")
    def test_installer_bash_syntax(self):
        result = subprocess.run(["bash", "-n", str(INSTALLER)], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
