"""Ressource Règles (docs/conception_api_rest.md, section 4.5).

Seule la consultation (UC3, en lecture) est implémentée ici. La
création/modification des règles reste à faire (voir
docs/plan_de_developpement.md, tâche API-5).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database.session import get_db
from app.detection.models import Regle
from app.detection.schemas import RegleOut

router = APIRouter(prefix="/v1/regles", tags=["Règles"])

ROLES_AUTORISES = ("Administrateur", "Analyste sécurité")
_verifier_acces = require_role(*ROLES_AUTORISES)


@router.get("", response_model=list[RegleOut])
def lister_regles(
    session: Session = Depends(get_db),
    _utilisateur=Depends(_verifier_acces),
) -> list[Regle]:
    return session.query(Regle).order_by(Regle.nom).all()
