from dataclasses import dataclass, field
import hashlib
import hmac
import re
from datetime import timedelta
import httpx
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from .domain import now, safe_url


@dataclass
class ProviderOutcome:
    status: str
    provider_id: str = ""
    web_link: str = ""
    retry_after: int = 0
    evidence: dict = field(default_factory=dict)


class MessageWorker:
    def __init__(self, service, provider, send_enabled=False, daily_limit=20, space=None):
        self.service = service
        self.provider = provider
        self.send_enabled = send_enabled
        self.daily_limit = daily_limit
        self.space = space

    async def tick(self):
        db = self.service.db
        own = {"space": self.space} if self.space else {}
        await db.ebt_p_messages.update_many({**own, "status": "executing", "claimed_at": {"$lt": now()-timedelta(minutes=10)}}, {"$set": {"status": "unknown", "error": "Execução interrompida. Confira o provedor antes de preparar outra mensagem."}})
        query = {"status": "scheduled", "due_at": {"$lte": now()}}
        query.update(own)
        if not self.send_enabled:
            query["mode"] = "draft"
        message = await db.ebt_p_messages.find_one_and_update(query, {"$set": {"status": "executing", "claimed_at": now()}, "$inc": {"attempts": 1}}, return_document=ReturnDocument.AFTER)
        if not message:
            return False
        status, outcome, error = "unknown", ProviderOutcome("unknown"), ""
        try:
            contact = await self.service.get_contact(message["space"], message["contact_id"])
            if contact["version"] != message["contact_version"] or contact["status"] in {"suppressed", "discarded"} or contact["email"] != message["recipient"]:
                status, error = "needs_review", "Contato alterado ou bloqueado depois da aprovação."
            elif message["mode"] == "send" and not await self._reserve_email(message["space"]):
                status, error = "limit_reached", "Limite diário de e-mail atingido; revisão necessária."
            else:
                # O serviço legado pode conter bloqueios por endereço ou domínio.
                legacy = await db.suppression.find_one({"value": {"$in": [message["recipient"], message["recipient"].split("@")[-1]]}})
                if legacy:
                    status, error = "cancelled", "Endereço ou domínio na lista de supressão existente."
                else:
                    outcome = await self.provider.execute(message)
                    status = outcome.status
        except Exception:
            error = "Resultado não confirmado. Verifique o Outlook antes de repetir."
        update = {"status": status, "finished_at": now(), "error": error}
        # Um ID salvo antes de /send precisa sobreviver a timeout/exceção.
        if outcome.provider_id:
            update["provider_id"] = outcome.provider_id
        if outcome.web_link:
            update["web_link"] = safe_url(outcome.web_link)
        if outcome.evidence:
            update["evidence"] = outcome.evidence
        if status == "accepted":
            update.update(accepted_at=now(), evidence_attempts=0, evidence_check_until=now())
        if status == "deferred" and message["attempts"] < 3:
            update.update(status="scheduled", due_at=now()+timedelta(seconds=max(60, min(outcome.retry_after, 3600))))
        await db.ebt_p_messages.update_one({"space": message["space"], "id": message["id"], "status": "executing"}, {"$set": update})
        await self.service.event(message["space"], message["contact_id"], status, error or ("Rascunho confirmado no Outlook." if status == "draft_created" else "Solicitação aceita pelo provedor; entrega não confirmada." if status == "accepted" else "Resultado: " + status))
        return True

    async def reconcile(self):
        own = {"space": self.space} if self.space else {}
        message = await self.service.db.ebt_p_messages.find_one_and_update({**own, "status": "accepted", "provider_id": {"$ne": ""}, "accepted_at": {"$lte": now()-timedelta(seconds=30)}, "evidence_attempts": {"$lt": 5}, "evidence_check_until": {"$lte": now()}}, {"$inc": {"evidence_attempts": 1}, "$set": {"evidence_check_until": now()+timedelta(minutes=2)}}, return_document=ReturnDocument.AFTER)
        if not message:
            return False
        evidence = await self.provider.check_sent(message, message["provider_id"])
        if evidence.get("status") == "sent_confirmed":
            await self.service.db.ebt_p_messages.update_one({"space": message["space"], "id": message["id"], "status": "accepted"}, {"$set": {"status": "sent_confirmed", "sent_evidence": evidence, "sent_items_confirmed_at": now()}})
            await self.service.event(message["space"], message["contact_id"], "sent_confirmed", "Outlook confirmou a mensagem fora dos rascunhos, com data de envio e identificador. Entrega não confirmada.")
        return True

    async def _reserve_email(self, space):
        db = self.service.db
        key = {"space": space, "day": now().date().isoformat()}
        await db.ebt_p_email_budget.create_index([("space", 1), ("day", 1)], unique=True)
        try:
            await db.ebt_p_email_budget.update_one(key, {"$setOnInsert": {"attempted": 0}}, upsert=True)
        except DuplicateKeyError:
            pass
        return bool(await db.ebt_p_email_budget.find_one_and_update({**key, "attempted": {"$lt": self.daily_limit}}, {"$inc": {"attempted": 1}}))


class WhatsAppCloud:
    def __init__(self, base, phone_id, token, transport=None):
        self.base, self.phone_id, self.token, self.transport = base, phone_id, token, transport

    @staticmethod
    def valid_signature(body, signature, secret):
        if not secret or not signature:
            return False
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

    async def template(self, phone, name, language, parameters):
        if not re.fullmatch(r"\d{10,15}", phone) or not re.fullmatch(r"[a-z0-9_]{1,512}", name) or not re.fullmatch(r"[a-z]{2}(?:_[A-Z]{2})?", language) or not re.fullmatch(r"\d+", self.phone_id):
            raise ValueError("Número ou template inválido.")
        if not self.base.startswith("https://graph.facebook.com/v"):
            raise ValueError("Use o endpoint oficial da Meta.")
        if len(parameters) > 20 or any(not isinstance(p, str) or len(p) > 1024 for p in parameters):
            raise ValueError("Parâmetros devem preservar exatamente o texto aprovado e ter até 1024 caracteres.")
        payload = {"messaging_product": "whatsapp", "to": phone, "type": "template", "template": {"name": name, "language": {"code": language}}}
        if parameters:
            payload["template"]["components"] = [{"type": "body", "parameters": [{"type": "text", "text": p} for p in parameters]}]
        async with httpx.AsyncClient(transport=self.transport, timeout=20, follow_redirects=False) as client:
            try:
                response = await client.post(f"{self.base}/{self.phone_id}/messages", headers={"Authorization": f"Bearer {self.token}"}, json=payload)
            except httpx.TransportError:
                return ProviderOutcome("unknown")
        if response.status_code == 429:
            retry = response.headers.get("Retry-After", "120")
            return ProviderOutcome("deferred", retry_after=int(retry) if retry.isdigit() else 120)
        if response.status_code >= 500:
            return ProviderOutcome("unknown")
        if response.status_code not in {200, 201}:
            return ProviderOutcome("rejected")
        messages = response.json().get("messages", [])
        return ProviderOutcome("accepted", messages[0]["id"]) if messages else ProviderOutcome("unknown")
