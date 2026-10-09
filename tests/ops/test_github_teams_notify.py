"""Isolated tests: no Microsoft credentials, GitHub write actions or network."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error

SOURCE = Path(__file__).resolve().parents[2] / "scripts/ops/github_teams_notify.py"
spec = importlib.util.spec_from_file_location("github_teams_notify", SOURCE)
notifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notifier)


class FakeResponse:
    status = 202

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, _size):
        return b""


class FakeOpener:
    def __init__(self, effects):
        self.effects = iter(effects)
        self.calls = []

    def open(self, req, timeout):
        self.calls.append((req, timeout))
        item = next(self.effects)
        if isinstance(item, Exception):
            raise item
        return item


class NotifyTests(unittest.TestCase):
    def test_push_main(self):
        msg = notifier.event_message("push", {
            "ref": "refs/heads/main", "after": "a" * 40,
            "head_commit": {"message": "fix: tests\nmore details"}})
        self.assertIn("fix: tests more details", msg)
        self.assertIn("/commit/" + "a" * 40, msg)

    def test_push_other_branch_and_invalid_sha_are_skipped(self):
        self.assertIsNone(notifier.event_message("push", {"ref": "refs/heads/other", "after": "a" * 40}))
        self.assertIsNone(notifier.event_message("push", {"ref": "refs/heads/main", "after": "unsafe"}))

    def test_pr_update_and_merge(self):
        payload = {"action": "closed", "pull_request": {"number": 15, "title": "fix: OAuth", "merged": True}}
        self.assertIn("integrado", notifier.event_message("pull_request_target", payload))
        payload["pull_request"]["merged"] = False
        self.assertIn("fechado sem integração", notifier.event_message("pull_request_target", payload))
        payload["action"] = "synchronize"
        self.assertIn("atualizado", notifier.event_message("pull_request_target", payload))

    def test_pr_strips_untrusted_control_chars(self):
        msg = notifier.event_message("pull_request_target", {"action": "opened", "number": 17,
            "pull_request": {"title": "Title\nInjected\rText"}})
        self.assertIn("Title Injected Text", msg)
        self.assertEqual(1, msg.count("\n"))

    def test_successful_workflows_are_silent(self):
        event = {"action": "completed", "workflow_run": {"id": 33, "name": "Build", "conclusion": "success"}}
        self.assertIsNone(notifier.event_message("workflow_run", event))

    def test_failed_workflow_alert(self):
        event = {"action": "completed", "workflow_run": {"id": 33, "name": "Build", "conclusion": "failure", "head_branch": "main"}}
        msg = notifier.event_message("workflow_run", event)
        self.assertIn("Falha", msg)
        self.assertIn("/actions/runs/33", msg)

    def test_non_bot_incident_ignored(self):
        incident = {"action": "opened", "issue": {"number": 9, "title": "[EBT OPS] Incident", "user": {"login": "human"}}}
        self.assertIsNone(notifier.event_message("issues", incident))
        incident["issue"]["user"]["login"] = "github-actions[bot]"
        self.assertIn("Incidente detectado", notifier.event_message("issues", incident))
        incident["action"] = "closed"
        self.assertIn("Incidente resolvido", notifier.event_message("issues", incident))

    def test_only_valid_teams_workflows_urls(self):
        self.assertTrue(notifier.webhook_is_allowed("https://prod-00.brazilsouth.logic.azure.com/workflows/abc/triggers/manual/paths/invoke?api-version=2016"))
        self.assertTrue(notifier.webhook_is_allowed("https://foo.environment.api.powerplatform.com/powerautomate/automations/direct/workflows/xxx"))
        for url in ("http://prod.logic.azure.com/path", "https://logic.azure.com.evil.test/path",
                    "https://prod.logic.azure.com@evil.test/path", "https://localhost/path", "https://logic.azure.com/"):
            with self.subTest(url=url):
                self.assertFalse(notifier.webhook_is_allowed(url))

    def test_sends_json_text_without_logging_secret(self):
        client = FakeOpener([FakeResponse()])
        url = "https://prod.logic.azure.com/workflows/secret?sig=REDACTED"
        notifier.send_to_teams(url, "EBT test", opener=client)
        req, timeout = client.calls[0]
        self.assertEqual(12, timeout)
        self.assertEqual("POST", req.method)
        self.assertEqual({"text": "EBT test"}, json.loads(req.data))

    def test_retries_rate_limit(self):
        response = error.HTTPError("https://prod.logic.azure.com/workflows/secret", 429, "limited", {}, None)
        client = FakeOpener([response, FakeResponse()])
        pauses = []
        notifier.send_to_teams("https://prod.logic.azure.com/workflows/secret", "retry", opener=client, pause=pauses.append)
        self.assertEqual([1], pauses)
        self.assertEqual(2, len(client.calls))

    def test_failure_error_does_not_disclose_url(self):
        response = error.HTTPError("https://prod.logic.azure.com/workflows/sensitive", 401, "unauthorized", {}, None)
        client = FakeOpener([response])
        with self.assertRaisesRegex(RuntimeError, "teams_webhook_http_401") as raised:
            notifier.send_to_teams("https://prod.logic.azure.com/workflows/sensitive", "retry", opener=client)
        self.assertNotIn("sensitive", str(raised.exception))

    def test_main_requires_setup_but_does_not_expose_webhook(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text(json.dumps({"ref": "refs/heads/main", "after": "a" * 40}), encoding="utf-8")
            env = {"GITHUB_REPOSITORY": notifier.REPO, "GITHUB_EVENT_NAME": "push", "GITHUB_EVENT_PATH": str(path)}
            with patch.dict("os.environ", env, clear=True):
                self.assertEqual(0, notifier.main())
            with patch.dict("os.environ", env | {"TEAMS_WORKFLOWS_WEBHOOK_URL": "https://prod.logic.azure.com/workflows/secret"}, clear=True):
                with patch.object(notifier, "send_to_teams") as mocked:
                    self.assertEqual(0, notifier.main())
                    mocked.assert_called_once()

    def test_production_report_notifies_transitions_only(self):
        self.assertIsNone(notifier.report_message({"notification": "none", "checks": []}, "5"))
        report = {"notification": "create", "checks": [
            {"state": "FAIL"}, {"state": "INCONCLUSIVE"}, {"state": "PASS"}
        ]}
        msg = notifier.report_message(report, "55")
        self.assertIn("novo incidente", msg)
        self.assertIn("Falhas: 1 | Inconclusivos: 1", msg)
        self.assertIn("/actions/runs/55", msg)
        report["notification"] = "close"
        self.assertIn("incidente encerrado", notifier.report_message(report, "55"))

    def test_production_report_main_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps({"notification": "create", "checks": []}), encoding="utf-8")
            env = {"GITHUB_REPOSITORY": notifier.REPO, "GITHUB_REF": "refs/heads/other"}
            with patch.dict("os.environ", env, clear=True):
                with patch.object(notifier, "send_to_teams") as mocked:
                    self.assertEqual(0, notifier.main(["--production-report", str(path)]))
                    mocked.assert_not_called()
            env["GITHUB_REF"] = "refs/heads/main"
            env["TEAMS_WORKFLOWS_WEBHOOK_URL"] = "https://prod.logic.azure.com/workflows/secret"
            with patch.dict("os.environ", env, clear=True):
                with patch.object(notifier, "send_to_teams") as mocked:
                    self.assertEqual(0, notifier.main(["--production-report", str(path)]))
                    mocked.assert_called_once()

    def test_unexpected_event_is_silent(self):
        self.assertIsNone(notifier.event_message("deployment", {}))
        self.assertIsNone(notifier.event_message("issues", {"action": "edited", "issue": {}}))


if __name__ == "__main__":
    unittest.main()
