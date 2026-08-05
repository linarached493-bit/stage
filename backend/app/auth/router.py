"""Ressources Authentification et Utilisateurs
(docs/conception_api_rest.md, sections 4.1 et 4.2)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.auth.models import Utilisateur
from app.auth.schemas import (
    Token,
    UtilisateurAdminOut,
    UtilisateurCreate,
    UtilisateurOut,
    UtilisateurStatutUpdate,
    UtilisateurUpdate,
)
from app.auth.security import create_access_token
from app.auth.service import (
    NomUtilisateurDejaUtilise,
    RoleIntrouvable,
    authenticate_user,
    changer_statut_utilisateur,
    creer_utilisateur,
    lister_utilisateurs,
    modifier_utilisateur,
    obtenir_utilisateur,
)
from app.database.session import get_db

router = APIRouter(prefix="/v1/auth", tags=["Authentification"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db),
) -> Token:
    utilisateur = authenticate_user(session, form_data.username, form_data.password)
    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides ou compte désactivé.",
        )
    jeton = create_access_token(sujet=str(utilisateur.id), role=utilisateur.role.nom)
    return Token(access_token=jeton)


@router.get("/session", response_model=UtilisateurOut)
def session_courante(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    return UtilisateurOut(
        id=utilisateur.id, nom_utilisateur=utilisateur.nom_utilisateur, role=utilisateur.role.nom
    )


# --- Ressource Utilisateurs (UC6 « Gérer les utilisateurs », réservée à
# l'Administrateur conformément à la matrice de permissions du cahier
# des charges, section 5.4) --------------------------------------------

utilisateurs_router = APIRouter(prefix="/v1/utilisateurs", tags=["Utilisateurs"])
_verifier_administrateur = require_role("Administrateur")


def _obtenir_utilisateur_ou_404(session: Session, utilisateur_id: int) -> Utilisateur:
    utilisateur = obtenir_utilisateur(session, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable."
        )
    return utilisateur


@utilisateurs_router.get("", response_model=list[UtilisateurAdminOut])
def lister(
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> list[UtilisateurAdminOut]:
    return [UtilisateurAdminOut.depuis_modele(u) for u in lister_utilisateurs(session)]


@utilisateurs_router.get("/{utilisateur_id}", response_model=UtilisateurAdminOut)
def consulter(
    utilisateur_id: int,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> UtilisateurAdminOut:
    return UtilisateurAdminOut.depuis_modele(_obtenir_utilisateur_ou_404(session, utilisateur_id))


@utilisateurs_router.post(
    "", response_model=UtilisateurAdminOut, status_code=status.HTTP_201_CREATED
)
def creer(
    donnees: UtilisateurCreate,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> UtilisateurAdminOut:
    try:
        nouvel_utilisateur = creer_utilisateur(
            session, donnees.nom_utilisateur, donnees.mot_de_passe, donnees.role_id
        )
    except NomUtilisateurDejaUtilise as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà utilisé.",
        ) from exc
    except RoleIntrouvable as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Le rôle indiqué n'existe pas.",
        ) from exc
    return UtilisateurAdminOut.depuis_modele(nouvel_utilisateur)


@utilisateurs_router.put("/{utilisateur_id}", response_model=UtilisateurAdminOut)
def modifier(
    utilisateur_id: int,
    donnees: UtilisateurUpdate,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> UtilisateurAdminOut:
    utilisateur = _obtenir_utilisateur_ou_404(session, utilisateur_id)
    try:
        utilisateur = modifier_utilisateur(
            session,
            utilisateur,
            nom_utilisateur=donnees.nom_utilisateur,
            role_id=donnees.role_id,
        )
    except NomUtilisateurDejaUtilise as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà utilisé.",
        ) from exc
    except RoleIntrouvable as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Le rôle indiqué n'existe pas.",
        ) from exc
    return UtilisateurAdminOut.depuis_modele(utilisateur)


@utilisateurs_router.patch("/{utilisateur_id}/statut", response_model=UtilisateurAdminOut)
def changer_statut(
    utilisateur_id: int,
    donnees: UtilisateurStatutUpdate,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> UtilisateurAdminOut:
    utilisateur = _obtenir_utilisateur_ou_404(session, utilisateur_id)
    utilisateur = changer_statut_utilisateur(session, utilisateur, donnees.statut_compte)
    return UtilisateurAdminOut.depuis_modele(utilisateur)
