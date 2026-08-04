"""Module Gestion des alertes (docs/architecture_logicielle.md, section 4.4).

Transforme les détections positives du Moteur de détection en alertes
persistées, conformément au diagramme de séquence « Génération d'une
alerte » (docs/conception_uml.md, section 4.3).
"""

from sqlalchemy.orm import Session

from app.alerts.models import Alerte
from app.detection.engine import DetectionPositive


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
