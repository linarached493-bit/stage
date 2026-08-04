"""Schémas Pydantic de la ressource Alertes
(docs/conception_api_rest.md, section 4.3)."""

from datetime import datetime

from pydantic import BaseModel


class AlerteOut(BaseModel):
    id: int
    type_menace: str
    ip_source: str
    ip_destination: str | None
    gravite: str
    statut_traitement: str
    horodatage_detection: datetime

    model_config = {"from_attributes": True}
