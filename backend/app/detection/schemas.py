"""Schémas Pydantic de la ressource Règles
(docs/conception_api_rest.md, section 4.5)."""

import json
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.database.enums import Gravite
from app.detection.models import StatutRegle

if TYPE_CHECKING:
    from app.detection.models import Regle


class RegleOut(BaseModel):
    """Vue complète d'une règle, y compris ses paramètres de
    déclenchement (`condition_declenchement`, exposée en dict plutôt
    qu'en JSON brut). Utilisée par les cinq endpoints de la ressource :
    aucune vue restreinte séparée n'est nécessaire, Administrateur et
    Analyste sécurité ayant déjà accès au même niveau de détail en
    lecture (cahier des charges, section 5.4)."""

    id: int
    nom: str
    description: str | None
    type_menace: str
    condition_declenchement: dict
    gravite: Gravite
    statut: StatutRegle
    auteur: str
    date_creation: datetime
    date_derniere_modification: datetime | None

    @classmethod
    def depuis_modele(cls, regle: "Regle") -> "RegleOut":
        return cls(
            id=regle.id,
            nom=regle.nom,
            description=regle.description,
            type_menace=regle.type_menace,
            condition_declenchement=json.loads(regle.condition_declenchement),
            gravite=regle.gravite,
            statut=regle.statut,
            auteur=regle.auteur.nom_utilisateur,
            date_creation=regle.date_creation,
            date_derniere_modification=regle.date_derniere_modification,
        )


class RegleCreate(BaseModel):
    nom: str
    description: str | None = None
    type_menace: str
    condition_declenchement: dict
    gravite: Gravite


class RegleUpdate(BaseModel):
    """Tous les champs sont optionnels : seuls ceux fournis sont modifiés."""

    nom: str | None = None
    description: str | None = None
    type_menace: str | None = None
    condition_declenchement: dict | None = None
    gravite: Gravite | None = None


class RegleStatutUpdate(BaseModel):
    statut: StatutRegle
