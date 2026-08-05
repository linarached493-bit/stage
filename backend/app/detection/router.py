"""Ressource Règles (docs/conception_api_rest.md, section 4.5 ;
docs/cahier_des_charges.md, UC3 « Configurer une règle de détection »).

Lecture (liste, détail) ouverte à l'Administrateur et à l'Analyste
sécurité, conformément à la matrice de permissions du cahier des
charges (section 5.4). Écriture (création, modification, changement de
statut) réservée à l'Administrateur : restriction volontaire pour cette
étape, plus stricte que la matrice d'origine qui autorisait aussi
l'Analyste sécurité à gérer les règles — écart assumé et documenté.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.auth.models import Utilisateur
from app.database.session import get_db
from app.detection.schemas import RegleCreate, RegleOut, RegleStatutUpdate, RegleUpdate
from app.detection.service import (
    ConditionDeclenchementInvalide,
    NomRegleDejaUtilise,
    changer_statut_regle,
    creer_regle,
    lister_regles,
    modifier_regle,
    obtenir_regle,
)

router = APIRouter(prefix="/v1/regles", tags=["Règles"])

ROLES_LECTURE = ("Administrateur", "Analyste sécurité")
_verifier_acces_lecture = require_role(*ROLES_LECTURE)
_verifier_administrateur = require_role("Administrateur")


def _obtenir_regle_ou_404(session: Session, regle_id: int):
    regle = obtenir_regle(session, regle_id)
    if regle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Règle introuvable.")
    return regle


@router.get("", response_model=list[RegleOut])
def lister(
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces_lecture),
) -> list[RegleOut]:
    return [RegleOut.depuis_modele(r) for r in lister_regles(session)]


@router.get("/{regle_id}", response_model=RegleOut)
def consulter(
    regle_id: int,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces_lecture),
) -> RegleOut:
    return RegleOut.depuis_modele(_obtenir_regle_ou_404(session, regle_id))


@router.post("", response_model=RegleOut, status_code=status.HTTP_201_CREATED)
def creer(
    donnees: RegleCreate,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> RegleOut:
    try:
        nouvelle_regle = creer_regle(
            session,
            nom=donnees.nom,
            description=donnees.description,
            type_menace=donnees.type_menace,
            condition_declenchement=donnees.condition_declenchement,
            gravite=donnees.gravite,
            auteur=utilisateur,
        )
    except NomRegleDejaUtilise as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ce nom de règle est déjà utilisé."
        ) from exc
    except ConditionDeclenchementInvalide as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return RegleOut.depuis_modele(nouvelle_regle)


@router.put("/{regle_id}", response_model=RegleOut)
def modifier(
    regle_id: int,
    donnees: RegleUpdate,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> RegleOut:
    regle = _obtenir_regle_ou_404(session, regle_id)
    try:
        regle = modifier_regle(
            session,
            regle,
            auteur=utilisateur,
            nom=donnees.nom,
            description=donnees.description,
            type_menace=donnees.type_menace,
            condition_declenchement=donnees.condition_declenchement,
            gravite=donnees.gravite,
        )
    except NomRegleDejaUtilise as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ce nom de règle est déjà utilisé."
        ) from exc
    except ConditionDeclenchementInvalide as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return RegleOut.depuis_modele(regle)


@router.patch("/{regle_id}/statut", response_model=RegleOut)
def changer_statut(
    regle_id: int,
    donnees: RegleStatutUpdate,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> RegleOut:
    regle = _obtenir_regle_ou_404(session, regle_id)
    regle = changer_statut_regle(session, regle, donnees.statut, auteur=utilisateur)
    return RegleOut.depuis_modele(regle)
