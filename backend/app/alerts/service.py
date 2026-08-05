"""Module Gestion des alertes (docs/architecture_logicielle.md, section 4.4).

Couvre la génération des alertes à partir du Moteur de détection
(`creer_alertes`, déjà existant) ainsi que leur cycle de vie côté
administration : consultation filtrée, acquittement, fermeture et
commentaires, avec conservation de l'historique (docs/cahier_des_charges.md,
UC8 « Qualifier une alerte »).
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.alerts.models import Alerte, HistoriqueAlerte, StatutAlerte
from app.auth.models import Utilisateur
from app.database.enums import Gravite
from app.detection.engine import DetectionPositive

STATUTS_FERMETURE_VALIDES = (StatutAlerte.TRAITEE, StatutAlerte.FAUX_POSITIF)


class TransitionAlerteInvalide(Exception):
    """La transition demandée n'est pas autorisée depuis le statut courant
    de l'alerte (ex. acquitter une alerte déjà traitée)."""


class StatutFermetureInvalide(Exception):
    """Le statut final demandé pour une fermeture n'est pas un statut
    terminal valide (`STATUTS_FERMETURE_VALIDES`)."""


def creer_alertes(session: Session, detections: list[DetectionPositive]) -> list[Alerte]:
    alertes = [
        Alerte(
            regle=detection.regle,
            type_menace=detection.regle.type_menace,
            ip_source=detection.ip_source,
            gravite=detection.regle.gravite,
        )
        for detection in detections
    ]
    session.add_all(alertes)
    session.commit()
    return alertes


def lister_alertes(
    session: Session,
    *,
    gravite: Gravite | None = None,
    statut: StatutAlerte | None = None,
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
) -> list[Alerte]:
    requete = session.query(Alerte)
    if gravite is not None:
        requete = requete.filter(Alerte.gravite == gravite)
    if statut is not None:
        requete = requete.filter(Alerte.statut_traitement == statut)
    if date_debut is not None:
        requete = requete.filter(Alerte.horodatage_detection >= date_debut)
    if date_fin is not None:
        requete = requete.filter(Alerte.horodatage_detection <= date_fin)
    return requete.order_by(Alerte.horodatage_detection.desc()).all()


def obtenir_alerte(session: Session, alerte_id: int) -> Alerte | None:
    return session.get(Alerte, alerte_id)


def _ajouter_entree_historique(
    session: Session,
    alerte: Alerte,
    statut: StatutAlerte,
    utilisateur: Utilisateur,
    commentaire: str | None,
) -> None:
    """Toute alerte créée par le moteur reste consultable : cette
    fonction ne fait jamais que muter son statut et ajouter une ligne
    d'historique, jamais la supprimer."""
    session.add(
        HistoriqueAlerte(
            alerte=alerte, statut=statut, commentaire=commentaire, utilisateur=utilisateur
        )
    )
    alerte.statut_traitement = statut
    alerte.utilisateur_qualification = utilisateur
    alerte.date_derniere_maj_statut = datetime.now(UTC)


def acquitter_alerte(
    session: Session, alerte: Alerte, utilisateur: Utilisateur, commentaire: str | None = None
) -> Alerte:
    if alerte.statut_traitement is not StatutAlerte.NOUVELLE:
        raise TransitionAlerteInvalide(
            f"Impossible d'acquitter une alerte au statut {alerte.statut_traitement.value!r} "
            f"(seul le statut {StatutAlerte.NOUVELLE.value!r} peut être acquitté)."
        )
    _ajouter_entree_historique(session, alerte, StatutAlerte.EN_COURS, utilisateur, commentaire)
    session.commit()
    session.refresh(alerte)
    return alerte


def fermer_alerte(
    session: Session,
    alerte: Alerte,
    utilisateur: Utilisateur,
    statut_final: StatutAlerte,
    commentaire: str | None = None,
) -> Alerte:
    if statut_final not in STATUTS_FERMETURE_VALIDES:
        valeurs_attendues = ", ".join(s.value for s in STATUTS_FERMETURE_VALIDES)
        raise StatutFermetureInvalide(
            f"Statut de fermeture invalide : {statut_final.value!r} "
            f"(attendu : {valeurs_attendues})."
        )
    if alerte.statut_traitement in STATUTS_FERMETURE_VALIDES:
        raise TransitionAlerteInvalide("Cette alerte est déjà fermée.")

    _ajouter_entree_historique(session, alerte, statut_final, utilisateur, commentaire)
    session.commit()
    session.refresh(alerte)
    return alerte


def ajouter_commentaire(
    session: Session, alerte: Alerte, utilisateur: Utilisateur, commentaire: str
) -> Alerte:
    """Journalise un commentaire sans changer le statut courant de l'alerte."""
    _ajouter_entree_historique(session, alerte, alerte.statut_traitement, utilisateur, commentaire)
    session.commit()
    session.refresh(alerte)
    return alerte
