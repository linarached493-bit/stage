"""Point d'entrée de l'application backend.

Expose une partie du catalogue d'endpoints défini dans
docs/conception_api_rest.md : Authentification (login, session),
Utilisateurs (gestion complète), Alertes (consultation et traitement),
Règles (gestion complète) et Logs (consultation). Les autres ressources
(Statistiques, Configuration, Liste noire) restent à faire — voir
docs/plan_de_developpement.md, Phase 7.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.alerts.router import router as alertes_router
from app.auth.router import router as auth_router
from app.auth.router import utilisateurs_router
from app.core.config import get_settings
from app.detection.router import router as regles_router
from app.eventlog.router import router as logs_router

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

app.include_router(auth_router)
app.include_router(utilisateurs_router)
app.include_router(alertes_router)
app.include_router(regles_router)
app.include_router(logs_router)
