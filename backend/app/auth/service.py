"""Logique métier de l'Authentification (docs/conception_uml.md,
diagramme de séquence « Authentification d'un utilisateur »).
"""

from sqlalchemy.orm import Session

from app.auth.models import StatutCompte, Utilisateur
from app.auth.security import verify_password


def authenticate_user(
    session: Session, nom_utilisateur: str, mot_de_passe: str
) -> Utilisateur | None:
    """Retourne l'utilisateur si les identifiants sont valides et le compte actif, sinon None."""
    utilisateur = (
        session.query(Utilisateur).filter(Utilisateur.nom_utilisateur == nom_utilisateur).first()
    )
    if utilisateur is None:
        return None
    if utilisateur.statut_compte is not StatutCompte.ACTIF:
        return None
    if not verify_password(mot_de_passe, utilisateur.mot_de_passe_hash):
        return None
    return utilisateur
