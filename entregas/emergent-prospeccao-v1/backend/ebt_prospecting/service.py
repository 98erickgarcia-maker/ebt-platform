import asyncio
import re
import uuid
from datetime import datetime, timedelta, timezone
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from .domain import DEFAULT_TEMPLATES, city_key, digest, direct_links, normalize_company, now, render_template, text, valid_email


def identifier():
    return uuid.uuid4().hex


def public(doc):
    return {k: v for k, v in doc.items() if k not in {"_id", "space", "lease", "lease_until", "token_cache", "flow"}}


class ProspectService:
    def __init__(self, db, monthly_limit=3000):
        self.db = db
        self.monthly_limit = monthly_limit

    async def initialize(self):
        for name, key in [("catalog", "cnpj"), ("contacts", "cnpj"), ("templates", "id"), ("recipes", "id"), ("messages", "id"), ("events", "id"), ("budget", "month")]:
            await self.db[f"ebt_p_{name}"].create_index([("space", 1), (key, 1)], unique=True)
        await self.db.ebt_p_recipes.create_index([("enabled", 1), ("next_run", 1), ("lease_until", 1)])
        await self.db.ebt_p_catalog.create_index([("space", 1), ("active", 1), ("uf", 1), ("city_key", 1), ("cnpj", 1)])
        await self.db.ebt_p_events.create_index([("space", 1), ("contact_id", 1), ("at", -1)])
        await self.db.ebt_p_messages.create_index([("status", 1), ("due_at", 1)])

    async def import_catalog(self, space, rows, source):
        accepted, rejected = 0, []
        for index, row in enumerate(rows):
            try:
                normalized = normalize_company(row, source)
                await self.db.ebt_p_catalog.update_one({"space": space, "cnpj": normalized["cnpj"]}, {"$set": normalized}, upsert=True)
                accepted += 1
            except (ValueError, KeyError) as e:
                rejected.append({"row": index + 1, "reason": str(e)})
        return {"accepted": accepted, "rejected": rejected[:100], "rejected_count": len(rejected)}

    async def reserve(self, space):
        month = now().strftime("%Y-%m")
        try:
            await self.db.ebt_p_budget.update_one({"space": space, "month": month}, {"$setOnInsert": {"processed": 0}}, upsert=True)
        except DuplicateKeyError:
            pass
        return bool(await self.db.ebt_p_budget.find_one_and_update({"space": space, "month": month, "processed": {"$lt": self.monthly_limit}}, {"$inc": {"processed": 1}}))

    async def budget(self, space):
        doc = await self.db.ebt_p_budget.find_one({"space": space, "month": now().strftime("%Y-%m")}) or {}
        processed = doc.get("processed", 0)
        return {"processed": processed, "limit": self.monthly_limit, "remaining": max(0, self.monthly_limit - processed), "llm_calls": 0, "paid_api_calls": 0, "variable_api_cost_brl": 0, "hosting_included": False}

    async def create_recipe(self, space, user, data):
        doc = {"space": space, "id": identifier(), "user_id": user, "name": text(data["name"]), "uf": text(data.get("uf")).upper(), "city_key": city_key(data.get("city")), "city": text(data.get("city")), "cnae": text(data.get("cnae")), "batch_size": int(data.get("batch_size", 25)), "interval_hours": int(data.get("interval_hours", 24)), "enabled": True, "next_run": now(), "lease_until": now(), "cursor": "", "last_result": {}, "created_at": now()}
        if not doc["name"] or not 1 <= doc["batch_size"] <= 100 or not 1 <= doc["interval_hours"] <= 720 or not re.fullmatch(r"\d{0,7}", doc["cnae"]):
            raise ValueError("Receita inválida: lote 1–100, intervalo 1–720h e CNAE numérico.")
        if await self.db.ebt_p_recipes.count_documents({"space": space}) >= 20:
            raise ValueError("Limite de 20 receitas por espaço.")
        await self.db.ebt_p_recipes.insert_one(doc)
        return public(doc)

    async def recipes(self, space):
        return [public(d) for d in await self.db.ebt_p_recipes.find({"space": space}).sort("created_at", -1).to_list(20)]

    async def queue_recipe(self, space, recipe_id, enabled=True):
        doc = await self.db.ebt_p_recipes.find_one_and_update({"space": space, "id": recipe_id}, {"$set": {"next_run": now(), "enabled": enabled}}, return_document=ReturnDocument.AFTER)
        if not doc:
            raise LookupError("Receita não encontrada.")
        return public(doc)

    async def tick(self, space=None):
        lease = identifier()
        own = {"space": space} if space else {}
        recipe = await self.db.ebt_p_recipes.find_one_and_update({**own, "enabled": True, "next_run": {"$lte": now()}, "lease_until": {"$lte": now()}}, {"$set": {"lease": lease, "lease_until": now() + timedelta(minutes=2)}}, return_document=ReturnDocument.AFTER)
        if not recipe:
            return False
        query = {"space": recipe["space"], "active": True, "cnpj": {"$gt": recipe["cursor"]}}
        if recipe["uf"]:
            query["uf"] = recipe["uf"]
        if recipe["city_key"]:
            query["city_key"] = recipe["city_key"]
        if recipe["cnae"]:
            query["cnae"] = {"$regex": "^" + re.escape(recipe["cnae"])}
        result = {"processed": 0, "new_contacts": 0, "duplicates": 0, "budget_reached": False}
        cursor = recipe["cursor"]
        try:
            rows = await self.db.ebt_p_catalog.find(query).sort("cnpj", 1).limit(recipe["batch_size"]).to_list(recipe["batch_size"])
            for row in rows:
                if not await self.db.ebt_p_recipes.find_one({"id": recipe["id"], "space": recipe["space"], "lease": lease, "enabled": True, "lease_until": {"$gt": now()}}):
                    break
                if not await self.reserve(recipe["space"]):
                    result["budget_reached"] = True
                    break
                created = await self.db.ebt_p_contacts.update_one({"space": recipe["space"], "cnpj": row["cnpj"]}, {"$setOnInsert": {**public(row), "space": recipe["space"], "id": identifier(), "status": "review", "version": 1, "notes": "", "next_action": "", "next_action_at": None, "owner_id": recipe["user_id"], "created_at": now()}}, upsert=True)
                result["processed"] += 1
                result["new_contacts" if created.upserted_id else "duplicates"] += 1
                cursor = row["cnpj"]
            await self.db.ebt_p_recipes.update_one({"space": recipe["space"], "id": recipe["id"], "lease": lease}, {"$set": {"cursor": cursor if len(rows) == recipe["batch_size"] or result["budget_reached"] else "", "last_result": result, "last_run": now(), "next_run": now() + timedelta(hours=recipe["interval_hours"]), "lease_until": now()}, "$unset": {"lease": ""}})
        except Exception:
            await self.db.ebt_p_recipes.update_one({"space": recipe["space"], "id": recipe["id"], "lease": lease}, {"$set": {"next_run": now() + timedelta(minutes=5), "lease_until": now(), "last_result": {"error": "Falha no lote; retomada idempotente em 5 minutos."}}, "$unset": {"lease": ""}})
            raise
        return True

    async def add_contact(self, space, user, row, source):
        normalized = normalize_company(row, source)
        doc = {**normalized, "space": space, "id": identifier(), "owner_id": user, "status": "review", "version": 1, "notes": "", "next_action": "", "next_action_at": None, "created_at": now()}
        try:
            await self.db.ebt_p_contacts.insert_one(doc)
        except DuplicateKeyError:
            raise ValueError("CNPJ já cadastrado neste espaço.")
        return public(doc)

    async def list_contacts(self, space, search="", status="", skip=0, limit=50):
        query = {"space": space}
        if search:
            query["$or"] = [{key: {"$regex": re.escape(search[:100]), "$options": "i"}} for key in ("company_name", "cnpj", "email", "contact_name")]
        if status:
            query["status"] = status
        return [public(c) for c in await self.db.ebt_p_contacts.find(query).sort([("score", -1), ("id", 1)]).skip(skip).limit(limit).to_list(limit)]

    async def get_contact(self, space, contact_id):
        doc = await self.db.ebt_p_contacts.find_one({"space": space, "id": contact_id})
        if not doc:
            raise LookupError("Contato não encontrado.")
        return public(doc)

    async def update_contact(self, space, contact_id, data):
        current = await self.get_contact(space, contact_id)
        allowed = {"contact_name", "contact_role", "email", "email_quality", "phone", "website", "linkedin", "notes", "next_action", "next_action_at", "status"}
        update = {k: v for k, v in data.items() if k in allowed}
        if "email" in update:
            if update["email"] and not valid_email(update["email"]):
                raise ValueError("E-mail inválido.")
            update["email"] = valid_email(update["email"])
            if update["email"] != current["email"]:
                update["email_quality"] = "unverified"
        if update.get("email_quality", "unverified") not in {"unverified", "verified", "missing", "invalid"} or update.get("status", "review") not in {"review", "qualified", "customer", "discarded", "suppressed"}:
            raise ValueError("Situação inválida.")
        if update.get("next_action_at"):
            update["next_action_at"] = datetime.fromisoformat(update["next_action_at"].replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)
        for key in allowed - {"next_action_at"}:
            if key in update:
                update[key] = text(update[key], 4000 if key == "notes" else 500)
        update["updated_at"] = now()
        doc = await self.db.ebt_p_contacts.find_one_and_update({"space": space, "id": contact_id, "version": data["version"]}, {"$set": update, "$inc": {"version": 1}}, return_document=ReturnDocument.AFTER)
        if not doc:
            raise ValueError("Contato alterado por outra operação. Atualize a tela.")
        await self.event(space, contact_id, "contact_updated", "Cadastro atualizado.")
        return public(doc)

    async def event(self, space, contact_id, kind, description):
        await self.db.ebt_p_events.insert_one({"space": space, "id": identifier(), "contact_id": contact_id, "kind": kind, "description": text(description, 2000), "at": now()})

    async def history(self, space, contact_id):
        await self.get_contact(space, contact_id)
        return [public(e) for e in await self.db.ebt_p_events.find({"space": space, "contact_id": contact_id}).sort("at", -1).to_list(100)]

    async def suppress(self, space, contact_id, reason):
        current = await self.get_contact(space, contact_id)
        await self.update_contact(space, contact_id, {"version": current["version"], "status": "suppressed"})
        await self.db.ebt_p_messages.update_many({"space": space, "contact_id": contact_id, "status": "scheduled"}, {"$set": {"status": "cancelled"}})
        await self.event(space, contact_id, "suppressed", reason)
        return {"ok": True}

    async def templates(self, space):
        for template in DEFAULT_TEMPLATES:
            try:
                await self.db.ebt_p_templates.update_one({"space": space, "id": template["id"]}, {"$setOnInsert": {**template, "version": 1}}, upsert=True)
            except DuplicateKeyError:
                pass
        return [public(t) for t in await self.db.ebt_p_templates.find({"space": space}).sort("id", 1).to_list(50)]

    async def save_template(self, space, template_id, data):
        render_template({**data, "version": data["version"]}, {"company_name": "Empresa Exemplo", "contact_name": "Ana", "city": "Cidade"}, "Responsável")
        update = {k: text(data[k], 8000 if k == "body" else 200) for k in ("name", "subject", "body")}
        doc = await self.db.ebt_p_templates.find_one_and_update({"space": space, "id": template_id, "version": data["version"]}, {"$set": update, "$inc": {"version": 1}}, return_document=ReturnDocument.AFTER)
        if not doc:
            raise ValueError("Template alterado ou inexistente. Atualize a tela.")
        return public(doc)

    async def prepare(self, space, contact_id, template_id, sender):
        contact = await self.get_contact(space, contact_id)
        if contact["status"] in {"suppressed", "discarded"}:
            raise ValueError("Contato bloqueado para abordagem.")
        templates = await self.templates(space)
        template = next((t for t in templates if t["id"] == template_id), None)
        if not template:
            raise LookupError("Template não encontrado.")
        rendered = render_template(template, contact, sender)
        payload = {**rendered, "contact_id": contact_id, "contact_version": contact["version"], "recipient": contact["phone"] if template["channel"] == "whatsapp" else contact["email"], "company_name": contact["company_name"], "channel": template["channel"]}
        return {**payload, "digest": digest(payload), "links": direct_links(contact, rendered["subject"], rendered["body"])}

    async def approve_message(self, space, user, contact_id, expected_digest, template_id, sender, due_at, mode):
        prepared = await self.prepare(space, contact_id, template_id, sender)
        if expected_digest != prepared["digest"]:
            raise ValueError("A prévia mudou; revise o destinatário e o texto novamente.")
        contact = await self.get_contact(space, contact_id)
        if not prepared["recipient"] or prepared["channel"] != "email":
            raise ValueError("Selecione template de e-mail e contato com endereço válido.")
        if mode not in {"draft", "send"}:
            raise ValueError("Modo inválido.")
        if mode == "send" and (contact["status"] != "qualified" or contact["email_quality"] != "verified"):
            raise ValueError("Envio exige contato qualificado e endereço verificado pelo responsável.")
        due = datetime.fromisoformat(due_at.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)
        if due < now() - timedelta(minutes=1) or due > now() + timedelta(days=365):
            raise ValueError("Data de agendamento inválida.")
        msg_id = digest({"space": space, "digest": expected_digest, "due": due.isoformat(), "mode": mode})
        doc = {**{k: v for k, v in prepared.items() if k != "links"}, "space": space, "id": msg_id, "user_id": user, "due_at": due, "mode": mode, "status": "scheduled", "created_at": now(), "attempts": 0}
        result = await self.db.ebt_p_messages.update_one({"space": space, "id": msg_id}, {"$setOnInsert": doc}, upsert=True)
        if result.upserted_id:
            await self.event(space, contact_id, "email_approved", f"{user} aprovou {mode} para {doc['recipient']}; versão {doc['contact_version']}; digest {expected_digest}.")
        return public(await self.db.ebt_p_messages.find_one({"space": space, "id": msg_id}))

    async def prepare_manual_whatsapp(self, space, user, contact_id, expected_digest, template_id, sender):
        prepared = await self.prepare(space, contact_id, template_id, sender)
        if prepared["digest"] != expected_digest:
            raise ValueError("A prévia mudou; prepare o template novamente.")
        if prepared["channel"] != "whatsapp" or not prepared["links"].get("whatsapp"):
            raise ValueError("Selecione template WhatsApp e um telefone internacional válido.")
        event = {"space": space, "id": identifier(), "contact_id": contact_id,
                 "kind": "whatsapp_manual_prepared", "status": "manual_prepared", "at": now(),
                 "description": "Template manual preparado para abrir a conversa; envio não confirmado.",
                 "user_id": user, "recipient": prepared["recipient"], "body": prepared["body"],
                 "template_id": template_id, "template_version": prepared["template_version"],
                 "contact_version": prepared["contact_version"], "digest": expected_digest}
        await self.db.ebt_p_events.insert_one(event)
        return {"url": prepared["links"]["whatsapp"], "status": "manual_prepared", "event_id": event["id"]}

    async def messages(self, space, contact_id=None):
        query = {"space": space}
        if contact_id:
            query["contact_id"] = contact_id
        return [public(m) for m in await self.db.ebt_p_messages.find(query).sort("due_at", -1).to_list(100)]

    async def summary(self, space):
        contacts = self.db.ebt_p_contacts
        return {"catalog": await self.db.ebt_p_catalog.count_documents({"space": space}), "contacts": await contacts.count_documents({"space": space}), "review": await contacts.count_documents({"space": space, "status": "review"}), "qualified": await contacts.count_documents({"space": space, "status": "qualified"}), "overdue": await contacts.count_documents({"space": space, "next_action_at": {"$ne": None, "$lte": now()}, "status": {"$nin": ["suppressed", "discarded"]}}), "budget": await self.budget(space)}
