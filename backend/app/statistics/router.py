"""Ressource Statistiques (docs/conception_api_rest.md, section 4.6 ;
docs/cahier_des_charges.md, UC5 « Consulter les statistiques »).

ÉCART SIGNALÉ : la matrice de permissions du cahier des charges
(section 5.4) et le catalogue d'API d'origine (Livrable 6) accordaient
aussi la consultation des statistiques au profil Lecture seule. Cette
étape, plus stricte, la réserve à l'Administrateur et à l'Analyste
sécurité, conformément à la consigne explicite reçue pour ce livrable.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.auth.models import Utilisateur
from app.database.session import get_db
from app.statistics.schemas import StatistiquesOut
from app.statistics.service import calculer_statistiques

router = APIRouter(prefix="/v1/statistiques", tags=["Statistiques"])

_verifier_acces = require_role("Administrateur", "Analyste sécurité")


@router.get("", response_model=StatistiquesOut)
def consulter(
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_acces),
) -> StatistiquesOut:
    return StatistiquesOut(**calculer_statistiques(session))
