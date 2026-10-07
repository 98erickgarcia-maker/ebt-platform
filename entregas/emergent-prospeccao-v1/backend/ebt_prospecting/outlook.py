import asyncio
import hashlib
import json
import secrets
from datetime import timedelta
from urllib.parse import urlparse, quote
import httpx
import msal
from cryptography.fernet import Fernet
from pymongo import ReturnDocument
from .channels import ProviderOutcome
from .domain import now


class OutlookConnector:
    def __init__(self, db, cfg, transport=None, app_factory=None):
        self.db, self.cfg, self.transport = db, cfg, transport
        self.app_factory = app_factory
        self.application_app = None
        self.application_lock = asyncio.Lock()

    @property
    def scopes(self):
        return ["User.Read", "Mail.ReadWrite"] + (["Mail.Send"] if self.cfg.send_enabled else [])

    def cipher(self):
        return Fernet(self.cfg.token_key.encode())

    def app(self, cache=None):
        if self.app_factory:
            return self.app_factory(cache)
        return msal.ConfidentialClientApplication(self.cfg.ms_client_id, authority=f"https://login.microsoftonline.com/{self.cfg.ms_tenant_id}", client_credential=self.cfg.ms_client_secret, token_cache=cache, timeout=15)

    async def begin(self, space, user_id, binding):
        if not self.cfg.outlook_configured or self.cfg.outlook_mode != "delegated":
            raise ValueError("Conector Outlook requer configuração Entra e chave de criptografia.")
        flow = await asyncio.to_thread(self.app().initiate_auth_code_flow, self.scopes, redirect_uri=self.cfg.ms_redirect_uri, prompt="select_account")
        await self.db.ebt_p_oauth.insert_one({"space": space, "user_id": user_id, "state": flow["state"], "binding": hashlib.sha256(binding.encode()).hexdigest(), "expires_at": now()+timedelta(minutes=10), "flow": self.cipher().encrypt(json.dumps(flow).encode()).decode()})
        return flow["auth_uri"]

    async def callback(self, parameters, user_id, space, binding, expected_email):
        state = parameters.get("state", "")
        doc = await self.db.ebt_p_oauth.find_one_and_delete({"state": state, "space": space, "user_id": user_id, "binding": hashlib.sha256(binding.encode()).hexdigest(), "expires_at": {"$gt": now()}})
        if not doc:
            raise ValueError("Autorização expirada ou iniciada em outro navegador.")
        cache = msal.SerializableTokenCache()
        flow = json.loads(self.cipher().decrypt(doc["flow"].encode()))
        result = await asyncio.to_thread(self.app(cache).acquire_token_by_auth_code_flow, flow, parameters)
        if "access_token" not in result:
            raise ValueError("A Microsoft não autorizou o conector.")
        async with httpx.AsyncClient(transport=self.transport, timeout=20, follow_redirects=False) as client:
            profile = await client.get("https://graph.microsoft.com/v1.0/me?$select=id,mail,userPrincipalName,displayName", headers={"Authorization": "Bearer " + result["access_token"]})
        if profile.status_code != 200:
            raise ValueError("Não foi possível confirmar a conta Microsoft.")
        p = profile.json()
        email = (p.get("mail") or p.get("userPrincipalName") or "").lower()
        if email != expected_email.lower():
            raise ValueError("Conecte a mesma conta autenticada no aplicativo.")
        await self.db.ebt_p_outlook.update_one({"space": space, "user_id": user_id}, {"$set": {"email": email, "account_id": p["id"], "connected_at": now(), "token_cache": self.cipher().encrypt(cache.serialize().encode()).decode()}}, upsert=True)
        await self.db.ebt_p_messages.update_many({"space": space, "user_id": user_id, "status": "needs_connection"}, {"$set": {"status": "scheduled", "due_at": now()}})

    async def status(self, space, user_id):
        if self.cfg.outlook_mode == "application":
            mailbox = await self.mailbox()
            checked = await self.db.ebt_p_outlook_health.find_one({"space": space, "mailbox": mailbox}) or {}
            return {"configured": bool(self.cfg.outlook_configured and mailbox), "connected": checked.get("last_success") is not None, "automatic": True, "email": mailbox or None, "send_enabled": self.cfg.send_enabled, "daily_email_limit": self.cfg.daily_email_limit, "last_api_success": checked.get("last_success")}
        doc = await self.db.ebt_p_outlook.find_one({"space": space, "user_id": user_id})
        return {"configured": self.cfg.outlook_configured, "connected": bool(doc), "automatic": False, "email": doc.get("email") if doc else None, "send_enabled": self.cfg.send_enabled, "daily_email_limit": self.cfg.daily_email_limit}

    async def mailbox(self):
        if self.cfg.sender_mailbox:
            return self.cfg.sender_mailbox.strip().lower()
        settings = await self.db.settings.find_one({"id": "settings"}) or {}
        return str(settings.get("sender_mailbox", "")).strip().lower()

    async def disconnect(self, space, user_id):
        await self.db.ebt_p_outlook.delete_one({"space": space, "user_id": user_id})
        return {"ok": True}

    async def execute(self, message):
        if message["mode"] == "send" and not self.cfg.send_enabled:
            return ProviderOutcome("disabled")
        if self.cfg.outlook_mode == "application":
            mailbox = await self.mailbox()
            if not self.cfg.outlook_configured or not mailbox:
                return ProviderOutcome("needs_connection")
            async with self.application_lock:
                if not self.application_app:
                    self.application_app = await asyncio.to_thread(self.app)
                result = await asyncio.to_thread(self.application_app.acquire_token_for_client, scopes=["https://graph.microsoft.com/.default"])
            if not result or "access_token" not in result:
                return ProviderOutcome("needs_connection")
            outcome = await self.graph_action(message, result["access_token"], "https://graph.microsoft.com/v1.0/users/"+quote(mailbox,safe="")+"/messages")
            if outcome.status in {"draft_created", "accepted", "sent_confirmed"}:
                await self.db.ebt_p_outlook_health.update_one({"space": message["space"], "mailbox": mailbox}, {"$set": {"last_success": now()}}, upsert=True)
            return outcome
        space, user_id = message["space"], message["user_id"]
        lease = secrets.token_hex(16)
        token_doc = await self.db.ebt_p_outlook.find_one_and_update({"space": space, "user_id": user_id, "$or": [{"lease_until": {"$exists": False}}, {"lease_until": {"$lte": now()}}]}, {"$set": {"lease": lease, "lease_until": now()+timedelta(minutes=2)}}, return_document=ReturnDocument.AFTER)
        if not token_doc:
            exists = await self.db.ebt_p_outlook.find_one({"space": space, "user_id": user_id})
            return ProviderOutcome("deferred", retry_after=120) if exists else ProviderOutcome("needs_connection")
        try:
            cache = msal.SerializableTokenCache()
            cache.deserialize(self.cipher().decrypt(token_doc["token_cache"].encode()).decode())
            app = self.app(cache)
            accounts = app.get_accounts(username=token_doc["email"])
            result = await asyncio.to_thread(app.acquire_token_silent, self.scopes, account=accounts[0] if accounts else None)
            if not result or "access_token" not in result:
                return ProviderOutcome("needs_connection")
            await self.db.ebt_p_outlook.update_one({"space": space, "user_id": user_id, "lease": lease}, {"$set": {"token_cache": self.cipher().encrypt(cache.serialize().encode()).decode()}})
            return await self.graph_action(message, result["access_token"], "https://graph.microsoft.com/v1.0/me/messages")
        finally:
            await self.db.ebt_p_outlook.update_one({"space": space, "user_id": user_id, "lease": lease}, {"$unset": {"lease": "", "lease_until": ""}})

    async def graph_action(self, message, token, endpoint):
        mail = {"subject": message["subject"], "body": {"contentType": "Text", "content": message["body"]}, "toRecipients": [{"emailAddress": {"address": message["recipient"]}}], "internetMessageHeaders": [{"name": "x-ebt-operation", "value": message["id"]}]}
        mode = message["mode"]
        headers = {"Authorization": "Bearer " + token, "Prefer": 'IdType="ImmutableId"'}
        async with httpx.AsyncClient(transport=self.transport, timeout=30, follow_redirects=False) as client:
            try:
                if mode == "evidence":
                    response = await client.get(endpoint+"/"+quote(message["provider_id"],safe="")+"?$select=id,isDraft,sentDateTime,internetMessageId,webLink", headers=headers)
                    if response.status_code != 200:
                        return ProviderOutcome("pending")
                    data = response.json()
                    if data.get("isDraft") is False and data.get("sentDateTime") and not data["sentDateTime"].startswith("0001-") and data.get("internetMessageId"):
                        return ProviderOutcome("sent_confirmed", message["provider_id"], evidence={"status": "sent_confirmed", "sent_at": data["sentDateTime"], "internet_message_id": data["internetMessageId"], "checked_at": now().isoformat()+"Z"})
                    return ProviderOutcome("pending")
                response = await client.post(endpoint, headers=headers, json=mail)
                if mode == "send" and response.status_code == 201:
                    draft = response.json()
                    await self.db.ebt_p_messages.update_one({"space": message["space"], "id": message["id"]}, {"$set": {"provider_id": draft["id"], "draft_created_at": now()}})
                    sent = await client.post(endpoint+"/"+quote(draft["id"],safe="")+"/send", headers=headers)
                    if sent.status_code == 202:
                        return ProviderOutcome("accepted", draft["id"], draft.get("webLink", ""), evidence={"accepted_http_status": 202, "request_id": sent.headers.get("request-id", ""), "accepted_at": now().isoformat()+"Z"})
                    # Um rascunho já existe. Não repetir automaticamente a criação.
                    return ProviderOutcome("unknown" if sent.status_code >= 500 or sent.status_code == 429 else "rejected", draft["id"], draft.get("webLink", ""))
            except httpx.TransportError:
                return ProviderOutcome("unknown")
        if response.status_code == 429:
            retry = response.headers.get("Retry-After", "120")
            return ProviderOutcome("deferred", retry_after=int(retry) if retry.isdigit() else 120)
        if response.status_code == 401:
            return ProviderOutcome("needs_connection")
        if response.status_code >= 500:
            return ProviderOutcome("unknown")
        if mode == "draft" and response.status_code == 201:
            data = response.json()
            link = data.get("webLink", "")
            u = urlparse(link)
            if u.scheme != "https" or u.hostname not in {"outlook.office.com", "outlook.office365.com", "outlook.live.com"}:
                link = ""
            return ProviderOutcome("draft_created", data["id"], link)
        return ProviderOutcome("rejected")

    async def check_sent(self, message, provider_id):
        outcome = await self.execute({**message, "mode": "evidence", "provider_id": provider_id})
        return outcome.evidence or {"status": "pending"}
