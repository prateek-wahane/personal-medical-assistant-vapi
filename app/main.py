from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Base, engine
from app.routers.health import router as health_router
from app.routers.reports import router as reports_router
from app.routers.vapi import router as vapi_router

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Starter backend for a Vapi-powered personal medical assistant.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(reports_router)
app.include_router(vapi_router)
