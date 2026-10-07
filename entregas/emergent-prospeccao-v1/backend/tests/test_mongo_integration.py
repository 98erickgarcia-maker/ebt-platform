import os
import uuid
import asyncio
import pytest
from pymongo import AsyncMongoClient
from ebt_prospecting.service import ProspectService
from test_domain import ROW, SOURCE
import httpx
from fastapi import FastAPI
from ebt_prospecting.router import create_router
from ebt_prospecting.config import Config
from ebt_prospecting.outlook import OutlookConnector
from ebt_prospecting.channels import WhatsAppCloud, ProviderOutcome


@pytest.mark.skipif(not os.getenv("EP_TEST_MONGO_URL"), reason="MongoDB real não configurado neste ambiente; CI inclui serviço isolado")
async def test_real_mongo_concurrent_limits_dedupe_and_restart():
    client=AsyncMongoClient(os.environ["EP_TEST_MONGO_URL"],serverSelectionTimeoutMS=5000)
    database_name="ep_synthetic_test_"+uuid.uuid4().hex
    db=client[database_name]
    try:
        s=ProspectService(db,monthly_limit=2)
        await s.initialize()
        await s.import_catalog("A",[ROW,{**ROW,"cnpj":"12ABC34501DE35"}],SOURCE)
        await s.create_recipe("A","u1",{"name":"Todas","batch_size":50})
        await asyncio.gather(s.tick(),ProspectService(db,monthly_limit=2).tick())
        assert len(await s.list_contacts("A"))==2
        assert not await s.list_contacts("B")
        assert (await s.budget("A"))["processed"]==2
        assert not await s.reserve("A")
        restarted=ProspectService(db,monthly_limit=2)
        assert len(await restarted.list_contacts("A"))==2
    finally:
        # Nome sintético criado por este teste; nunca usa DB_NAME de produção.
        assert database_name.startswith("ep_synthetic_test_")
        await client.drop_database(database_name)
        await client.close()


@pytest.mark.skipif(not os.getenv("EP_TEST_MONGO_URL"), reason="MongoDB real não configurado; CI inclui serviço isolado")
async def test_real_mongo_whatsapp_concurrent_approval_dedupe_and_cost(monkeypatch):
    client = AsyncMongoClient(os.environ["EP_TEST_MONGO_URL"], serverSelectionTimeoutMS=5000)
    database_name = "ep_synthetic_test_"+uuid.uuid4().hex
    db = client[database_name]
    try:
        service = ProspectService(db)
        await service.initialize()
        c = await service.add_contact("A", "u1", ROW, SOURCE)
        await service.update_contact("A", c["id"], {"version": 1, "status": "qualified"})
        cfg = Config(owner_email="owner@example.com", workspace="A", origins=["https://test.example.com"], wa_send_enabled=True, wa_token="synthetic-token", wa_phone_id="123", wa_max_cost_brl=0.10, wa_template_cost_brl=0.0149)
        calls = []
        async def send(self, *args):
            calls.append(args)
            number = len(calls)
            await asyncio.sleep(0.01)
            return ProviderOutcome("accepted", "wamid.synthetic."+str(number))
        monkeypatch.setattr(WhatsAppCloud, "template", send)
        async def current():
            return {"role": "owner", "email": "owner@example.com", "user_id": "u1"}
        app = FastAPI()
        app.include_router(create_router(service, cfg, current, OutlookConnector(db, cfg)))
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://test.example.com", headers={"Origin": "https://test.example.com", "X-EBT-Action": "prospecting"}) as http:
            path = f'/api/prospecting/contacts/{c["id"]}/whatsapp-template'
            payload = {"name": "approved_template", "parameters": ["Ana"], "confirmation_phone": c["phone"], "opt_in_evidence": "Consentimento sintético registrado"}
            responses = await asyncio.gather(*[http.post(path, json={**payload, "operation_id": "duplicate-operation-"+str(i)}) for i in range(8)])
            assert all(r.status_code == 200 for r in responses)
            assert len({r.json()["id"] for r in responses}) == 1
            assert len(calls) == 1
            responses = await asyncio.gather(*[http.post(path, json={**payload, "operation_id": "new-operation-"+str(i), "parameters": [str(i)]}) for i in range(10)])
            assert sum(r.status_code == 200 for r in responses) == 4
            assert all(r.status_code in {200, 409} for r in responses)
            assert len(calls) == 5
            assert (await db.ebt_p_wa_budget.find_one({"space": "A"}))["reserved_cents"] == 10
    finally:
        assert database_name.startswith("ep_synthetic_test_")
        await client.drop_database(database_name)
        await client.close()
