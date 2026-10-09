"""Offline regressions for the auditor, not acceptance tests of product code."""
import hashlib
import importlib.util
import json
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("pr_audit", ROOT / "scripts/ops/pr_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
SHA = "a" * 40


def run(wid=1, **values):
    return {"workflow_id": wid, "id": wid, "head_sha": SHA, "event": "pull_request",
            "run_number": 1, "run_attempt": 1, "status": "completed", "conclusion": "success", **values}


def review(state="APPROVED", sha=SHA, login="reviewer", **values):
    return {"id": 1, "user": {"login": login, "type": "User"}, "commit_id": sha,
            "state": state, "submitted_at": "2026-10-09T18:00:00Z", **values}


class Fixture:
    def __init__(self, moved=False, missing_file=False, listing_moved=False):
        self.moved = moved
        self.missing_file = missing_file
        self.listing_moved = listing_moved
        self.reads = 0
        self.listings = 0

    def get(self, repo, resource, **kwargs):
        self.reads += 1
        return {"number": 1, "head": {"sha": "b" * 40 if self.moved and self.reads > 1 else SHA, "ref": "feat"},
                "base": {"sha": "c" * 40, "ref": "main"}, "state": "open", "draft": True,
                "changed_files": 2, "title": "synthetic", "user": {"login": "author"}, "mergeable": True}

    def pages(self, repo, resource, key=None, **kwargs):
        if resource == "pulls":
            self.listings += 1
            return [] if self.listing_moved and self.listings > 1 else [{"number": 1}]
        if resource == "actions/runs":
            return [run()]
        if resource.endswith("/reviews"):
            return []
        if resource.endswith("/files"):
            return [{"filename": "a.py"}] if self.missing_file else [{"filename": "a.py"}, {"filename": "b.py"}]
        raise AssertionError("unexpected resource")


class EvidenceTests(unittest.TestCase):
    def test_no_runs(self):
        self.assertEqual(audit.summarize_runs([], SHA, (1,))[0], "NOT_RUN")

    def test_stale_sha_and_push_never_pass(self):
        self.assertEqual(audit.summarize_runs([run(head_sha="old"), run(event="push")], SHA)[0], "NOT_RUN")

    def test_required_workflow_missing(self):
        self.assertEqual(audit.summarize_runs([run()], SHA, (1, 2))[0], "MISSING_REQUIRED_WORKFLOW")

    def test_skips_never_pass(self):
        for value in ("skipped", "neutral"):
            self.assertEqual(audit.summarize_runs([run(conclusion=value)], SHA)[0], "NOT_PROVEN")

    def test_cancelled_failure_timeout(self):
        for value in ("cancelled", "failure", "timed_out", "action_required", None):
            self.assertEqual(audit.summarize_runs([run(conclusion=value)], SHA)[0], "FAIL")

    def test_waiting(self):
        self.assertEqual(audit.summarize_runs([run(status="queued", conclusion=None)], SHA)[0], "WAITING_CI")

    def test_rerun_overrides_old_success(self):
        rows = [run(), run(run_attempt=2, conclusion="failure")]
        self.assertEqual(audit.summarize_runs(rows, SHA)[0], "FAIL")
        self.assertEqual(audit.summarize_runs(list(reversed(rows)), SHA)[0], "FAIL")

    def test_required_pass_is_not_release(self):
        self.assertEqual(audit.summarize_runs([run()], SHA, (1,))[0], "PASS_CONFIGURED_CI")
        self.assertEqual(audit.summarize_runs([run()], SHA)[0], "OBSERVED_CI_SUCCESS")

    def test_invalid_workflow_identity(self):
        with self.assertRaises(audit.AuditError):
            audit.summarize_runs([run(wid=True)], SHA)

    def test_1000_generated_ci_scenarios(self):
        # 1000 reproducible inputs, not 1000 claims of whole-product review.
        for seed in range(1000):
            rng = random.Random(seed)
            sha = hashlib.sha256(str(seed).encode()).hexdigest()[:40]
            old = hashlib.sha256(f"old-{seed}".encode()).hexdigest()[:40]
            rows = [run(wid, head_sha=sha, id=seed * 10 + wid) for wid in (1, 2, 3)]
            mode = seed % 10
            expected = ["PASS_CONFIGURED_CI", "FAIL", "WAITING_CI", "MISSING_REQUIRED_WORKFLOW",
                        "NOT_PROVEN", "NOT_RUN", "NOT_RUN", "FAIL", "PASS_CONFIGURED_CI", "FAIL"][mode]
            if mode == 1:
                rows[rng.randrange(3)]["conclusion"] = "failure"
            elif mode == 2:
                rows[0].update(status="in_progress", conclusion=None)
            elif mode == 3:
                rows.pop()
            elif mode == 4:
                rows[0]["conclusion"] = "skipped"
            elif mode in (5, 6):
                for row in rows:
                    row.update({"head_sha": old} if mode == 5 else {"event": "push"})
            elif mode in (7, 8):
                rows.append({**rows[0], "run_attempt": 2, "conclusion": "failure" if mode == 7 else "success"})
                if mode == 8:
                    rows[0]["conclusion"] = "failure"
            elif mode == 9:
                rows[0]["conclusion"] = "cancelled"
            rng.shuffle(rows)
            with self.subTest(seed=seed):
                self.assertEqual(audit.summarize_runs(rows, sha, (1, 2, 3))[0], expected)

    def test_reviews_require_current_sha_and_not_author(self):
        for reviews in ([review(sha="old")], [review(login="author")], []):
            self.assertEqual(audit.summarize_reviews(reviews, SHA, "author"), "REVIEW_PENDING")

    def test_changes_on_older_sha_still_block(self):
        self.assertEqual(audit.summarize_reviews([review("CHANGES_REQUESTED", "old")], SHA, "author"), "CHANGES_REQUESTED")

    def test_dismissed_approval(self):
        rows = [review(), review("DISMISSED", id=2)]
        self.assertEqual(audit.summarize_reviews(rows, SHA, "author"), "REVIEW_PENDING")

    def test_comment_does_not_erase_request(self):
        rows = [review("CHANGES_REQUESTED"), review("COMMENTED", id=2)]
        self.assertEqual(audit.summarize_reviews(rows, SHA, "author"), "CHANGES_REQUESTED")

    def test_approval_is_not_threads_or_merge_acceptance(self):
        self.assertEqual(audit.summarize_reviews([review()], SHA, "author"), "APPROVAL_OBSERVED_THREADS_NOT_CHECKED")

    def test_bot_not_independent_reviewer(self):
        self.assertEqual(audit.summarize_reviews([review(user={"login": "bot", "type": "Bot"})], SHA, "author"), "REVIEW_PENDING")


class CollectionTests(unittest.TestCase):
    def test_normal_snapshot(self):
        report = audit.inventory(Fixture(), ["app-mail", "app-mail"])
        self.assertTrue(report["complete"])
        self.assertEqual(len(report["pull_requests"]), 1)
        self.assertFalse(report["pull_requests"][0]["merge_authorized"])

    def test_moving_head_marks_partial(self):
        report = audit.inventory(Fixture(moved=True), ["app-mail"])
        self.assertFalse(report["complete"])
        self.assertEqual(report["pull_requests"][0]["ci"], "HEAD_OR_BASE_MOVED")

    def test_file_count_mismatch(self):
        report = audit.inventory(Fixture(missing_file=True), ["app-mail"])
        self.assertFalse(report["complete"])
        self.assertEqual(report["errors"][0]["code"], "changed_files_incomplete")

    def test_listing_changes(self):
        self.assertFalse(audit.inventory(Fixture(listing_moved=True), ["app-mail"])["complete"])

    def test_pagination(self):
        client = audit.GitHubReadOnly()
        with patch.object(client, "get", side_effect=[[{}] * 100, [{}] * 3]):
            self.assertEqual(len(client.pages("app-mail", "pulls")), 103)

    def test_pagination_exhaustion_not_empty_success(self):
        client = audit.GitHubReadOnly()
        with patch.object(client, "get", return_value=[{}] * 100):
            with self.assertRaisesRegex(audit.AuditError, "pagination_limit"):
                client.pages("app-mail", "pulls")

    def test_partial_collection(self):
        client = audit.GitHubReadOnly()
        with patch.object(client, "get", return_value={"workflow_runs": [], "total_count": 1}):
            with self.assertRaises(audit.AuditError):
                client.pages("app-mail", "actions/runs", "workflow_runs")

    def test_invalid_collection(self):
        client = audit.GitHubReadOnly()
        with patch.object(client, "get", return_value=["invalid"]):
            with self.assertRaises(audit.AuditError):
                client.pages("app-mail", "pulls")

    def test_scope_and_path_rejected_before_network(self):
        client = audit.GitHubReadOnly("synthetic-secret")
        for repo, resource in (("foreign", "pulls"), ("app-mail", "../secrets"), ("app-mail", "/pulls"), ("app-mail", "https://bad")):
            with self.assertRaises(audit.AuditError):
                client.get(repo, resource)

    def test_redirect_refused(self):
        with self.assertRaisesRegex(audit.AuditError, "redirect_refused"):
            audit.NoRedirect().redirect_request(None, None, 302, "", {}, "https://untrusted")

    def test_error_sanitized_and_no_retry(self):
        client = audit.GitHubReadOnly("synthetic-secret")
        client.opener = MagicMock()
        client.opener.open.side_effect = HTTPError("url", 403, "synthetic-secret", {}, None)
        with self.assertRaisesRegex(audit.AuditError, "^github_http_403$"):
            client.get("app-mail", "pulls")
        self.assertEqual(client.opener.open.call_count, 1)

    def test_transport_sanitized(self):
        client = audit.GitHubReadOnly()
        client.opener = MagicMock()
        client.opener.open.side_effect = URLError("synthetic-secret")
        with self.assertRaisesRegex(audit.AuditError, "^github_transport_or_json_error$"):
            client.get("app-mail", "pulls")

    def test_invalid_review_schema_is_partial(self):
        fixture = Fixture()
        original = fixture.pages
        def pages(repo, resource, key=None, **kwargs):
            if resource.endswith("/reviews"):
                return [{"user": "invalid"}]
            return original(repo, resource, key, **kwargs)
        fixture.pages = pages
        report = audit.inventory(fixture, ["app-mail"])
        self.assertFalse(report["complete"])
        self.assertEqual(report["errors"][0]["code"], "invalid_pr_schema")

    def test_invalid_pr_number_never_fetches(self):
        client = MagicMock()
        for number in (True, 0, -1, "1"):
            with self.assertRaises(audit.AuditError):
                audit.audit_pr(client, "app-mail", number)
        client.get.assert_not_called()

    def test_atomic_output(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "audit.json"
            audit.write_report(path, {"complete": True})
            self.assertEqual(json.loads(path.read_text()), {"complete": True})
            with patch.object(audit.os, "replace", side_effect=OSError("synthetic")):
                with self.assertRaises(OSError):
                    audit.write_report(path, {"complete": False})
            self.assertEqual(json.loads(path.read_text()), {"complete": True})
            self.assertEqual(len(list(Path(folder).iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
