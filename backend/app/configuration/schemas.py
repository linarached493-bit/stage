"""Schémas Pydantic des ressources Configuration et Liste noire
(docs/conception_api_rest.md, sections 4.7 et 4.8)."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.configuration.models import StatutListeNoire

if TYPE_CHECKING:
    from app.configuration.models import ParametreConfiguration


class ParametreOut(BaseModel):
    nom_parametre: str
    valeur: str
    description: str | None
    date_derniere_modification: datetime | None

    @classmethod
    def depuis_modele(cls, parametre: "ParametreConfiguration") -> "ParametreOut":
        return cls(
            nom_parametre=parametre.nom_parametre,
            valeur=parametre.valeur,
            description=parametre.description,
            date_derniere_modification=parametre.date_derniere_modification,
        )


class ParametreUpdate(BaseModel):
    valeur: str
    description: str | None = None


class PortsInterditsOut(BaseModel):
    ports: list[int]


class PortsInterditsUpdate(BaseModel):
    ports: list[int]


class AdresseListeNoireOut(BaseModel):
    id: int
    adresse_ip: str
    motif_source: str | None
    date_ajout: datetime
    statut: StatutListeNoire

    model_config = {"from_attributes": True}


class AdresseListeNoireCreate(BaseModel):
    adresse_ip: str
    motif_source: str | None = None


class AdresseListeNoireStatutUpdate(BaseModel):
    statut: StatutListeNoire
