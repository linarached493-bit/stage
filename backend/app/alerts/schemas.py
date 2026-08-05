"""Schémas Pydantic de la ressource Alertes
(docs/conception_api_rest.md, section 4.3)."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.alerts.models import StatutAlerte
from app.database.enums import Gravite

if TYPE_CHECKING:
    from app.alerts.models import Alerte, HistoriqueAlerte


class AlerteOut(BaseModel):
    """Vue de liste, inchangée par cette étape : conserver cette forme
    évite de casser les nombreux scénarios de détection déjà testés qui
    consultent GET /v1/alertes."""

    id: int
    type_menace: str
    ip_source: str
    ip_destination: str | None
    gravite: str
    statut_traitement: str
    horodatage_detection: datetime

    model_config = {"from_attributes": True}


class HistoriqueEntreeOut(BaseModel):
    statut: StatutAlerte
    commentaire: str | None
    utilisateur: str
    horodatage: datetime

    @classmethod
    def depuis_modele(cls, entree: "HistoriqueAlerte") -> "HistoriqueEntreeOut":
        return cls(
            statut=entree.statut,
            commentaire=entree.commentaire,
            utilisateur=entree.utilisateur.nom_utilisateur,
            horodatage=entree.horodatage,
        )


class AlerteDetailOut(BaseModel):
    """Vue détaillée, utilisée par GET /v1/alertes/{id} et par les
    endpoints d'acquittement/fermeture/commentaire : inclut la règle
    d'origine et l'historique complet des changements d'état."""

    id: int
    type_menace: str
    ip_source: str
    ip_destination: str | None
    gravite: Gravite
    statut_traitement: StatutAlerte
    horodatage_detection: datetime
    regle: str
    historique: list[HistoriqueEntreeOut]

    @classmethod
    def depuis_modele(cls, alerte: "Alerte") -> "AlerteDetailOut":
        return cls(
            id=alerte.id,
            type_menace=alerte.type_menace,
            ip_source=alerte.ip_source,
            ip_destination=alerte.ip_destination,
            gravite=alerte.gravite,
            statut_traitement=alerte.statut_traitement,
            horodatage_detection=alerte.horodatage_detection,
            regle=alerte.regle.nom,
            historique=[HistoriqueEntreeOut.depuis_modele(e) for e in alerte.historique],
        )


class AlerteAcquitterRequest(BaseModel):
    commentaire: str | None = None


class AlerteFermerRequest(BaseModel):
    statut_final: StatutAlerte
    commentaire: str | None = None


class AlerteCommentaireRequest(BaseModel):
    commentaire: str
