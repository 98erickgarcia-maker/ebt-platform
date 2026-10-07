import pytest
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.service import ProspectService
from ebt_prospecting.channels import MessageWorker, ProviderOutcome
from ebt_prospecting.domain import now
from test_domain import ROW, SOURCE


async def test_worker_cannot_use_own_mailbox_for_another_workspace():
    db=AsyncMongoMockClient().synthetic
    s=ProspectService(db)
    await s.initialize()
    contact=await s.add_contact("B","u2",ROW,SOURCE)
    preview=await s.prepare("B",contact["id"],"presentation","Erick")
    await s.approve_message("B","u2",contact["id"],preview["digest"],"presentation","Erick",now().isoformat()+"Z","draft")
    class Provider:
        calls=0
        async def execute(self,message):
            self.calls+=1
            return ProviderOutcome("draft_created")
    provider=Provider()
    worker=MessageWorker(s,provider,space="A")
    await worker.tick()
    assert provider.calls==0
    assert (await s.messages("B"))[0]["status"]=="scheduled"
