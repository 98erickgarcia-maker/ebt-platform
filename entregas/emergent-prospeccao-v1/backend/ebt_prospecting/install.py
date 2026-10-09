import asyncio
import contextlib
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from .channels import MessageWorker
from .config import Config
from .outlook import OutlookConnector
from .router import create_router
from .service import ProspectService

logger = logging.getLogger("ebt.prospecting")


def install_prospecting(app, db, get_current_user, cfg=None):
    """Montar uma única vez, antes de iniciar o FastAPI. Não cria login nem banco."""
    cfg = cfg or Config.from_env()
    cfg.validate()
    service = ProspectService(db, cfg.monthly_limit)
    outlook = OutlookConnector(db, cfg)
    worker = MessageWorker(service, outlook, cfg.send_enabled, cfg.daily_email_limit, space=cfg.workspace)
    app.include_router(create_router(service, cfg, get_current_user, outlook))
    stop = asyncio.Event()
    task = None

    @app.middleware("http")
    async def guard_legacy_development(request: Request, call_next):
        # O backend de referência expõe login temporário e limpeza global.
        if request.url.path in {"/api/auth/dev-login", "/api/leads/clear-all"}:
            return JSONResponse({"detail": "Rota de teste bloqueada pela extensão."}, status_code=403)
        if request.url.path.startswith("/api/prospecting/"):
            size = request.headers.get("Content-Length", "0")
            if size.isdigit() and int(size) > 6_000_000:
                return JSONResponse({"detail": "Payload muito grande."}, status_code=413)
        response = await call_next(request)
        if request.url.path.startswith("/api/prospecting/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    async def cycle():
        while not stop.is_set():
            try:
                await service.tick(cfg.workspace)
                # Um e-mail por ciclo de 30s: não cria rajada de envios.
                await worker.tick()
                await worker.reconcile()
            except Exception:
                logger.error("Falha no ciclo de prospecção; veja estado persistido e conexão MongoDB.")
            try:
                await asyncio.wait_for(stop.wait(), timeout=30)
            except asyncio.TimeoutError:
                pass

    async def start():
        nonlocal task
        await service.initialize()
        for collection, key in [("ebt_p_outlook", "user_id"), ("ebt_p_wa_events", "id"), ("ebt_p_wa_outbox", "id"), ("ebt_p_wa_budget", "month")]:
            await db[collection].create_index([("space", 1), (key, 1)], unique=True)
        await db.ebt_p_oauth.create_index("expires_at", expireAfterSeconds=0)
        await db.ebt_p_oauth.create_index("state", unique=True)
        task = asyncio.create_task(cycle())

    async def shutdown():
        stop.set()
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    # O app enviado usa eventos startup/shutdown. Se a aplicação real usar
    # lifespan, chame start()/shutdown() dentro dele em vez destes eventos.
    app.add_event_handler("startup", start)
    app.add_event_handler("shutdown", shutdown)
    return {"service": service, "outlook": outlook, "worker": worker, "start": start, "shutdown": shutdown}
