"""MicroscopyAI FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.analyze import router as analyze_router
from backend.api.config import router as config_router
from backend.api.health import router as health_router
from backend.api.samples import router as samples_router

app = FastAPI(
    title="MicroscopyAI",
    description="Brightfield Cell Analysis & Quantification API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(config_router, prefix="/api", tags=["config"])
app.include_router(analyze_router, prefix="/api", tags=["analyze"])
app.include_router(samples_router, prefix="/api", tags=["samples"])
