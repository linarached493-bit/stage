"""Module Moteur de détection (docs/architecture_logicielle.md, section 4.3).

Évalue les règles actives sur un lot d'événements réseau et produit des
détections positives. Chaque type d'indicateur est enregistré dans
`CALCULATEURS_INDICATEURS` : ajouter une nouvelle menace ne modifie pas
la boucle d'évaluation (principe ouvert/fermé), conformément à la
décision de garder l'entité Règle générique
(docs/preparation_implementation.md, section 3.3).
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.analysis.indicators import (
    nombre_echecs_authentification_consecutifs,
    nombre_ports_distincts,
)
from app.capture.events import EvenementReseau
from app.detection.models import Regle, StatutRegle


@dataclass(frozen=True, slots=True)
class DetectionPositive:
    regle: Regle
    ip_source: str


CalculateurIndicateur = Callable[[list[EvenementReseau], str, dict, datetime], int]


def _calculer_ports_distincts(
    evenements: list[EvenementReseau], ip_source: str, condition: dict, maintenant: datetime
) -> int:
    return nombre_ports_distincts(
        evenements, ip_source, condition.get("fenetre_secondes", 60), maintenant
    )


def _calculer_echecs_consecutifs(
    evenements: list[EvenementReseau], ip_source: str, condition: dict, maintenant: datetime
) -> int:
    return nombre_echecs_authentification_consecutifs(evenements, ip_source)


CALCULATEURS_INDICATEURS: dict[str, CalculateurIndicateur] = {
    "ports_distincts_par_source": _calculer_ports_distincts,
    "echecs_consecutifs": _calculer_echecs_consecutifs,
}


class MoteurDetection:
    def __init__(self, regles: list[Regle]):
        self._regles = [regle for regle in regles if regle.statut is StatutRegle.ACTIVE]

    def evaluer(
        self, evenements: list[EvenementReseau], maintenant: datetime
    ) -> list[DetectionPositive]:
        sources = {evenement.ip_source for evenement in evenements}
        detections: list[DetectionPositive] = []

        for regle in self._regles:
            condition = json.loads(regle.condition_declenchement)
            calculateur = CALCULATEURS_INDICATEURS.get(condition["indicateur"])
            if calculateur is None:
                continue

            seuil = condition["seuil"]
            for ip_source in sources:
                valeur = calculateur(evenements, ip_source, condition, maintenant)
                if valeur >= seuil:
                    detections.append(DetectionPositive(regle=regle, ip_source=ip_source))

        return detections
