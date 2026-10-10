import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ops"))
from vps_automation_status import evaluate, TIMERS, EXPECTED_BRANCH, EXPECTED_REMOTE, EXPECTED_PRODUCT_ORIGIN, EXPECTED_PRODUCT_SCOPE, INITIAL_PROPOSAL_SHA


def healthy_report(schedule_status="FAIL", product_healthy=True):
    timers = {
        unit: {
            "enabled": {"rc": 0, "value": "enabled"},
            "active": {"rc": 0, "value": "active"},
        }
        for unit in TIMERS
    }
    return {
        "timers": timers,
        "flow_workspace": {
            "branch": EXPECTED_BRANCH,
            "head": INITIAL_PROPOSAL_SHA,
            "remote": EXPECTED_REMOTE,
            "agent_cannot_read_git": True,
        },
        "controller_transport": {
            "env_root_private": True,
            "git_key_root_private": True,
            "known_hosts_root_private": True,
            "agent_cannot_read_git_key": True,
            "agent_cannot_read_known_hosts": True,
        },
        "engineering_checkpoint": {"status": "task_verified", "synced_sha": INITIAL_PROPOSAL_SHA},
        "engineering_heartbeat": {"status": "idle"},
        "product_watch": {
            "origin": EXPECTED_PRODUCT_ORIGIN,
            "healthy_in_scope": product_healthy,
            "notification": "disabled",
            "scope": EXPECTED_PRODUCT_SCOPE,
        },
        "schedule_watchdog": {
            "last_observation": {"status": schedule_status, "alerts": ["schedule_gap"] if schedule_status == "FAIL" else []},
            "last_valid_observation": {"status": schedule_status},
        },
    }


class StatusEvaluationTests(unittest.TestCase):
    def test_schedule_incident_does_not_make_installation_integrity_fail(self):
        result = evaluate(healthy_report(schedule_status="FAIL"))
        self.assertEqual(result["installation_integrity"], "PASS")
        self.assertEqual(result["observed_health"]["github_schedule"], "FAIL")

    def test_product_health_failure_is_reported_separately_from_installation_integrity(self):
        result = evaluate(healthy_report(product_healthy=False))
        self.assertEqual(result["installation_integrity"], "PASS")
        self.assertEqual(result["observed_health"]["product"], "UNHEALTHY")

    def test_missing_or_inactive_timer_fails_installation_integrity(self):
        report = healthy_report()
        report["timers"]["ebt-engineering-runner.timer"]["active"] = {"rc": 3, "value": "inactive"}
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "FAIL")
        self.assertIn("ebt-engineering-runner.timer:not_active", result["integrity_failures"])

    def test_wrong_branch_or_remote_fails_installation_integrity(self):
        report = healthy_report()
        report["flow_workspace"]["branch"] = "main"
        report["flow_workspace"]["remote"] = "https://example.invalid/repo.git"
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "FAIL")
        self.assertIn("flow_workspace:wrong_branch", result["integrity_failures"])
        self.assertIn("flow_workspace:wrong_remote", result["integrity_failures"])

    def test_workspace_head_must_match_synced_checkpoint(self):
        report = healthy_report()
        report["engineering_checkpoint"] = {
            "status": "task_verified",
            "synced_sha": "2" * 40,
            "source_commit": INITIAL_PROPOSAL_SHA,
        }
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "FAIL")
        self.assertIn("flow_workspace:head_checkpoint_mismatch", result["integrity_failures"])
        self.assertFalse(result["observed_health"]["workspace_head_consistent"])
        self.assertEqual(result["controller_consistency"]["expected_head"], "2" * 40)

    def test_awaiting_sync_uses_sync_sha_as_expected_head(self):
        report = healthy_report()
        report["flow_workspace"]["head"] = "3" * 40
        report["engineering_checkpoint"] = {
            "status": "awaiting_sync",
            "source_commit": INITIAL_PROPOSAL_SHA,
            "sync_sha": "3" * 40,
        }
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "PASS")
        self.assertTrue(result["observed_health"]["workspace_head_consistent"])

    def test_pre_first_cycle_requires_initial_proposal_sha(self):
        report = healthy_report()
        report["engineering_checkpoint"] = {"state": "MISSING"}
        report["engineering_heartbeat"] = {"state": "MISSING"}
        report["flow_workspace"]["head"] = "4" * 40
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "FAIL")
        self.assertEqual(result["controller_consistency"]["expected_head"], INITIAL_PROPOSAL_SHA)

    def test_agent_transport_access_fails_installation_integrity(self):
        report = healthy_report()
        report["controller_transport"]["agent_cannot_read_git_key"] = False
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "FAIL")
        self.assertIn("controller_transport:agent_cannot_read_git_key", result["integrity_failures"])

    def test_missing_monitor_evidence_fails_installation_integrity(self):
        report = healthy_report()
        report["product_watch"] = {"state": "MISSING"}
        report["schedule_watchdog"] = {"state": "MISSING"}
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "FAIL")
        self.assertIn("product_watch:unexpected_origin", result["integrity_failures"])
        self.assertIn("schedule_watchdog:missing_observation", result["integrity_failures"])

    def test_engineering_can_be_pending_first_cycle_without_failing_installation(self):
        report = healthy_report()
        report["engineering_checkpoint"] = {"state": "MISSING"}
        report["engineering_heartbeat"] = {"state": "MISSING"}
        result = evaluate(report)
        self.assertEqual(result["installation_integrity"], "PASS")
        self.assertEqual(result["observed_health"]["engineering"], "PENDING_FIRST_CYCLE")


if __name__ == "__main__":
    unittest.main()
