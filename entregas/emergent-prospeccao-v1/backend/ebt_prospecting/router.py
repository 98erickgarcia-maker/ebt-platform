import csv
import hashlib
import io
import json
import re
import secrets
from datetime import datetime
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import DuplicateKeyError
from .channels import WhatsAppCloud
from .domain import digest, now, direct_links
from .service import public


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=8, max_length=500)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class CatalogImport(StrictModel):
    source: Source
    rows: list[dict] = Field(min_length=1, max_length=1000)


class Recipe(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    uf: str = Field(default="", pattern=r"^(?:[A-Z]{2})?$")
    city: str = Field(default="", max_length=200)
    cnae: str = Field(default="", pattern=r"^\d{0,7}$")
    batch_size: int = Field(default=25, ge=1, le=100)
    interval_hours: int = Field(default=24, ge=1, le=720)


class ContactUpdate(StrictModel):
    version: int = Field(ge=1)
    contact_name: str | None = Field(default=None, max_length=200)
    contact_role: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=254)
    email_quality: Literal["verified", "unverified", "missing", "invalid"] | None = None
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=500)
    linkedin: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=4000)
    next_action: str | None = Field(default=None, max_length=200)
    next_action_at: str | None = Field(default=None, max_length=50)
    status: Literal["review", "qualified", "customer", "discarded", "suppressed"] | None = None


class Preview(StrictModel):
    template_id: str = Field(min_length=1, max_length=100)
    sender: str = Field(min_length=1, max_length=200)


class Schedule(Preview):
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    due_at: str = Field(min_length=10, max_length=50)
    mode: Literal["draft", "send"] = "draft"


