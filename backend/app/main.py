import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, jobs, public, raffles, webhooks
from app.core.config import get_settings
from sqlmodel import Session

from app.core.database import create_db_and_tables, engine
from app.services.raffles import expire_all_old_reservations

settings = get_settings()
logger = logging.getLogger(__name__)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Rifas App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(raffles.router)
app.include_router(public.router)
app.include_router(public.compat_router)
app.include_router(webhooks.router)
app.include_router(jobs.router)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.on_event("startup")
async def on_startup() -> None:
    create_db_and_tables()
    app.state.reservation_expiry_task = asyncio.create_task(periodic_reservation_expiry())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    task = getattr(app.state, "reservation_expiry_task", None)
    if task:
        task.cancel()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def periodic_reservation_expiry() -> None:
    while True:
        try:
            with Session(engine) as session:
                expire_all_old_reservations(session)
        except Exception as exc:
            logger.exception("Reservation expiry job error: %s", exc)
        await asyncio.sleep(15 * 60)
