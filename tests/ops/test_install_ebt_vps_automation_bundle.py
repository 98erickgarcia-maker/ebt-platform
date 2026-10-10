import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts/ops/install_ebt_vps_automation_bundle.sh"
STATUS = ROOT / "scripts/ops/collect_ebt_vps_automation_status.sh"
ROLLBACK = ROOT / "scripts/ops/disable_ebt_vps_automation.sh"
STATUS_PY = ROOT / "scripts/ops/vps_automation_status.py"


class BundleTests(unittest.TestCase):
    def test_pins_all_reviewed_sources(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        for marker in (
            'FLOW_SOURCE_SHA="532a3301c6de60f99d431e1f9d4f8294bf0ab8b5"',
            'FLOW_PROPOSAL_SHA="0b2b21813658ccc693e4bc870fa3f0b5d09f8bb0"',
            'WATCHDOG_HEAD_SHA="e6a112f4db0d0bec02f623c968c579116b7dfe9c"',
            'WATCHDOG_SOURCE_SHA="56a659ac1fc7597f7e453bd7e39042742e8f408e"',
            'PRODUCT_SHA="3820d0edd5126ae416ea569b3dc30b5b0ce1a215"',
            'FLOW_PROPOSAL_BRANCH="codex/flow-history-proposal-vps-20261009"',
        ):
            self.assertIn(marker, text)

    def test_privileged_install_requires_root_owned_nonwritable_bundle(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("trusted_root_path", text)
        self.assertIn('if (( CHECK_ONLY == 0 )); then', text)
        self.assertIn('"$BUNDLE_ROOT/.git"', text)
        self.assertIn('"$BUNDLE_ROOT/scripts/ops/vps_automation_status.py"', text)
        self.assertIn('must not be group/other writable', text)

    def test_preflight_checks_service_toolchain_and_codex_auth(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn('ENGINEERING_PATH=', text)
        self.assertIn('runuser -u ebt-scout -- env PATH="$ENGINEERING_PATH" bash -lc', text)
        self.assertIn('command -v codex', text)
        self.assertIn('command -v dotnet', text)
        self.assertIn('command -v npm', text)
        self.assertIn('CODEX_HOME=/var/lib/ebt-scout/.codex codex login status', text)
        self.assertLess(
            text.index('codex login status'),
            text.index('Preparing pinned sources...'),
        )

    def test_bootstrap_self_pins_its_own_checkout(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        for marker in (
            "EXPECTED_BUNDLE_SHA",
            'git -C "$BUNDLE_ROOT" rev-parse HEAD',
            'Bootstrap checkout SHA differs from EXPECTED_BUNDLE_SHA.',
            'Bootstrap checkout must be clean.',
            'GIT_OPTIONAL_LOCKS=0 git -C "$BUNDLE_ROOT" status --porcelain --untracked-files=all',
        ):
            self.assertIn(marker, text)

    def test_installs_stable_status_and_rollback_helpers(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn('HELPER_DIR="/opt/ebt-vps-automation"', text)
        self.assertIn('STATUS_COMMAND="/usr/local/sbin/ebt-vps-automation-status"', text)
        self.assertIn('DISABLE_COMMAND="/usr/local/sbin/ebt-vps-automation-disable"', text)
        self.assertIn('install -o root -g root -m 0644 "$BUNDLE_ROOT/scripts/ops/vps_automation_status.py"', text)
        self.assertIn('Status: sudo ebt-vps-automation-status', text)
        self.assertIn('Rollback timers only: sudo ebt-vps-automation-disable', text)

    def test_flow_installer_receives_distinct_source_and_proposal_pins(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn('EXPECTED_SOURCE_SHA="$FLOW_SOURCE_SHA"', text)
        self.assertIn('EXPECTED_PROPOSAL_SHA="$FLOW_PROPOSAL_SHA"', text)
        self.assertIn('[[ "$proposal_remote" == "$FLOW_PROPOSAL_SHA" ]]', text)

    def test_check_only_exits_before_installers(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        check_pos = text.index("if (( CHECK_ONLY == 1 ))")
        watchdog_install = text.index('bash "$WATCHDOG_SOURCE/scripts/ops/install_ebt_watchdog_vps.sh"')
        self.assertLess(check_pos, watchdog_install)
        self.assertIn("CHECK_ONLY: no systemd unit was installed or enabled.", text)

    def test_watchdog_probe_is_forced_and_exit_two_is_accepted(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn('systemctl start ebt-schedule-watchdog.service', text)
        self.assertIn('watchdog_probe_rc', text)
        self.assertIn('"$watchdog_probe_rc" -ne 0 && "$watchdog_probe_rc" -ne 2', text)
        self.assertIn('[[ -s /var/lib/ebt-watch/state.json ]]', text)
        self.assertLess(
            text.index('systemctl start ebt-schedule-watchdog.service'),
            text.index('install_ebt_production_watch_vps.sh'),
        )

    def test_flow_execution_is_deferred_until_helpers_and_timer_activation(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("EBT_DEFER_TIMER_START=1", text)
        self.assertIn("activated before bundle integrity gate", text)
        self.assertIn("Flow runner service started before bundle integrity gate", text)
        self.assertIn("systemctl enable --now ebt-engineering-runner.timer ebt-engineering-watch.timer", text)
        self.assertIn("Flow runner service fired before the two-minute activation delay", text)
        flow_install = text.index('install_ebt_engineering_auto.sh')
        helper_install = text.index('Installing stable local status/rollback helpers')
        flow_enable = text.index('systemctl enable --now ebt-engineering-runner.timer ebt-engineering-watch.timer')
        final_status = text.index('Final sanitized activation integrity check')
        self.assertLess(flow_install, helper_install)
        self.assertLess(helper_install, flow_enable)
        self.assertLess(flow_enable, final_status)

    def test_install_order_puts_read_only_monitors_before_flow(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        watchdog = text.index('install_ebt_watchdog_vps.sh')
        product = text.index('install_ebt_production_watch_vps.sh')
        flow = text.index('install_ebt_engineering_auto.sh')
        self.assertLess(watchdog, product)
        self.assertLess(product, flow)

    def test_clean_host_gate_and_partial_install_rollback(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn('TARGET_TIMERS=(', text)
        self.assertIn('already active/enabled; use the individual diagnostic/recovery path', text)
        self.assertIn('on_exit', text)
        self.assertIn('trap on_exit EXIT', text)
        self.assertIn('rc != 0 && INSTALL_STARTED == 1', text)
        self.assertNotIn('trap rollback_on_error ERR', text)
        self.assertIn('INSTALL_STARTED=1', text)
        self.assertIn('INSTALL_STARTED=0', text)
        self.assertIn('systemctl disable --now "$unit"', text)
        self.assertIn('runuser', text)
        self.assertLess(
            text.index('INSTALL_STARTED=1'),
            text.index('bash "$WATCHDOG_SOURCE/scripts/ops/install_ebt_watchdog_vps.sh"'),
        )

    def test_bundle_has_no_dangerous_product_operations(self):
        text = BOOTSTRAP.read_text(encoding="utf-8")
        for forbidden in (
            "push --force", "reset --hard", "az containerapp",
            "sqlcmd", "systemctl restart", "TEAMS_WORKFLOWS_WEBHOOK_URL",
            "GH_TOKEN=", "github_pat_", "PRIVATE KEY-----",
        ):
            self.assertNotIn(forbidden, text)

    def test_status_collector_is_sanitized(self):
        wrapper = STATUS.read_text(encoding="utf-8")
        text = STATUS_PY.read_text(encoding="utf-8")
        self.assertIn("vps_automation_status.py", wrapper)
        for allowed in (
            "installation_integrity", "observed_health", "engineering_checkpoint",
            "engineering_heartbeat", "product_watch", "schedule_watchdog",
        ):
            self.assertIn(allowed, text)
        for forbidden in ("GH_TOKEN", "TEAMS_WORKFLOWS_WEBHOOK_URL", "Authorization: Bearer", "PRIVATE KEY-----"):
            self.assertNotIn(forbidden, text)

    def test_rollback_only_disables_automation_timers(self):
        text = ROLLBACK.read_text(encoding="utf-8")
        self.assertIn("systemctl disable --now", text)
        for forbidden in ("rm -rf", "git reset", "git push", "sqlcmd", "az containerapp", "systemctl restart"):
            self.assertNotIn(forbidden, text)

    @unittest.skipUnless(os.name != "nt" and shutil.which("bash"), "bash syntax requires Linux/macOS")
    def test_shell_syntax(self):
        for path in (BOOTSTRAP, STATUS, ROLLBACK):
            result = subprocess.run(["bash", "-n", str(path)], text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
