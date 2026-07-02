from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    auth,
    cases,
    health,
    metrics,
    prompt_versions,
    tipos_documento,
    users,
)
from app.config import get_settings
from app.db import init_db


def _validate_settings() -> None:
    """Falla al arranque con un mensaje claro si la configuracion es inconsistente."""
    settings = get_settings()
    if settings.extractor_mode == "gemini" and not settings.gemini_api_key:
        raise RuntimeError(
            "EXTRACTOR_MODE=gemini requiere GEMINI_API_KEY definida en el .env. "
            "Definila o volve a EXTRACTOR_MODE=mock."
        )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    _validate_settings()
    init_db()
    yield


app = FastAPI(
    title="ADA - Plataforma de Auditoria Documental Automatizada",
    description="API del prototipo MVP. Ver TFG para arquitectura completa.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(prompt_versions.router)
app.include_router(tipos_documento.router)
app.include_router(users.router)
app.include_router(metrics.router)
