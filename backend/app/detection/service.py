"""Logique métier de la ressource Règles (docs/cahier_des_charges.md,
cas d'utilisation UC3 « Configurer une règle de détection »).
"""

import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.auth.models import Utilisateur
from app.database.enums import Gravite
from app.detection.engine import CALCULATEURS_INDICATEURS
from app.detection.models import Regle, StatutRegle


class NomRegleDejaUtilise(Exception):
    """Violation de la contrainte d'unicité sur `nom`
    (docs/conception_base_de_donnees.md, section 6.1)."""


class ConditionDeclenchementInvalide(Exception):
    """La condition fournie ne référence aucun indicateur connu du
    moteur de détection, ou lui manque un champ requis."""


def valider_condition_declenchement(condition: dict) -> None:
    """Rejette toute condition dont l'indicateur n'est pas enregistré dans
    le moteur de détection (`CALCULATEURS_INDICATEURS`), seule source de
    vérité réutilisée ici plutôt que dupliquée. C'est ce qui garantit
    qu'une règle valide est immédiatement exploitable par le moteur sans
    aucune modification du code des indicateurs (voir
    app/detection/engine.py)."""
    indicateur = condition.get("indicateur")
    if indicateur not in CALCULATEURS_INDICATEURS:
        raise ConditionDeclenchementInvalide(
            f"Indicateur inconnu du moteur de détection : {indicateur!r}."
        )
    seuil = condition.get("seuil")
    if not isinstance(seuil, int) or isinstance(seuil, bool):
        raise ConditionDeclenchementInvalide("Le champ 'seuil' est requis et doit être un entier.")


def lister_regles(session: Session) -> list[Regle]:
    return session.query(Regle).order_by(Regle.nom).all()


def obtenir_regle(session: Session, regle_id: int) -> Regle | None:
    return session.get(Regle, regle_id)


def _verifier_nom_disponible(
    session: Session, nom: str, regle_id_exclue: int | None = None
) -> None:
    requete = session.query(Regle).filter(Regle.nom == nom)
    if regle_id_exclue is not None:
        requete = requete.filter(Regle.id != regle_id_exclue)
    if requete.first() is not None:
        raise NomRegleDejaUtilise(nom)


def creer_regle(
    session: Session,
    *,
    nom: str,
    description: str | None,
    type_menace: str,
    condition_declenchement: dict,
    gravite: Gravite,
    auteur: Utilisateur,
) -> Regle:
    valider_condition_declenchement(condition_declenchement)
    _verifier_nom_disponible(session, nom)

    regle = Regle(
        nom=nom,
        description=description,
        type_menace=type_menace,
        condition_declenchement=json.dumps(condition_declenchement),
        gravite=gravite,
        auteur=auteur,
    )
    session.add(regle)
    session.commit()
    session.refresh(regle)
    return regle


def modifier_regle(
    session: Session,
    regle: Regle,
    *,
    auteur: Utilisateur,
    nom: str | None = None,
    description: str | None = None,
    type_menace: str | None = None,
    condition_declenchement: dict | None = None,
    gravite: Gravite | None = None,
) -> Regle:
    if nom is not None:
        _verifier_nom_disponible(session, nom, regle_id_exclue=regle.id)
        regle.nom = nom
    if description is not None:
        regle.description = description
    if type_menace is not None:
        regle.type_menace = type_menace
    if condition_declenchement is not None:
        valider_condition_declenchement(condition_declenchement)
        regle.condition_declenchement = json.dumps(condition_declenchement)
    if gravite is not None:
        regle.gravite = gravite

    regle.auteur = auteur
    regle.date_derniere_modification = datetime.now(UTC)
    session.commit()
    session.refresh(regle)
    return regle


def changer_statut_regle(
    session: Session, regle: Regle, statut: StatutRegle, *, auteur: Utilisateur
) -> Regle:
    regle.statut = statut
    regle.auteur = auteur
    regle.date_derniere_modification = datetime.now(UTC)
    session.commit()
    session.refresh(regle)
    return regle
