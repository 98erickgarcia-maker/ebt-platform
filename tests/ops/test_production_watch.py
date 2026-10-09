import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

source = Path(__file__).resolve().parents[2] / "scripts/ops/production_watch.py"
spec = importlib.util.spec_from_file_location("ebt_watch", source)
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


def health_response(path):
    return (200, "application/json", json.dumps({
        "status": "alive" if path.endswith("live") else "ready",
        "version": "0.3.0"
    }).encode())


class WatchTests(unittest.TestCase):
    def test_live_and_ready(self):
        self.assertTrue(all(r["state"] == "PASS" for r in watch.health(health_response)))

    def test_unparseable_health(self):
        self.assertEqual("FAIL", watch.health(lambda _: (200, "application/json", b"bad-json"))[0]["state"])

    def test_non_object_health(self):
        self.assertEqual("FAIL", watch.health(lambda _: (200, "application/json", b"null"))[0]["state"])

    def test_version_mismatch(self):
        def fetch(path):
            status, mime, value = health_response(path)
            data = json.loads(value)
            data["version"] = path
            return status, mime, json.dumps(data).encode()
        self.assertEqual("FAIL", watch.health(fetch)[-1]["state"])

    def test_network_error_is_inconclusive(self):
        self.assertEqual("INCONCLUSIVE", watch.health(lambda _: (None, "", b""))[0]["state"])

    def test_rate_limit_is_inconclusive(self):
        self.assertEqual("INCONCLUSIVE", watch.security(lambda _: (429, "", b""))[0]["state"])

    def test_anonymous_denied(self):
        self.assertTrue(all(r["state"] == "PASS" for r in watch.security(lambda _: (401, "", b""))))

    def test_anonymous_accessible_is_failure_without_leak(self):
        checks = watch.security(lambda _: (200, "", b"PRIVATE USER DATA"))
        self.assertTrue(all(r["state"] == "FAIL" for r in checks))
        self.assertNotIn("PRIVATE USER DATA", json.dumps(checks))

    def test_redirect_is_not_followed(self):
        self.assertIsNone(watch.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test"))

    def test_foreign_hosts_rejected(self):
        for path in ("https://evil.test/", "//evil.test/", "http://localhost/"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                watch.url_for(path)

    def test_frontend_assets(self):
        def fetch(path):
            if path == "/":
                return (200, "text/html", b'<title>EBT</title><div id="root"></div><script type="module" src="/assets/a.js"></script><link rel="stylesheet" href="/assets/a.css">')
            return (200, "application/javascript", b"console.log(1)") if path.endswith(".js") else (200, "text/css", b"body{}")
        self.assertTrue(all(r["state"] == "PASS" for r in watch.frontend(fetch)))

    def test_frontend_missing_script(self):
        self.assertEqual("FAIL", watch.frontend(lambda _: (200, "text/html", b'EBT<div id="root"></div>'))[-1]["state"])

    def test_frontend_invalid_js_mime(self):
        def fetch(path):
            return 200, "text/html", b'EBT<div id="root"></div><script type="module" src="/assets/a.js"></script>'
        self.assertEqual("FAIL", watch.frontend(fetch)[-1]["state"])

    def test_frontend_foreign_asset_not_requested(self):
        paths = []
        def fetch(path):
            paths.append(path)
            return 200, "text/html", b'EBT<div id="root"></div><script type="module" src="//evil.test/app.js"></script>'
        self.assertEqual("FAIL", watch.frontend(fetch)[-1]["state"])
        self.assertEqual(["/"], paths)

    def test_incident_transition(self):
        bad = [{"agent": "A", "check": "B", "state": "FAIL", "http": 503}]
        good = [{"agent": "A", "check": "B", "state": "PASS", "http": 200}]
        self.assertEqual("create", watch.incident_transition(bad, None))
        existing = {"body": "<!-- state:" + watch.fingerprint(bad) + " -->"}
        self.assertEqual("none", watch.incident_transition(bad, existing))
        self.assertEqual("close", watch.incident_transition(good, existing))
        bad[0]["http"] = 502
        self.assertEqual("update", watch.incident_transition(bad, existing))

    def test_inconclusive_cannot_resolve_incident(self):
        rows = [{"agent": "A", "check": "B", "state": "INCONCLUSIVE", "http": None}]
        self.assertNotEqual("close", watch.incident_transition(rows, {"body": "existing"}))

    def test_empty_never_closes_incident(self):
        self.assertEqual("none", watch.incident_transition([], {"body": "existing"}))

    def test_only_bot_issue_is_eligible(self):
        report = {"checks": [{"agent": "A", "check": "B", "state": "PASS", "http": 200}], "observed_at": "2026-10-09"}
        with patch.object(watch, "github", return_value=[{
                "number": 42, "user": {"login": "human"}, "body": watch.ISSUE_MARKER
        }]) as mock:
            self.assertEqual("none", watch.notify(report, "mock-token"))
            self.assertEqual(1, mock.call_count)

    def test_create_incident_once(self):
        report = {"checks": [{"agent": "A", "check": "B", "state": "FAIL", "http": 503}], "observed_at": "2026-10-09"}
        with patch.object(watch, "github", side_effect=[[], {"number": 43}]) as mock:
            self.assertEqual("create", watch.notify(report, "mock-token"))
            self.assertEqual("POST", mock.call_args_list[1].args[0])

    def test_github_write_scope(self):
        with self.assertRaises(ValueError):
            watch.github("POST", "/repos/another/repo/issues", "x")


if __name__ == "__main__":
    unittest.main()
