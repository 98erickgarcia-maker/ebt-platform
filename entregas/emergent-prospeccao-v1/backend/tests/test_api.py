import pytest
import httpx
from fastapi import FastAPI, Request, HTTPException
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.service import ProspectService
from ebt_prospecting.router import create_router
from ebt_prospecting.config import Config
from ebt_prospecting.outlook import OutlookConnector
from test_domain import ROW, SOURCE
from ebt_prospecting.domain import now


@pytest.fixture
async def api():
    db = AsyncMongoMockClient().synthetic
    service = ProspectService(db)
    await service.initialize()
    cfg = Config(owner_email="owner@example.com", workspace="A", origins=["https://test.example.com"])
    async def current(request: Request):
        if not request.headers.get("Test-User"):
            raise HTTPException(401)
        return {"user_id": "user-a", "email": request.headers["Test-User"], "role": "owner"}
    app = FastAPI()
    app.include_router(create_router(service, cfg, current, OutlookConnector(db, cfg)))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://test.example.com", headers={"Test-User": "owner@example.com", "Origin": "https://test.example.com", "X-EBT-Action": "prospecting"}) as client:
        yield client, service, cfg


async def test_anonymous_and_other_user_are_blocked(api):
    client, s, cfg = api
    assert (await client.get("/api/prospecting/summary", headers={"Test-User": ""})).status_code == 401
    assert (await client.get("/api/prospecting/summary", headers={"Test-User": "other@example.com"})).status_code == 403


async def test_mutation_rejects_untrusted_origin_and_missing_action(api):
    client, s, cfg = api
    data = {"rows": [ROW], "source": SOURCE}
    assert (await client.post("/api/prospecting/catalog/import", json=data, headers={"Origin": "https://evil.example.com"})).status_code == 403
    assert (await client.post("/api/prospecting/catalog/import", json=data, headers={"X-EBT-Action": ""})).status_code == 403
    response = await client.post("/api/prospecting/catalog/import", json=data)
    assert response.status_code == 200
    assert response.json()["accepted"] == 1


async def test_client_cannot_choose_workspace_and_invalid_json_is_422(api):
    client, s, cfg = api
    response = await client.post("/api/prospecting/catalog/import", json={"space": "B", "source": SOURCE, "rows": [ROW]})
    assert response.status_code == 422
    assert (await client.post("/api/prospecting/recipes", json={"name": "T", "batch_size": -1})).status_code == 422


async def test_full_contact_template_queue_flow(api):
    client, s, cfg = api
    await client.post("/api/prospecting/catalog/import", json={"source": SOURCE, "rows": [ROW]})
    r = await client.post("/api/prospecting/recipes", json={"name": "TI", "uf": "SP", "city": "São Paulo", "cnae": "620"})
    assert r.status_code == 200
    await s.tick()
    contacts = (await client.get("/api/prospecting/contacts")).json()["items"]
    assert len(contacts) == 1
    contact = contacts[0]
    p = await client.post(f'/api/prospecting/contacts/{contact["id"]}/preview', json={"template_id": "presentation", "sender": "Erick"})
    assert p.status_code == 200
    assert p.json()["recipient"] == "comercial@example.com"
    assert (await client.get(f'/api/prospecting/contacts/{contact["id"]}/history')).status_code == 200
    assert (await client.get("/api/prospecting/contacts/does-not-exist")).status_code == 404


async def test_outlook_requires_configuration_and_send_disabled_by_default(api):
    client, s, cfg = api
    response = await client.get("/api/prospecting/outlook/status")
    assert response.json()["configured"] is False
    assert response.json()["send_enabled"] is False
    assert (await client.post("/api/prospecting/outlook/connect")).status_code == 503


async def test_whatsapp_signature_mandatory(api):
    client, s, cfg = api
    response = await client.post("/api/prospecting/whatsapp/webhook", json={"entry": []})
    assert response.status_code == 403


async def test_manual_whatsapp_freezes_template_without_claiming_send(api):
    client, s, cfg = api
    c = await s.add_contact("A", "user-a", ROW, SOURCE)
    path = f'/api/prospecting/contacts/{c["id"]}'
    p = (await client.post(path+"/preview", json={"template_id": "whatsapp_intro", "sender": "Erick"})).json()
    payload = {"template_id": "whatsapp_intro", "sender": "Erick", "digest": p["digest"]}
    result = await client.post(path+"/whatsapp-manual", json=payload)
    assert result.status_code == 200
    assert result.json()["status"] == "manual_prepared"
    assert result.json()["url"].startswith("https://wa.me/")
    events = (await client.get(path+"/history")).json()["items"]
    event = events[0]
    assert event["body"] == p["body"]
    assert event["recipient"] == c["phone"]
    assert event["kind"] == "whatsapp_manual_prepared"
    assert await s.db.ebt_p_messages.count_documents({}) == 0
    exported = await client.get(path+"/history.json")
    assert exported.status_code == 200
    assert exported.json()["events"][0]["digest"] == p["digest"]
    await s.update_contact("A", c["id"], {"version": 1, "phone": "5511987654321"})
    assert (await client.post(path+"/whatsapp-manual", json=payload)).status_code == 409
    assert (await client.post(path+"/whatsapp-manual", json=payload, headers={"Origin": "https://evil.example.com"})).status_code == 403
    assert (await client.get('/api/prospecting/contacts/missing/history.json')).status_code == 404


