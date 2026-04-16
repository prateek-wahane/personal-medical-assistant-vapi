from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.middleware.observability import RequestContextMiddleware, SimpleRateLimitMiddleware, configure_logging
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.reports import router as reports_router
from app.routers.vapi import router as vapi_router

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="Production-hardened starter backend for a Vapi-powered personal medical assistant.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(reports_router)
app.include_router(vapi_router)
