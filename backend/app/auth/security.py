"""Primitives de sécurité : hachage des mots de passe et jetons de session.

Voir docs/architecture_logicielle.md (section 4.6) pour la mission du
module Authentification et docs/conception_api_rest.md (section 5) pour
le principe retenu (jeton de session vérifié à chaque requête).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

# bcrypt n'accepte pas plus de 72 octets : au-delà, la fin du mot de
# passe serait silencieusement ignorée. On préfère lever une erreur
# explicite plutôt que d'affaiblir silencieusement le hachage.
_LONGUEUR_MAX_MOT_DE_PASSE_OCTETS = 72


def hash_password(mot_de_passe: str) -> str:
    mot_de_passe_octets = mot_de_passe.encode("utf-8")
    if len(mot_de_passe_octets) > _LONGUEUR_MAX_MOT_DE_PASSE_OCTETS:
        raise ValueError("Le mot de passe dépasse la longueur maximale supportée.")
    sel = bcrypt.gensalt()
    return bcrypt.hashpw(mot_de_passe_octets, sel).decode("utf-8")


def verify_password(mot_de_passe: str, mot_de_passe_hash: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), mot_de_passe_hash.encode("utf-8"))


def create_access_token(sujet: str, role: str) -> str:
    """Crée un jeton JWT portant l'identifiant de l'utilisateur et son rôle."""
    settings = get_settings()
    expiration = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": sujet, "role": role, "exp": expiration}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class TokenInvalide(Exception):
    """Levée quand le jeton est absent, expiré ou altéré."""


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenInvalide from exc
