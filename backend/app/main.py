"""Point d'entrée de l'application backend.

Phase 1 — Initialisation : instancie l'application FastAPI sans y rattacher
aucune route. Les routeurs des différentes ressources de l'API (voir
docs/conception_api_rest.md) seront ajoutés à partir de la Phase 7.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