async def test_official_whatsapp_dedupes_retries_and_exports_operation(api, monkeypatch):
    from ebt_prospecting.channels import WhatsAppCloud, ProviderOutcome
    client, s, cfg = api
    cfg.wa_send_enabled, cfg.wa_token, cfg.wa_phone_id = True, "synthetic-token", "123"
    cfg.wa_max_cost_brl, cfg.wa_template_cost_brl = 1.0, 0.0149
    c = await s.add_contact("A", "user-a", ROW, SOURCE)
    await s.update_contact("A", c["id"], {"version": 1, "status": "qualified"})
    calls = []
    async def send(self, *args):
        calls.append(args)
        return ProviderOutcome("unknown")
    monkeypatch.setattr(WhatsAppCloud, "template", send)
    payload = {"operation_id": "synthetic-operation-1", "name": "approved_template", "language": "pt_BR", "parameters": ["Ana"], "opt_in_evidence": "Consentimento sintético registrado", "confirmation_phone": c["phone"]}
    path = f'/api/prospecting/contacts/{c["id"]}/whatsapp-template'
    first = await client.post(path, json=payload)
    retry = await client.post(path, json={**payload, "operation_id": "synthetic-operation-2"})
    assert first.status_code == retry.status_code == 200
    assert retry.json()["id"] == first.json()["id"]
    assert retry.json()["status"] == "unknown"
    assert len(calls) == 1
    await s.update_contact("A", c["id"], {"version": 2, "notes": "Só uma nota; conteúdo externo igual"})
    changed_metadata = await client.post(path, json={**payload, "operation_id": "synthetic-operation-3", "opt_in_evidence": "Consentimento sintético com referência atualizada"})
    assert changed_metadata.status_code == 200
    assert changed_metadata.json()["id"] == first.json()["id"]
    assert len(calls) == 1
    assert (await client.post(path, json={**payload, "parameters": ["Outro texto"]})).status_code == 409
    record = await client.get('/api/prospecting/whatsapp/operations/synthetic-operation-1')
    assert record.json()["parameters"] == ["Ana"]
    assert (await client.get('/api/prospecting/whatsapp/outbox')).json()["items"][0]["status"] == "unknown"
    await s.db.ebt_p_wa_outbox.insert_one({"space": "B", "id": "other-workspace", "request_digest": "different"})
    assert (await client.get('/api/prospecting/whatsapp/operations/other-workspace')).status_code == 404


async def test_whatsapp_budget_reserves_ceil_cents_without_exceeding_limit(api, monkeypatch):
    from ebt_prospecting.channels import WhatsAppCloud, ProviderOutcome
    client, s, cfg = api
    cfg.wa_send_enabled, cfg.wa_token, cfg.wa_phone_id = True, "synthetic-token", "123"
    cfg.wa_max_cost_brl, cfg.wa_template_cost_brl = 0.10, 0.0149
    c = await s.add_contact("A", "user-a", ROW, SOURCE)
    await s.update_contact("A", c["id"], {"version": 1, "status": "qualified"})
    calls = []
    async def send(self, *args):
        calls.append(args)
        return ProviderOutcome("accepted", "wamid."+str(len(calls)))
    monkeypatch.setattr(WhatsAppCloud, "template", send)
    for i in range(10):
        payload = {"operation_id": "budget-operation-"+str(i), "name": "approved_template", "parameters": [str(i)], "opt_in_evidence": "Consentimento sintético registrado", "confirmation_phone": c["phone"]}
        response = await client.post(f'/api/prospecting/contacts/{c["id"]}/whatsapp-template', json=payload)
        assert response.status_code == (200 if i < 5 else 409)
    assert len(calls) == 5
    assert (await s.db.ebt_p_wa_budget.find_one({"space": "A"}))["reserved_cents"] == 10


