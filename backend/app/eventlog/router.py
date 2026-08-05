"""Ressource Logs (docs/conception_api_rest.md, section 4.4 ;
docs/cahier_des_charges.md, UC4 « Consulter l'historique des logs »).

Consultation uniquement (aucun endpoint de création, modification ou
suppression), réservée à l'Administrateur et à l'Analyste sécurité.
Le profil Lecture seule n'y a pas accès : ceci tranche explicitement
une ambiguïté déjà signalée entre le cahier des charges (accès
« Limité ») et la conception UML (aucun accès) — voir
docs/conception_api_rest.md, section 10.4 — dans le sens le plus
restrictif, conformément à la consigne de ce livrable.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.auth.models import Utilisateur
from app.database.session import get_db
from app.eventlog.models import LogEvenement, NiveauLog
from app.eventlog.schemas import LogOut
from app.eventlog.service import lister_logs, obtenir_log

router = APIRouter(prefix="/v1/logs", tags=["Logs"])

ROLES_LECTURE = ("Administrateur", "Analyste sécurité")
_verifier_acces = require_role(*ROLES_LECTURE)


@router.get("", response_model=list[LogOut])
def lister(
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    niveau: NiveauLog | None = None,
    type_evenement: str | None = None,
    adresse_ip: str | None = None,
    recherche: str | None = None,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces),
) -> list[LogEvenement]:
    return lister_logs(
        session,
        date_debut=date_debut,
        date_fin=date_fin,
        niveau=niveau,
        type_evenement=type_evenement,
        adresse_ip=adresse_ip,
        recherche=recherche,
    )


@router.get("/{log_id}", response_model=LogOut)
def consulter(
    log_id: int,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces),
) -> LogEvenement:
    log = obtenir_log(session, log_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log introuvable.")
    return log
