"""Schémas Pydantic des ressources Authentification et Utilisateurs
(docs/conception_api_rest.md, sections 4.1 et 4.2)."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.auth.models import StatutCompte

if TYPE_CHECKING:
    from app.auth.models import Utilisateur


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UtilisateurOut(BaseModel):
    """Vue restreinte utilisée par GET /v1/auth/session (profil de
    l'utilisateur connecté). Distincte de `UtilisateurAdminOut` : deux
    contextes différents (consultation de soi-même vs administration),
    volontairement non fusionnés pour ne pas exposer plus d'informations
    que nécessaire dans /session."""

    id: int
    nom_utilisateur: str
    role: str

    model_config = {"from_attributes": True}


class UtilisateurAdminOut(BaseModel):
    """Vue complète utilisée par la ressource Utilisateurs (gestion des
    comptes, réservée à l'Administrateur)."""

    id: int
    nom_utilisateur: str
    role: str
    statut_compte: StatutCompte
    date_creation: datetime
    date_derniere_connexion: datetime | None

    @classmethod
    def depuis_modele(cls, utilisateur: "Utilisateur") -> "UtilisateurAdminOut":
        return cls(
            id=utilisateur.id,
            nom_utilisateur=utilisateur.nom_utilisateur,
            role=utilisateur.role.nom,
            statut_compte=utilisateur.statut_compte,
            date_creation=utilisateur.date_creation,
            date_derniere_connexion=utilisateur.date_derniere_connexion,
        )


class UtilisateurCreate(BaseModel):
    nom_utilisateur: str
    mot_de_passe: str
    role_id: int


class UtilisateurUpdate(BaseModel):
    """Tous les champs sont optionnels : seuls ceux fournis sont modifiés."""

    nom_utilisateur: str | None = None
    role_id: int | None = None


class UtilisateurStatutUpdate(BaseModel):
    statut_compte: StatutCompte
