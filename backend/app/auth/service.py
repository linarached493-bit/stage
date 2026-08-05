"""Logique métier de l'Authentification et de la gestion des
Utilisateurs (docs/conception_uml.md, diagramme de séquence
« Authentification d'un utilisateur » ; docs/cahier_des_charges.md,
cas d'utilisation UC6 « Gérer les utilisateurs »).
"""

from sqlalchemy.orm import Session

from app.auth.models import Role, StatutCompte, Utilisateur
from app.auth.security import hash_password, verify_password


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


class NomUtilisateurDejaUtilise(Exception):
    """Violation de la contrainte d'unicité sur `nom_utilisateur`
    (docs/conception_base_de_donnees.md, section 6.1)."""


class RoleIntrouvable(Exception):
    """Le `role_id` fourni ne correspond à aucun rôle existant
    (référence obligatoire, docs/conception_base_de_donnees.md, section 6.2)."""


def lister_utilisateurs(session: Session) -> list[Utilisateur]:
    return session.query(Utilisateur).order_by(Utilisateur.nom_utilisateur).all()


def obtenir_utilisateur(session: Session, utilisateur_id: int) -> Utilisateur | None:
    return session.get(Utilisateur, utilisateur_id)


def _verifier_role_existe(session: Session, role_id: int) -> None:
    if session.get(Role, role_id) is None:
        raise RoleIntrouvable(role_id)


def _verifier_nom_utilisateur_disponible(
    session: Session, nom_utilisateur: str, utilisateur_id_exclu: int | None = None
) -> None:
    requete = session.query(Utilisateur).filter(Utilisateur.nom_utilisateur == nom_utilisateur)
    if utilisateur_id_exclu is not None:
        requete = requete.filter(Utilisateur.id != utilisateur_id_exclu)
    if requete.first() is not None:
        raise NomUtilisateurDejaUtilise(nom_utilisateur)


def creer_utilisateur(
    session: Session, nom_utilisateur: str, mot_de_passe: str, role_id: int
) -> Utilisateur:
    _verifier_role_existe(session, role_id)
    _verifier_nom_utilisateur_disponible(session, nom_utilisateur)

    utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        mot_de_passe_hash=hash_password(mot_de_passe),
        role_id=role_id,
    )
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    return utilisateur


def modifier_utilisateur(
    session: Session,
    utilisateur: Utilisateur,
    *,
    nom_utilisateur: str | None = None,
    role_id: int | None = None,
) -> Utilisateur:
    if nom_utilisateur is not None:
        _verifier_nom_utilisateur_disponible(
            session, nom_utilisateur, utilisateur_id_exclu=utilisateur.id
        )
        utilisateur.nom_utilisateur = nom_utilisateur
    if role_id is not None:
        _verifier_role_existe(session, role_id)
        utilisateur.role_id = role_id

    session.commit()
    session.refresh(utilisateur)
    return utilisateur


def changer_statut_utilisateur(
    session: Session, utilisateur: Utilisateur, statut: StatutCompte
) -> Utilisateur:
    utilisateur.statut_compte = statut
    session.commit()
    session.refresh(utilisateur)
    return utilisateur
