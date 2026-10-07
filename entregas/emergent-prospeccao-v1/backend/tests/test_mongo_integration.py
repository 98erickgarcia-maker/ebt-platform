import os
import uuid
import asyncio
import pytest
from pymongo import AsyncMongoClient
from ebt_prospecting.service import ProspectService
from test_domain import ROW, SOURCE


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
