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
from dataclasses import dataclass, field
from datetime import datetime

from app.analysis.indicators import (
    nombre_echecs_authentification_consecutifs,
    nombre_evenements_avec_port_interdit,
    nombre_evenements_par_source,
    nombre_ports_distincts,
    nombre_total_evenements_par_source,
    nombre_types_evenements_distincts,
)
from app.capture.events import EvenementReseau
from app.detection.models import Regle, StatutRegle


@dataclass(frozen=True, slots=True)
class DetectionPositive:
    regle: Regle
    ip_source: str


@dataclass(frozen=True, slots=True)
class ContexteDetection:
    """Données auxiliaires qu'un indicateur peut consulter en plus des
    événements observés : des ensembles de référence alimentés par la
    Configuration (docs/architecture_logicielle.md, section 4.10), utilisés
    par les règles fondées sur une appartenance à un ensemble plutôt que
    sur un seuil temporel (IP blacklistée, section 7.6 ; ports interdits,
    section 7.9 du cahier des charges)."""

    adresses_blacklistees: frozenset[str] = field(default_factory=frozenset)
    ports_interdits: frozenset[int] = field(default_factory=frozenset)


CalculateurIndicateur = Callable[
    [list[EvenementReseau], str, dict, datetime, ContexteDetection], int
]


def _calculer_ports_distincts(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return nombre_ports_distincts(
        evenements, ip_source, condition.get("fenetre_secondes", 60), maintenant
    )


def _calculer_echecs_consecutifs(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return nombre_echecs_authentification_consecutifs(evenements, ip_source)


def _calculer_appartenance_liste_noire(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return 1 if ip_source in contexte.adresses_blacklistees else 0


def _calculer_port_interdit(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return nombre_evenements_avec_port_interdit(evenements, ip_source, contexte.ports_interdits)


def _calculer_types_evenements_distincts(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return nombre_types_evenements_distincts(
        evenements, ip_source, condition.get("fenetre_secondes", 60), maintenant
    )


def _calculer_volume_total(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return nombre_total_evenements_par_source(
        evenements, ip_source, condition.get("fenetre_secondes", 60), maintenant
    )


def _calculer_nombre_evenements(
    evenements: list[EvenementReseau],
    ip_source: str,
    condition: dict,
    maintenant: datetime,
    contexte: ContexteDetection,
) -> int:
    return nombre_evenements_par_source(
        evenements,
        ip_source,
        condition.get("type_evenement", "connexion"),
        condition.get("fenetre_secondes", 60),
        maintenant,
    )


CALCULATEURS_INDICATEURS: dict[str, CalculateurIndicateur] = {
    "ports_distincts_par_source": _calculer_ports_distincts,
    "echecs_consecutifs": _calculer_echecs_consecutifs,
    "adresse_dans_liste_noire": _calculer_appartenance_liste_noire,
    # Indicateur générique : sert les règles Tentatives répétées de
    # connexion, SYN Flood et ICMP Flood, distinguées uniquement par le
    # `type_evenement` dans la condition de la règle (voir
    # app/analysis/indicators.py, docstring de nombre_evenements_par_source).
    "nombre_evenements_par_source": _calculer_nombre_evenements,
    # Même principe qu'"adresse_dans_liste_noire", appliqué au port :
    # appartenance à un ensemble configurable porté par le Contexte.
    "port_interdit_utilise": _calculer_port_interdit,
    # Même fenêtre glissante que "ports_distincts_par_source", appliquée
    # à la diversité des types d'événements plutôt qu'aux ports.
    "types_evenements_distincts_par_source": _calculer_types_evenements_distincts,
    # Même fenêtre glissante, mais volume brut sans distinction de type :
    # complémentaire de "types_evenements_distincts_par_source" (diversité)
    # et de "nombre_evenements_par_source" (fréquence d'UN type précis).
    "nombre_total_evenements_par_source": _calculer_volume_total,
}


class MoteurDetection:
    def __init__(
        self,
        regles: list[Regle],
        adresses_blacklistees: frozenset[str] = frozenset(),
        ports_interdits: frozenset[int] = frozenset(),
    ):
        self._regles = [regle for regle in regles if regle.statut is StatutRegle.ACTIVE]
        self._contexte = ContexteDetection(
            adresses_blacklistees=adresses_blacklistees, ports_interdits=ports_interdits
        )

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
                valeur = calculateur(evenements, ip_source, condition, maintenant, self._contexte)
                if valeur >= seuil:
                    detections.append(DetectionPositive(regle=regle, ip_source=ip_source))

        return detections