async def test_whatsapp_webhook_before_send_response_is_reconciled(api, monkeypatch):
    import json, hashlib, hmac
    from ebt_prospecting.channels import WhatsAppCloud, ProviderOutcome
    client, s, cfg = api
    cfg.wa_send_enabled, cfg.wa_token, cfg.wa_phone_id, cfg.wa_app_secret = True, "synthetic-token", "123", "synthetic-secret"
    cfg.wa_max_cost_brl, cfg.wa_template_cost_brl = 1.0, 0.09
    c = await s.add_contact("A", "user-a", ROW, SOURCE)
    await s.update_contact("A", c["id"], {"version": 1, "status": "qualified"})
    data = {"entry": [{"changes": [{"value": {"metadata": {"phone_number_id": "123"}, "statuses": [{"id": "wamid.early", "status": "delivered", "timestamp": "1791400000", "recipient_id": c["phone"]}]}}]}]}
    body = json.dumps(data).encode()
    sig = "sha256="+hmac.new(b"synthetic-secret", body, hashlib.sha256).hexdigest()
    async def send(self, *args):
        assert (await client.post('/api/prospecting/whatsapp/webhook', content=body, headers={"X-Hub-Signature-256": sig})).status_code == 200
        return ProviderOutcome("accepted", "wamid.early")
    monkeypatch.setattr(WhatsAppCloud, "template", send)
    response = await client.post(f'/api/prospecting/contacts/{c["id"]}/whatsapp-template', json={"operation_id": "early-operation-1", "name": "approved_template", "opt_in_evidence": "Consentimento sintético registrado", "confirmation_phone": c["phone"]})
    assert response.status_code == 200
    record = (await client.get('/api/prospecting/whatsapp/operations/early-operation-1')).json()
    assert record["evidence"]["delivered"]["provider_timestamp"] == "1791400000"
    await s.db.ebt_p_wa_outbox.update_one({"space": "A", "id": "early-operation-1"}, {"$unset": {"evidence": ""}})
    await client.post('/api/prospecting/whatsapp/webhook', content=body, headers={"X-Hub-Signature-256": sig})
    record = (await client.get('/api/prospecting/whatsapp/operations/early-operation-1')).json()
    assert "delivered" in record["evidence"]
    assert await s.db.ebt_p_wa_events.count_documents({"space": "A"}) == 1


async def test_resume_email_only_after_safe_pre_send_connection_failure(api):
    client, s, cfg = api
    c = await s.add_contact("A", "user-a", ROW, SOURCE)
    p = await s.prepare("A", c["id"], "presentation", "Erick")
    m = await s.approve_message("A", "user-a", c["id"], p["digest"], "presentation", "Erick", now().isoformat()+"Z", "draft")
    await s.db.ebt_p_messages.update_one({"space": "A", "id": m["id"]}, {"$set": {"status": "needs_connection"}})
    path = f'/api/prospecting/messages/{m["id"]}/resume'
    assert (await client.post(path)).status_code == 409
    cfg.ms_client_id, cfg.ms_tenant_id, cfg.ms_client_secret, cfg.sender_mailbox = "synthetic", "synthetic", "synthetic", "owner@example.com"
    assert (await client.post(path)).status_code == 200
    assert (await client.post(path)).status_code == 409
    await s.db.ebt_p_messages.update_one({"space": "A", "id": m["id"]}, {"$set": {"status": "unknown", "provider_id": "immutable-uncertain"}})
    assert (await client.post(path)).status_code == 409
    await s.db.ebt_p_messages.update_one({"space": "A", "id": m["id"]}, {"$set": {"status": "needs_connection", "provider_id": "immutable-uncertain"}})
    assert (await client.post(path)).status_code == 409
    await s.db.ebt_p_messages.update_one({"space": "A", "id": m["id"]}, {"$set": {"provider_id": ""}})
    await s.update_contact("A", c["id"], {"version": 1, "email": "outro@example.com"})
    assert (await client.post(path)).status_code == 409


async def test_whatsapp_explicit_resume_only_for_conclusive_unsent_state(api, monkeypatch):
    from ebt_prospecting.channels import WhatsAppCloud, ProviderOutcome
    client, s, cfg = api
    cfg.wa_send_enabled, cfg.wa_token, cfg.wa_phone_id = True, "synthetic-token", "123"
    cfg.wa_max_cost_brl, cfg.wa_template_cost_brl = 0.01, 0.09
    c = await s.add_contact("A", "user-a", ROW, SOURCE)
    await s.update_contact("A", c["id"], {"version": 1, "status": "qualified"})
    calls = []
    async def send(self, *args):
        calls.append(args)
        return ProviderOutcome("accepted", "wamid.resume")
    monkeypatch.setattr(WhatsAppCloud, "template", send)
    response = await client.post(f'/api/prospecting/contacts/{c["id"]}/whatsapp-template', json={"operation_id": "resume-operation-1", "name": "approved_template", "opt_in_evidence": "Consentimento sintético registrado", "confirmation_phone": c["phone"]})
    assert response.status_code == 409
    assert not calls
    cfg.wa_max_cost_brl = 1.0
    path = '/api/prospecting/whatsapp/operations/resume-operation-1/resume'
    assert (await client.post(path)).status_code == 200
    assert len(calls) == 1
    assert (await client.post(path)).status_code == 409
    await s.db.ebt_p_wa_outbox.update_one({"space": "A", "id": "resume-operation-1"}, {"$set": {"status": "unknown", "provider_id": ""}})
    assert (await client.post(path)).status_code == 409


async def test_whatsapp_oversized_parameter_rejected_before_outbox_or_provider(api):
    client, s, cfg = api
    for suffix in ("0", "1"):
        response = await client.post('/api/prospecting/contacts/synthetic/whatsapp-template', json={"operation_id": "oversized-operation-"+suffix, "name": "approved_template", "parameters": ["A"*1024+suffix], "opt_in_evidence": "Consentimento sintético registrado", "confirmation_phone": "5511999999999"})
        assert response.status_code == 422
    assert await s.db.ebt_p_wa_outbox.count_documents({}) == 0
