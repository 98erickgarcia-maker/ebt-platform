import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ops/ebt_engineering_auto.sh"
INSTALLER = ROOT / "scripts/ops/install_ebt_engineering_auto.sh"
SERVICE = ROOT / "deployment/systemd/ebt-engineering-auto.service"
TIMER = ROOT / "deployment/systemd/ebt-engineering-auto.timer"


class LinuxAutomationTests(unittest.TestCase):
    def test_script_has_fail_safe_git_controls(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('PROPOSAL_BRANCH="${PROPOSAL_BRANCH:-codex/flow-history-proposal-vps-20261009}"', text)
        self.assertIn('PENDING_PUSH="${PENDING_PUSH:-$STATE_DIR/pending-push.json}"', text)
        self.assertIn('git -C "$REPO_DIR" push "$REMOTE" "$sha:refs/heads/$PROPOSAL_BRANCH"', text)
        self.assertIn('merge --ff-only', text)
        self.assertIn('validate_dirty_paths', text)
        self.assertNotIn('push --force', text)
        self.assertNotIn('reset --hard', text)
        self.assertNotIn('git merge main', text)
        self.assertNotIn('az containerapp', text)
        self.assertNotIn('sqlcmd', text)

    def test_runner_push_stays_disabled(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('runner allow_push must stay false', text)

    def test_installer_uses_separate_push_url_and_dry_run(self):
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn('PUSH_REPOSITORY_URL=', text)
        self.assertIn('remote set-url --push origin', text)
        self.assertIn('ebt-engineering-auto --dry-run', text)
        self.assertNotIn('PRIVATE KEY', text)
        self.assertNotIn('github_pat_', text)

    def test_systemd_schedule_is_bounded_to_15_minutes(self):
        service = SERVICE.read_text(encoding="utf-8")
        timer = TIMER.read_text(encoding="utf-8")
        self.assertIn("Type=oneshot", service)
        self.assertIn("User=ebt-scout", service)
        self.assertIn("SuccessExitStatus=20", service)
        self.assertIn("OnCalendar=*-*-* *:00,15,30,45:00", timer)
        self.assertIn("Persistent=true", timer)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "bash syntax check requires Linux/macOS")
    def test_bash_syntax(self):
        for path in (SCRIPT, INSTALLER):
            result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
