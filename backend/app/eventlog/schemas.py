"""Schémas Pydantic de la ressource Logs
(docs/conception_api_rest.md, section 4.4)."""

from datetime import datetime

from pydantic import BaseModel

from app.eventlog.models import NiveauLog


class LogOut(BaseModel):
    """Schéma unique pour la liste et le détail : `LogEvenement` reste un
    modèle volontairement plat (pas de relation lourde à embarquer,
    contrairement à Alerte/Règle), donc pas de vue restreinte séparée."""

    id: int
    horodatage: datetime
    type_evenement: str
    niveau: NiveauLog
    ip_source: str
    ip_destination: str | None
    ports: str | None
    protocole: str | None
    alerte_id: int | None

    model_config = {"from_attributes": True}
