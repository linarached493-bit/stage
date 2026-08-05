"""Logique métier de la ressource Logs (docs/cahier_des_charges.md,
UC4 « Consulter l'historique des logs »).

Lecture seule : ce module n'expose volontairement aucune fonction de
création, modification ou suppression. Les logs sont produits par les
modules Capture réseau / Analyse (non encore branchés sur cette table,
voir docs/plan_de_developpement.md) ; ce service se limite à leur
consultation.
"""

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.eventlog.models import LogEvenement, NiveauLog


def lister_logs(
    session: Session,
    *,
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    niveau: NiveauLog | None = None,
    type_evenement: str | None = None,
    adresse_ip: str | None = None,
    recherche: str | None = None,
) -> list[LogEvenement]:
    requete = session.query(LogEvenement)

    if date_debut is not None:
        requete = requete.filter(LogEvenement.horodatage >= date_debut)
    if date_fin is not None:
        requete = requete.filter(LogEvenement.horodatage <= date_fin)
    if niveau is not None:
        requete = requete.filter(LogEvenement.niveau == niveau)
    if type_evenement is not None:
        requete = requete.filter(LogEvenement.type_evenement == type_evenement)
    if adresse_ip is not None:
        motif = f"%{adresse_ip}%"
        requete = requete.filter(
            or_(LogEvenement.ip_source.ilike(motif), LogEvenement.ip_destination.ilike(motif))
        )
    if recherche is not None:
        motif = f"%{recherche}%"
        requete = requete.filter(
            or_(
                LogEvenement.type_evenement.ilike(motif),
                LogEvenement.protocole.ilike(motif),
                LogEvenement.ip_source.ilike(motif),
                LogEvenement.ip_destination.ilike(motif),
            )
        )

    return requete.order_by(LogEvenement.horodatage.desc()).all()


def obtenir_log(session: Session, log_id: int) -> LogEvenement | None:
    return session.get(LogEvenement, log_id)
