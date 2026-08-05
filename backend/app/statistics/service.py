"""Service dédié aux statistiques.

Aucune entité Statistique n'existe en base : conformément à la décision
déjà actée (docs/preparation_implementation.md, section 3.3 — confirmée
explicitement par ce livrable), toutes les valeurs ci-dessous sont
calculées à la demande par agrégation SQL sur les tables déjà
existantes (Alerte, Règle, Utilisateur, Liste noire, Log), jamais
stockées ni recalculées en arrière-plan.
"""

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.alerts.models import Alerte
from app.auth.models import Role, Utilisateur
from app.configuration.models import AdresseListeNoire, StatutListeNoire
from app.detection.models import Regle, StatutRegle
from app.eventlog.models import LogEvenement


def _repartition(session: Session, colonne: ColumnElement) -> dict[str, int]:
    """Regroupe et compte les lignes selon une colonne (énumération ou
    texte libre). Factorise le motif GROUP BY / COUNT commun aux
    répartitions par gravité, statut et type de menace ci-dessous."""
    lignes = session.query(colonne, func.count()).group_by(colonne).all()
    return {
        (valeur.value if hasattr(valeur, "value") else valeur): total for valeur, total in lignes
    }


def calculer_statistiques(session: Session) -> dict[str, Any]:
    regles_par_statut = _repartition(session, Regle.statut)

    utilisateurs_par_role = dict(
        session.query(Role.nom, func.count(Utilisateur.id))
        .outerjoin(Utilisateur, Utilisateur.role_id == Role.id)
        .group_by(Role.nom)
        .all()
    )

    return {
        "nombre_total_alertes": session.query(Alerte).count(),
        "alertes_par_gravite": _repartition(session, Alerte.gravite),
        "alertes_par_statut": _repartition(session, Alerte.statut_traitement),
        "alertes_par_type_menace": _repartition(session, Alerte.type_menace),
        "regles_actives": regles_par_statut.get(StatutRegle.ACTIVE.value, 0),
        "regles_inactives": regles_par_statut.get(StatutRegle.INACTIVE.value, 0),
        "utilisateurs_par_role": utilisateurs_par_role,
        # Adresses actuellement actives : c'est ce que le moteur de
        # détection considère réellement comme la liste noire courante
        # (voir app/configuration/service.py:adresses_blacklistees_actives).
        "adresses_liste_noire": (
            session.query(AdresseListeNoire)
            .filter(AdresseListeNoire.statut == StatutListeNoire.ACTIVE)
            .count()
        ),
        "nombre_total_logs": session.query(LogEvenement).count(),
    }
