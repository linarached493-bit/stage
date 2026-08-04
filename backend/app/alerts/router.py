"""Ressource Alertes (docs/conception_api_rest.md, section 4.3).

Seul le cas d'utilisation UC2 (visualiser les alertes) est implémenté
ici. La qualification d'une alerte (UC8, PATCH .../statut) reste à
faire (voir docs/plan_de_developpement.md, tâche API-3).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.alerts.models import Alerte
from app.alerts.schemas import AlerteOut
from app.auth.dependencies import require_role
from app.database.session import get_db

router = APIRouter(prefix="/v1/alertes", tags=["Alertes"])

ROLES_LECTURE = ("Administrateur", "Analyste sécurité", "Lecture seule")
_verifier_acces_lecture = require_role(*ROLES_LECTURE)


@router.get("", response_model=list[AlerteOut])
def lister_alertes(
    session: Session = Depends(get_db),
    _utilisateur=Depends(_verifier_acces_lecture),
) -> list[Alerte]:
    return session.query(Alerte).order_by(Alerte.horodatage_detection.desc()).all()