class ManualWhatsApp(Preview):
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class TemplateUpdate(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    subject: str = Field(max_length=200)
    body: str = Field(min_length=1, max_length=8000)
    version: int = Field(ge=1)


class Reason(StrictModel):
    reason: str = Field(min_length=1, max_length=1000)


class WhatsappRequest(StrictModel):
    name: str = Field(pattern=r"^[a-z0-9_]{1,512}$")
    language: str = Field(default="pt_BR", pattern=r"^[a-z]{2}(?:_[A-Z]{2})?$")
    parameters: list[Annotated[str, Field(max_length=1024)]] = Field(default_factory=list, max_length=20)
    opt_in_evidence: str = Field(min_length=10, max_length=1000)
    confirmation_phone: str = Field(pattern=r"^\d{10,15}$")
    operation_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{10,80}$")


def create_router(service, cfg, get_current_user, outlook):
    cfg.validate()
    router = APIRouter(prefix="/api/prospecting", tags=["Prospecção EBT"])

    async def principal(user=Depends(get_current_user)):
        if user.get("role") != "owner" or user.get("email", "").lower() != cfg.owner_email or not user.get("user_id"):
            raise HTTPException(403, "Área exclusiva do proprietário autorizado.")
        return {"space": cfg.workspace, "user_id": user["user_id"], "email": user["email"]}

    async def mutation(request: Request, p=Depends(principal)):
        if request.headers.get("Origin") not in cfg.origins or request.headers.get("X-EBT-Action") != "prospecting":
            raise HTTPException(403, "Origem ou confirmação da ação inválida.")
        return p

    async def attempt(coroutine):
        try:
            return await coroutine
        except LookupError as e:
            raise HTTPException(404, str(e))
        except ValueError as e:
            raise HTTPException(409, str(e))

    @router.get("/summary")
    async def summary(p=Depends(principal)):
        return await service.summary(p["space"])

    @router.post("/catalog/import")
    async def catalog(payload: CatalogImport, p=Depends(mutation)):
        if len(json.dumps(payload.model_dump()).encode()) > 5_000_000:
            raise HTTPException(413, "Lote maior que 5MB.")
        return await attempt(service.import_catalog(p["space"], payload.rows, payload.source.model_dump()))

    @router.get("/recipes")
    async def recipes(p=Depends(principal)):
        return {"items": await service.recipes(p["space"])}

    @router.post("/recipes")
    async def create_recipe(payload: Recipe, p=Depends(mutation)):
        return await attempt(service.create_recipe(p["space"], p["user_id"], payload.model_dump()))

    @router.post("/recipes/{recipe_id}/run")
    async def run_recipe(recipe_id: str, p=Depends(mutation)):
        return await attempt(service.queue_recipe(p["space"], recipe_id))

    @router.post("/recipes/{recipe_id}/pause")
    async def pause_recipe(recipe_id: str, p=Depends(mutation)):
        return await attempt(service.queue_recipe(p["space"], recipe_id, False))

    @router.get("/contacts")
    async def contacts(search: str = Query("", max_length=100), status: str = "", skip: int = Query(0, ge=0, le=100000), limit: int = Query(50, ge=1, le=100), p=Depends(principal)):
        return {"items": await service.list_contacts(p["space"], search, status, skip, limit)}

    @router.get("/contacts/export.csv")
    async def export(p=Depends(principal)):
        rows = await service.list_contacts(p["space"], limit=1000)
        out = io.StringIO()
        fields = ["id", "cnpj", "company_name", "contact_name", "email", "phone", "city", "uf", "status", "next_action"]
        writer = csv.DictWriter(out, fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            # Evitar que planilhas interpretem dados importados como fórmulas.
            writer.writerow({k: "'"+str(row.get(k, "")) if str(row.get(k, "")).startswith(("=", "+", "-", "@")) else row.get(k, "") for k in fields})
        return Response("\ufeff"+out.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="prospeccao-primeiros-1000.csv"'})

    @router.get("/contacts/{contact_id}")
    async def contact(contact_id: str, p=Depends(principal)):
        c = await attempt(service.get_contact(p["space"], contact_id))
        return {**c, "links": direct_links(c)}

    @router.patch("/contacts/{contact_id}")
    async def update_contact(contact_id: str, payload: ContactUpdate, p=Depends(mutation)):
        return await attempt(service.update_contact(p["space"], contact_id, payload.model_dump(exclude_unset=True)))

    @router.get("/contacts/{contact_id}/history")
    async def history(contact_id: str, p=Depends(principal)):
        return {"items": await attempt(service.history(p["space"], contact_id))}

    @router.get("/contacts/{contact_id}/history.json")
    async def history_export(contact_id: str, p=Depends(principal)):
        events = await attempt(service.history(p["space"], contact_id))
        data = {"contact_id": contact_id, "events": events, "exported_at": now(),
                "meaning": "Template manual preparado não confirma envio. Eventos da API oficial identificam seus próprios estados."}
        return Response(json.dumps(jsonable_encoder(data), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": 'attachment; filename="historico-contato.json"', "Cache-Control": "no-store"})

    @router.post("/contacts/{contact_id}/suppress")
    async def suppress(contact_id: str, payload: Reason, p=Depends(mutation)):
        return await attempt(service.suppress(p["space"], contact_id, payload.reason))

    @router.post("/contacts/{contact_id}/preview")
    async def preview(contact_id: str, payload: Preview, p=Depends(mutation)):
        return await attempt(service.prepare(p["space"], contact_id, payload.template_id, payload.sender))

    @router.post("/contacts/{contact_id}/whatsapp-manual")
    async def manual_whatsapp(contact_id: str, payload: ManualWhatsApp, p=Depends(mutation)):
        return await attempt(service.prepare_manual_whatsapp(p["space"], p["user_id"], contact_id, payload.digest, payload.template_id, payload.sender))

    @router.post("/contacts/{contact_id}/schedule")
    async def schedule(contact_id: str, payload: Schedule, p=Depends(mutation)):
        if payload.mode == "send" and not cfg.send_enabled:
            raise HTTPException(403, "Envio desativado na configuração do servidor.")
        return await attempt(service.approve_message(p["space"], p["user_id"], contact_id, payload.digest, payload.template_id, payload.sender, payload.due_at, payload.mode))

    @router.get("/messages")
    async def messages(contact_id: str | None = None, p=Depends(principal)):
        return {"items": await service.messages(p["space"], contact_id)}

    @router.post("/messages/{message_id}/cancel")
    async def cancel(message_id: str, p=Depends(mutation)):
        result = await service.db.ebt_p_messages.update_one({"space": p["space"], "id": message_id, "status": "scheduled"}, {"$set": {"status": "cancelled"}})
        if not result.modified_count:
            raise HTTPException(409, "A mensagem já saiu da fila ou foi cancelada.")
        return {"ok": True}

    @router.post("/messages/{message_id}/resume")
    async def resume_email(message_id: str, p=Depends(mutation)):
        ready = await outlook.status(p["space"], p["user_id"])
        if not ready.get("configured") or (not ready.get("automatic") and not ready.get("connected")):
            raise HTTPException(409, "Corrija primeiro a configuração do conector Outlook.")
        return await attempt(service.resume_email(p["space"], message_id))

    @router.get("/messages/{message_id}/evidence.json")
    async def message_evidence(message_id: str, p=Depends(principal)):
        doc = await service.db.ebt_p_messages.find_one({"space": p["space"], "id": message_id})
        if not doc:
            raise HTTPException(404, "Mensagem não encontrada.")
        evidence = {"record": public(doc), "meaning": "Aprovação, solicitação e confirmação de envio são estados separados. Este registro não confirma entrega ao destinatário.", "exported_at": now()}
        return Response(json.dumps(jsonable_encoder(evidence), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": 'attachment; filename="evidencia-email.json"', "Cache-Control": "no-store"})

    @router.get("/templates")
    async def templates(p=Depends(principal)):
        return {"items": await service.templates(p["space"])}

    @router.put("/templates/{template_id}")
    async def save_template(template_id: str, payload: TemplateUpdate, p=Depends(mutation)):
        return await attempt(service.save_template(p["space"], template_id, payload.model_dump()))

    @router.get("/outlook/status")
    async def outlook_status(p=Depends(principal)):
        return await outlook.status(p["space"], p["user_id"])

    @router.post("/outlook/connect")
    async def outlook_connect(response: Response, p=Depends(mutation)):
        if not cfg.outlook_configured:
            raise HTTPException(503, "Configure o conector Microsoft no servidor.")
        binding = secrets.token_urlsafe(32)
        url = await attempt(outlook.begin(p["space"], p["user_id"], binding))
        response.set_cookie("ebt_ms_bind", binding, httponly=True, secure=cfg.ms_redirect_uri.startswith("https://"), samesite="lax", path="/api/prospecting/outlook", max_age=600)
        return {"url": url}

    @router.get("/outlook/callback")
    async def outlook_callback(request: Request, p=Depends(principal)):
        if not cfg.outlook_configured:
            raise HTTPException(503, "Conector Microsoft indisponível.")
        await attempt(outlook.callback(dict(request.query_params), p["user_id"], p["space"], request.cookies.get("ebt_ms_bind", ""), p["email"]))
        response = RedirectResponse(cfg.origins[0]+"/?prospecting=outlook-connected", status_code=303)
        response.delete_cookie("ebt_ms_bind", path="/api/prospecting/outlook")
        return response

    @router.post("/outlook/disconnect")
    async def disconnect(p=Depends(mutation)):
        return await outlook.disconnect(p["space"], p["user_id"])

    @router.get("/whatsapp/status")
    async def wa_status(p=Depends(principal)):
        return {"configured": bool(cfg.wa_phone_id and cfg.wa_token and cfg.wa_app_secret and cfg.wa_verify_token), "send_enabled": cfg.wa_send_enabled, "phone_id": cfg.wa_phone_id, "budget_brl": cfg.wa_max_cost_brl, "configured_template_cost_brl": cfg.wa_template_cost_brl}

    @router.get("/whatsapp/webhook")
    async def wa_verify(request: Request):
        query = request.query_params
        if not cfg.wa_verify_token or query.get("hub.mode") != "subscribe" or not secrets.compare_digest(query.get("hub.verify_token", ""), cfg.wa_verify_token):
            raise HTTPException(403, "Verificação inválida.")
        return Response(query.get("hub.challenge", ""), media_type="text/plain")

    @router.post("/whatsapp/webhook")
    async def wa_webhook(request: Request):
        body = await request.body()
        if len(body) > 1_000_000:
            raise HTTPException(413, "Webhook muito grande.")
        if not WhatsAppCloud.valid_signature(body, request.headers.get("X-Hub-Signature-256", ""), cfg.wa_app_secret):
            raise HTTPException(403, "Assinatura inválida.")
        try:
            payload = json.loads(body)
        except ValueError:
            raise HTTPException(400, "JSON inválido.")
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if value.get("metadata", {}).get("phone_number_id") != cfg.wa_phone_id:
                    continue
                for event in value.get("messages", []) + value.get("statuses", []):
                    event_id = digest({"id": event.get("id"), "status": event.get("status", "inbound"), "timestamp": event.get("timestamp")})
                    try:
                        await service.db.ebt_p_wa_events.insert_one({"space": cfg.workspace, "id": event_id, "provider_id": event.get("id"), "kind": event.get("status", "inbound"), "phone": event.get("from") or event.get("recipient_id"), "text": event.get("text", {}).get("body", "")[:4000], "timestamp": event.get("timestamp"), "at": now()})
                    except DuplicateKeyError:
                        pass
                    if event.get("status") in {"sent", "delivered", "read", "failed"}:
                        await service.reconcile_whatsapp(cfg.workspace, event["id"])
        return {"ok": True}

    @router.get("/whatsapp/events")
    async def wa_events(p=Depends(principal)):
        docs = await service.db.ebt_p_wa_events.find({"space": p["space"]}).sort("at", -1).to_list(100)
        return {"items": [public(d) for d in docs]}

    @router.get("/whatsapp/outbox")
    async def wa_outbox(contact_id: str | None = None, p=Depends(principal)):
        query = {"space": p["space"]}
        if contact_id:
            query["contact_id"] = contact_id
        docs = await service.db.ebt_p_wa_outbox.find(query).sort("at", -1).to_list(100)
        return {"items": [public(d) for d in docs]}

    @router.get("/whatsapp/operations/{operation_id}")
    async def wa_operation(operation_id: str, p=Depends(principal)):
        doc = await service.db.ebt_p_wa_outbox.find_one({"space": p["space"], "id": operation_id})
        if not doc:
            raise HTTPException(404, "Operação WhatsApp não encontrada.")
        return public(doc)

    def require_whatsapp_configuration():
        if not cfg.wa_send_enabled or not cfg.wa_token or not cfg.wa_phone_id or cfg.wa_max_cost_brl <= 0 or cfg.wa_template_cost_brl <= 0:
            raise HTTPException(403, "Configure e autorize WhatsApp oficial e orçamento antes de enviar.")

    async def execute_whatsapp(doc):
        space, operation_id = doc["space"], doc["id"]
        month = now().strftime("%Y-%m")
        try:
            await service.db.ebt_p_wa_budget.update_one({"space": space, "month": month}, {"$setOnInsert": {"reserved_cents": 0}}, upsert=True)
        except DuplicateKeyError:
            pass
        cents = max(1, int((Decimal(str(cfg.wa_template_cost_brl))*100).to_integral_value(rounding=ROUND_CEILING)))
        limit = int((Decimal(str(cfg.wa_max_cost_brl))*100).to_integral_value(rounding=ROUND_FLOOR))
        reserve = await service.db.ebt_p_wa_budget.find_one_and_update({"space": space, "month": month, "reserved_cents": {"$lte": limit-cents}}, {"$inc": {"reserved_cents": cents}})
        if not reserve:
            await service.db.ebt_p_wa_outbox.update_one({"space": space, "id": operation_id}, {"$set": {"status": "limit_reached"}})
            raise HTTPException(409, "Limite de custo configurado atingido.")
        w = WhatsAppCloud("https://graph.facebook.com/"+cfg.wa_version, cfg.wa_phone_id, cfg.wa_token)
        try:
            outcome = await w.template(doc["phone"], doc["name"], doc["language"], doc["parameters"])
        except Exception:
            await service.db.ebt_p_wa_outbox.update_one({"space": space, "id": operation_id}, {"$set": {"status": "unknown"}})
            raise HTTPException(502, "Resultado não confirmado. Consulte a operação antes de solicitar outra mensagem.")
        update = {"status": outcome.status, "provider_id": outcome.provider_id}
        await service.db.ebt_p_wa_outbox.update_one({"space": space, "id": operation_id}, {"$set": update})
        await service.reconcile_whatsapp(space, outcome.provider_id)
        await service.event(space, doc["contact_id"], "whatsapp_"+outcome.status, "Template oficial solicitado; consulte o webhook para entrega.")
        return public(await service.db.ebt_p_wa_outbox.find_one({"space": space, "id": operation_id}))

    @router.post("/contacts/{contact_id}/whatsapp-template")
    async def wa_send(contact_id: str, payload: WhatsappRequest, p=Depends(mutation)):
        require_whatsapp_configuration()
        c = await attempt(service.get_contact(p["space"], contact_id))
        if c["status"] != "qualified" or c["phone"] != payload.confirmation_phone:
            raise HTTPException(409, "Confirme o telefone do contato qualificado.")
        frozen = {"contact_id": contact_id, "contact_version": c["version"], "phone": c["phone"], "sender_phone_id": cfg.wa_phone_id, "name": payload.name, "language": payload.language, "parameters": payload.parameters, "user_id": p["user_id"], "opt_in_evidence": payload.opt_in_evidence}
        request_digest = digest(frozen)
        delivery_digest = digest({key: frozen[key] for key in ("phone", "sender_phone_id", "name", "language", "parameters")})
        doc = {**frozen, "space": p["space"], "id": payload.operation_id, "request_digest": request_digest, "delivery_digest": delivery_digest, "status": "executing", "at": now()}
        try:
            await service.db.ebt_p_wa_outbox.insert_one(doc)
        except DuplicateKeyError:
            old = await service.db.ebt_p_wa_outbox.find_one({"space": p["space"], "id": payload.operation_id})
            if old and old.get("request_digest") != request_digest:
                raise HTTPException(409, "Chave de operação já vinculada a outro conteúdo. Consulte o histórico.")
            if not old:
                old = await service.db.ebt_p_wa_outbox.find_one({"space": p["space"], "delivery_digest": delivery_digest})
            if not old:
                raise HTTPException(409, "Operação concorrente; consulte o histórico antes de tentar novamente.")
            return public(old)
        return await execute_whatsapp(doc)

    @router.post("/whatsapp/operations/{operation_id}/resume")
    async def wa_resume(operation_id: str, p=Depends(mutation)):
        require_whatsapp_configuration()
        query = {"space": p["space"], "id": operation_id, "status": {"$in": ["limit_reached", "rejected", "deferred"]}, "$or": [{"provider_id": {"$exists": False}}, {"provider_id": ""}]}
        doc = await service.db.ebt_p_wa_outbox.find_one(query)
        if not doc:
            raise HTTPException(409, "Somente resultado conclusivo anterior ao envio pode ser retomado. Não repetir operação aceita ou incerta.")
        c = await attempt(service.get_contact(p["space"], doc["contact_id"]))
        if c["status"] != "qualified" or c["phone"] != doc["phone"] or doc.get("sender_phone_id") != cfg.wa_phone_id:
            raise HTTPException(409, "Contato ou número alterado/bloqueado. Revise a aprovação.")
        claimed = await service.db.ebt_p_wa_outbox.find_one_and_update(query, {"$set": {"status": "executing", "resumed_at": now()}, "$inc": {"resume_count": 1}})
        if not claimed:
            raise HTTPException(409, "A operação já foi retomada por outra ação.")
        return await execute_whatsapp(doc)

    return router
