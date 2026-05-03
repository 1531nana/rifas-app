from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, public, raffles
from app.core.config import get_settings
from app.core.database import create_db_and_tables

settings = get_settings()

app = FastAPI(title="Rifas App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(raffles.router)
app.include_router(public.router)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
