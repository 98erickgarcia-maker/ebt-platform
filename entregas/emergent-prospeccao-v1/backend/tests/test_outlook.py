import json
from datetime import timedelta
import httpx
import pytest
from cryptography.fernet import Fernet
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.config import Config
from ebt_prospecting.outlook import OutlookConnector
from ebt_prospecting.domain import now


class SyntheticMsal:
    def __init__(self, cache):
        self.cache=cache

    def initiate_auth_code_flow(self, scopes, **kwargs):
        return {"state": "synthetic-state", "auth_uri": "https://login.microsoftonline.com/test/authorize", "code_verifier": "private-verifier"}

    def acquire_token_by_auth_code_flow(self, flow, params):
        return {"access_token": "synthetic-access-token"}

    def get_accounts(self, **kwargs):
        return [{"username": "owner@example.com"}]

    def acquire_token_silent(self, scopes, **kwargs):
        return {"access_token": "synthetic-access-token"}


def config():
    return Config(owner_email="owner@example.com", workspace="A", origins=["https://test.example.com"], ms_client_id="synthetic-client", ms_tenant_id="synthetic-tenant", ms_client_secret="synthetic-secret", ms_redirect_uri="https://test.example.com/api/prospecting/outlook/callback", token_key=Fernet.generate_key().decode(), send_enabled=True, outlook_mode="delegated")


async def test_oauth_state_is_bound_to_user_and_browser_and_consumed_once():
    db=AsyncMongoMockClient().synthetic
    cfg=config()
    o=OutlookConnector(db,cfg,app_factory=SyntheticMsal,transport=httpx.MockTransport(lambda r:httpx.Response(200,json={"id":"account-1","mail":"owner@example.com"})))
    await o.begin("A","u1","browser-one")
    flow=await db.ebt_p_oauth.find_one({"state":"synthetic-state"})
    assert "private-verifier" not in flow["flow"]
    with pytest.raises(ValueError):
        await o.callback({"state":"synthetic-state","code":"synthetic-code"},"u1","A","browser-two","owner@example.com")
    assert not (await o.status("A","u1"))["connected"]
    await o.callback({"state":"synthetic-state","code":"synthetic-code"},"u1","A","browser-one","owner@example.com")
    assert (await o.status("A","u1"))["connected"]
    with pytest.raises(ValueError):
        await o.callback({"state":"synthetic-state","code":"synthetic-code"},"u1","A","browser-one","owner@example.com")
    assert not (await o.status("B","u1"))["connected"]


async def test_email_send_keeps_id_and_reconciles_sent_items_evidence():
    db=AsyncMongoMockClient().synthetic
    cfg=config()
    requests=[]
    def handler(request):
        requests.append(request)
        if request.method=="GET":
            return httpx.Response(200,json={"id":"immutable-1","isDraft":False,"sentDateTime":"2026-10-07T12:00:00Z","internetMessageId":"<synthetic@example.com>"})
        if request.url.path.endswith("/send"):
            return httpx.Response(202,headers={"request-id":"request-1"})
        return httpx.Response(201,json={"id":"immutable-1","webLink":"https://outlook.office.com/mail/id/immutable-1"})
    o=OutlookConnector(db,cfg,app_factory=SyntheticMsal,transport=httpx.MockTransport(handler))
    await db.ebt_p_outlook.insert_one({"space":"A","user_id":"u1","email":"owner@example.com","token_cache":o.cipher().encrypt(b'{}').decode()})
    message={"id":"message-1","space":"A","user_id":"u1","mode":"send","recipient":"recipient@example.com","subject":"Teste","body":"Apresentação"}
    await db.ebt_p_messages.insert_one({**message,"status":"executing"})
    result=await o.execute(message)
    assert result.status=="accepted"
    assert result.provider_id=="immutable-1"
    assert requests[0].headers["Prefer"]=='IdType="ImmutableId"'
    assert requests[1].url.path.endswith("/messages/immutable-1/send")
    evidence=await o.check_sent(message,"immutable-1")
    assert evidence["status"]=="sent_confirmed"
    assert evidence["internet_message_id"]=="<synthetic@example.com>"
    assert "delivered" not in evidence


async def test_application_mode_connects_automatically_with_existing_dispatcher_settings():
    db=AsyncMongoMockClient().synthetic
    cfg=config()
    cfg.outlook_mode="application"
    await db.settings.insert_one({"id":"settings","sender_mailbox":"owner@example.com"})
    calls=[]
    class AppMsal(SyntheticMsal):
        def acquire_token_for_client(self, scopes):
            assert scopes == ["https://graph.microsoft.com/.default"]
            return {"access_token":"synthetic-app-token"}
    def handler(request):
        calls.append(request)
        return httpx.Response(201,json={"id":"app-draft-1","webLink":"https://outlook.office.com/mail/id/app-draft-1"})
    o=OutlookConnector(db,cfg,app_factory=AppMsal,transport=httpx.MockTransport(handler))
    status=await o.status("A","u1")
    assert status["automatic"] is True
    assert status["configured"] is True
    assert status["email"] == "owner@example.com"
    message={"id":"app-message-1","space":"A","user_id":"u1","mode":"draft","recipient":"recipient@example.com","subject":"Teste","body":"Apresentação"}
    result=await o.execute(message)
    assert result.status == "draft_created"
    assert calls[0].url.path == "/v1.0/users/owner@example.com/messages"
