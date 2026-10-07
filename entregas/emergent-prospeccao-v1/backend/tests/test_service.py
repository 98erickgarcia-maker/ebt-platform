import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.service import ProspectService
from test_domain import ROW, SOURCE


@pytest.fixture
async def service():
    s = ProspectService(AsyncMongoMockClient().synthetic, monthly_limit=2)
    await s.initialize()
    return s


async def test_recipe_discovers_and_deduplicates_companies(service):
    await service.import_catalog("A", [ROW, {**ROW, "company_name": "Nome atualizado"}], SOURCE)
    recipe = await service.create_recipe("A", "user-a", {"name": "TI SP", "uf": "SP", "city": "São Paulo", "cnae": "620", "batch_size": 50, "interval_hours": 24})
    await service.tick()
    await service.queue_recipe("A", recipe["id"])
    await service.tick()
    leads = await service.list_contacts("A")
    assert len(leads) == 1
    assert leads[0]["company_name"] == "Nome atualizado"
    assert leads[0]["status"] == "review"
    assert await service.list_contacts("B") == []


async def test_two_workers_cannot_exceed_monthly_limit(service):
    await asyncio.gather(*[service.reserve("A") for _ in range(8)])
    budget = await service.budget("A")
    assert budget["processed"] == 2
    assert budget["remaining"] == 0


async def test_contact_updates_require_version_and_remain_in_own_workspace(service):
    c = await service.add_contact("A", "user-a", ROW, SOURCE)
    with pytest.raises(LookupError):
        await service.get_contact("B", c["id"])
    with pytest.raises(ValueError):
        await service.update_contact("A", c["id"], {"version": 88, "notes": "errado"})
    updated = await service.update_contact("A", c["id"], {"version": 1, "contact_name": "Ana", "email_quality": "verified", "next_action_at": "2030-01-01T12:00:00Z", "next_action": "Ligar"})
    assert updated["version"] == 2
    assert updated["next_action"] == "Ligar"
    assert await service.get_contact("A", c["id"])


async def test_suppressed_email_cannot_be_prepared_for_outreach(service):
    c = await service.add_contact("A", "user-a", ROW, SOURCE)
    await service.suppress("A", c["id"], "pedido do contato")
    with pytest.raises(ValueError):
        await service.prepare("A", c["id"], "presentation", "Erick")


async def test_approval_freezes_recipient_and_content_and_due_job_resumes(service):
    c = await service.add_contact("A", "user-a", ROW, SOURCE)
    c = await service.update_contact("A", c["id"], {"version": 1, "status": "qualified", "email_quality": "verified", "contact_name": "Ana"})
    prepared = await service.prepare("A", c["id"], "presentation", "Erick")
    due = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    msg = await service.approve_message("A", "user-a", c["id"], prepared["digest"], "presentation", "Erick", due, "draft")
    assert msg["recipient"] == "comercial@example.com"
    assert msg["status"] == "scheduled"
    assert msg["contact_version"] == 2
    assert "access_token" not in msg
    await service.update_contact("A", c["id"], {"version": 2, "email": "outro@example.com"})
    with pytest.raises(ValueError):
        await service.approve_message("A", "user-a", c["id"], prepared["digest"], "presentation", "Erick", due, "draft")


async def test_template_update_rejects_stale_version(service):
    templates = await service.templates("A")
    assert len(templates) >= 4
    first = templates[0]
    await service.save_template("A", first["id"], {**first, "body": "Olá {{company}}", "version": 1})
    with pytest.raises(ValueError):
        await service.save_template("A", first["id"], {**first, "body": "Perdido", "version": 1})


async def test_recipe_keeps_cursor_when_budget_interrupts_partial_batch(service):
    await service.import_catalog("A", [ROW, {**ROW,"cnpj":"12ABC34501DE35"}], SOURCE)
    service.monthly_limit=1
    recipe=await service.create_recipe("A","u1",{"name":"Todas","batch_size":50})
    await service.tick()
    saved=(await service.recipes("A"))[0]
    assert saved["cursor"]=="11222333000181"
    assert saved["last_result"]["budget_reached"] is True
