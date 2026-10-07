import pytest
import httpx
from fastapi import FastAPI, Request, HTTPException
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.service import ProspectService
from ebt_prospecting.router import create_router
from ebt_prospecting.config import Config
from ebt_prospecting.outlook import OutlookConnector
from test_domain import ROW, SOURCE


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
