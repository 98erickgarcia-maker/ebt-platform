"""Servidor exclusivamente local com dados sintéticos. Não usar em produção."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if os.getenv("EP_QA_ONLY") != "1":
    raise RuntimeError("Servidor de teste exige EP_QA_ONLY=1 e bind 127.0.0.1.")
from fastapi import FastAPI, Request, HTTPException
from mongomock_motor import AsyncMongoMockClient
from ebt_prospecting.config import Config
from ebt_prospecting.outlook import OutlookConnector
from ebt_prospecting.router import create_router
from ebt_prospecting.service import ProspectService
from test_domain import ROW, SOURCE

db = AsyncMongoMockClient().synthetic
service = ProspectService(db)
cfg = Config(owner_email="owner@example.com", workspace="synthetic", origins=["http://127.0.0.1:5197"])
app = FastAPI()


async def current(request: Request):
    if request.client.host != "127.0.0.1":
        raise HTTPException(403)
    return {"user_id": "synthetic-owner", "role": "owner", "email": "owner@example.com"}


app.include_router(create_router(service, cfg, current, OutlookConnector(db, cfg)))


@app.on_event("startup")
async def seed():
    await service.initialize()
    await service.add_contact("synthetic", "synthetic-owner", {**ROW, "company_name": "Empresa Exemplo A", "email": "comercial-a@example.com"}, SOURCE)
    await service.add_contact("synthetic", "synthetic-owner", {**ROW, "cnpj": "12ABC34501DE35", "company_name": "Empresa Exemplo B", "email": "comercial-b@example.com"}, SOURCE)
