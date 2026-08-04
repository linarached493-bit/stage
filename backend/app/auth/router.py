"""Ressource Authentification (docs/conception_api_rest.md, section 4.1)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import Utilisateur
from app.auth.schemas import Token, UtilisateurOut
from app.auth.security import create_access_token
from app.auth.service import authenticate_user
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
