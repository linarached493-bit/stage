"""Ressource Alertes (docs/conception_api_rest.md, section 4.3 ;
docs/cahier_des_charges.md, UC2 « Visualiser les alertes » et UC8
« Qualifier une alerte »).

Lecture : Administrateur, Analyste sécurité, Lecture seule. Traitement
(acquittement, fermeture, commentaire) : Administrateur et Analyste
sécurité, conformément à la matrice de permissions du cahier des
charges (section 5.4) — aucun écart ici, contrairement à la
restriction volontaire déjà appliquée à l'écriture sur les Règles.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.alerts.models import Alerte, StatutAlerte
from app.alerts.schemas import (
    AlerteAcquitterRequest,
    AlerteCommentaireRequest,
    AlerteDetailOut,
    AlerteFermerRequest,
    AlerteOut,
)
from app.alerts.service import (
    StatutFermetureInvalide,
    TransitionAlerteInvalide,
    acquitter_alerte,
    ajouter_commentaire,
    fermer_alerte,
    lister_alertes,
    obtenir_alerte,
)
from app.auth.dependencies import require_role
from app.auth.models import Utilisateur
from app.database.enums import Gravite
from app.database.session import get_db

router = APIRouter(prefix="/v1/alertes", tags=["Alertes"])

ROLES_LECTURE = ("Administrateur", "Analyste sécurité", "Lecture seule")
ROLES_TRAITEMENT = ("Administrateur", "Analyste sécurité")
_verifier_acces_lecture = require_role(*ROLES_LECTURE)
_verifier_acces_traitement = require_role(*ROLES_TRAITEMENT)


def _obtenir_alerte_ou_404(session: Session, alerte_id: int) -> Alerte:
    alerte = obtenir_alerte(session, alerte_id)
    if alerte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte introuvable.")
    return alerte


@router.get("", response_model=list[AlerteOut])
def lister(
    gravite: Gravite | None = None,
    statut: StatutAlerte | None = None,
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces_lecture),
) -> list[Alerte]:
    return lister_alertes(
        session, gravite=gravite, statut=statut, date_debut=date_debut, date_fin=date_fin
    )


@router.get("/{alerte_id}", response_model=AlerteDetailOut)
def consulter(
    alerte_id: int,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces_lecture),
) -> AlerteDetailOut:
    return AlerteDetailOut.depuis_modele(_obtenir_alerte_ou_404(session, alerte_id))


@router.patch("/{alerte_id}/acquitter", response_model=AlerteDetailOut)
def acquitter(
    alerte_id: int,
    donnees: AlerteAcquitterRequest,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_acces_traitement),
) -> AlerteDetailOut:
    alerte = _obtenir_alerte_ou_404(session, alerte_id)
    try:
        alerte = acquitter_alerte(session, alerte, utilisateur, donnees.commentaire)
    except TransitionAlerteInvalide as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AlerteDetailOut.depuis_modele(alerte)


@router.patch("/{alerte_id}/fermer", response_model=AlerteDetailOut)
def fermer(
    alerte_id: int,
    donnees: AlerteFermerRequest,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_acces_traitement),
) -> AlerteDetailOut:
    alerte = _obtenir_alerte_ou_404(session, alerte_id)
    try:
        alerte = fermer_alerte(
            session, alerte, utilisateur, donnees.statut_final, donnees.commentaire
        )
    except StatutFermetureInvalide as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except TransitionAlerteInvalide as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AlerteDetailOut.depuis_modele(alerte)


@router.post(
    "/{alerte_id}/commentaires", response_model=AlerteDetailOut, status_code=status.HTTP_201_CREATED
)
def commenter(
    alerte_id: int,
    donnees: AlerteCommentaireRequest,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_acces_traitement),
) -> AlerteDetailOut:
    alerte = _obtenir_alerte_ou_404(session, alerte_id)
    alerte = ajouter_commentaire(session, alerte, utilisateur, donnees.commentaire)
    return AlerteDetailOut.depuis_modele(alerte)
