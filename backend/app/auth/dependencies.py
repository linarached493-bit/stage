"""Dépendances FastAPI pour l'authentification et le contrôle d'accès
par rôle (docs/conception_api_rest.md, section 5.3 : contrôle d'accès
centralisé avant tout traitement de la requête).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.models import Utilisateur
from app.auth.security import TokenInvalide, decode_access_token
from app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> Utilisateur:
    erreur_authentification = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification requise ou jeton invalide.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except TokenInvalide as exc:
        raise erreur_authentification from exc

    utilisateur_id = payload.get("sub")
    if utilisateur_id is None:
        raise erreur_authentification

    utilisateur = session.get(Utilisateur, int(utilisateur_id))
    if utilisateur is None:
        raise erreur_authentification
    return utilisateur


def require_role(*roles_autorises: str):
    """Fabrique de dépendance : n'autorise que les rôles listés (moindre privilège)."""

    def _verifier_role(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if utilisateur.role.nom not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profil non autorisé pour cette action.",
            )
        return utilisateur

    return _verifier_role
