import hashlib
import hmac
from datetime import timedelta
import httpx
import pytest
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.domain import now
from ebt_prospecting.service import ProspectService
from ebt_prospecting.channels import MessageWorker, WhatsAppCloud, ProviderOutcome
from test_domain import ROW, SOURCE


class Provider:
    def __init__(self, status="draft_created"):
        self.status = status
        self.calls = []

    async def execute(self, message):
        self.calls.append(message)
        return ProviderOutcome(self.status, "provider-123", "https://outlook.office.com/mail/")


async def setup_message():
    s = ProspectService(AsyncMongoMockClient().synthetic)
    await s.initialize()
    c = await s.add_contact("A", "u1", ROW, SOURCE)
    preview = await s.prepare("A", c["id"], "presentation", "Erick")
    m = await s.approve_message("A", "u1", c["id"], preview["digest"], "presentation", "Erick", now().isoformat()+"Z", "draft")
    return s, c, m


async def test_scheduled_draft_executes_once_across_workers():
    s, c, m = await setup_message()
    p = Provider()
    w = MessageWorker(s, p)
    await w.tick()
    await w.tick()
    assert len(p.calls) == 1
    saved = (await s.messages("A"))[0]
    assert saved["status"] == "draft_created"
    assert saved["provider_id"] == "provider-123"
    assert (await s.history("A", c["id"]))[0]["kind"] == "draft_created"


async def test_changed_recipient_cancels_frozen_message():
    s, c, m = await setup_message()
    await s.update_contact("A", c["id"], {"version": 1, "email": "novo@example.com"})
    p = Provider()
    await MessageWorker(s, p).tick()
    assert p.calls == []
    assert (await s.messages("A"))[0]["status"] == "needs_review"


async def test_unknown_provider_result_is_never_retried_automatically():
    s, c, m = await setup_message()
    p = Provider("unknown")
    await MessageWorker(s, p).tick()
    await MessageWorker(s, p).tick()
    assert len(p.calls) == 1
    assert (await s.messages("A"))[0]["status"] == "unknown"


async def test_crash_after_claim_becomes_unknown_instead_of_sending_twice():
    s, c, m = await setup_message()
    await s.db.ebt_p_messages.update_one({"space": "A", "id": m["id"]}, {"$set": {"status": "executing", "claimed_at": now()-timedelta(minutes=20)}})
    p = Provider()
    await MessageWorker(s, p).tick()
    assert not p.calls
    assert (await s.messages("A"))[0]["status"] == "unknown"


def test_whatsapp_webhook_rejects_tampering():
    body = b'{"entry":[]}'
    signature = "sha256=" + hmac.new(b"synthetic-key", body, hashlib.sha256).hexdigest()
    assert WhatsAppCloud.valid_signature(body, signature, "synthetic-key")
    assert not WhatsAppCloud.valid_signature(body + b"x", signature, "synthetic-key")
    assert not WhatsAppCloud.valid_signature(body, signature, "")


async def test_whatsapp_template_uses_official_api_and_does_not_claim_delivery():
    captured = []
    def handler(request):
        captured.append(request)
        return httpx.Response(200, json={"messages": [{"id": "wamid.synthetic"}]})
    w = WhatsAppCloud("https://graph.facebook.com/v23.0", "123456", "synthetic-token", transport=httpx.MockTransport(handler))
    result = await w.template("5511999999999", "approved_template", "pt_BR", ["Ana"])
    assert result.status == "accepted"
    assert result.provider_id == "wamid.synthetic"
    assert captured[0].url.path == "/v23.0/123456/messages"
    assert b'"type":"template"' in captured[0].content


async def test_http_429_is_deferred_and_timeout_stays_unknown():
    w = WhatsAppCloud("https://graph.facebook.com/v23.0", "123456", "synthetic-token", transport=httpx.MockTransport(lambda r: httpx.Response(429, headers={"Retry-After": "120"})))
    assert (await w.template("5511999999999", "template", "pt_BR", [])).status == "deferred"
