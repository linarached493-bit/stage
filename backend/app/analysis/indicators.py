"""Module Analyse (docs/architecture_logicielle.md, section 4.2).

Transforme une liste d'événements réseau bruts en indicateurs
numériques exploitables par le Moteur de détection.
"""

from collections.abc import Iterable
from datetime import datetime, timedelta

from app.capture.events import EvenementReseau


def _evenements_dans_la_fenetre(
    evenements: Iterable[EvenementReseau],
    ip_source: str,
    fenetre_secondes: int,
    maintenant: datetime,
) -> list[EvenementReseau]:
    """Sous-ensemble des événements de `ip_source` observés dans les
    `fenetre_secondes` dernières secondes avant `maintenant`.

    Filtre commun à plusieurs indicateurs fondés sur une fenêtre
    d'observation glissante (Port Scan, tentatives répétées de
    connexion, et les futures menaces volumétriques comme SYN/ICMP
    Flood — voir `nombre_evenements_par_source`).
    """
    debut_fenetre = maintenant - timedelta(seconds=fenetre_secondes)
    return [
        evenement
        for evenement in evenements
        if evenement.ip_source == ip_source and debut_fenetre <= evenement.horodatage <= maintenant
    ]


def nombre_ports_distincts(
    evenements: list[EvenementReseau],
    ip_source: str,
    fenetre_secondes: int,
    maintenant: datetime,
) -> int:
    """Nombre de ports distincts sollicités par `ip_source` sur la fenêtre
    des `fenetre_secondes` dernières secondes avant `maintenant`.

    Indicateur utilisé par la règle Port Scan (docs/cahier_des_charges.md,
    section 7.1).
    """
    ports = {
        evenement.port
        for evenement in _evenements_dans_la_fenetre(
            evenements, ip_source, fenetre_secondes, maintenant
        )
        if evenement.port is not None
    }
    return len(ports)


def nombre_evenements_par_source(
    evenements: list[EvenementReseau],
    ip_source: str,
    type_evenement: str,
    fenetre_secondes: int,
    maintenant: datetime,
) -> int:
    """Nombre d'événements d'un type donné (`type_evenement`) observés pour
    `ip_source` sur la fenêtre des `fenetre_secondes` dernières secondes.

    Indicateur générique de fréquence, utilisé par la règle Tentatives
    répétées de connexion avec `type_evenement="connexion"`
    (docs/cahier_des_charges.md, section 7.5). Sa généricité permet de
    couvrir plus tard SYN Flood et ICMP Flood par simple paramétrage
    d'une nouvelle règle (`type_evenement="syn"` / `"icmp"`), sans
    modification de code (voir docs/preparation_implementation.md,
    section 3.3 sur la généricité de l'entité Règle).
    """
    return sum(
        1
        for evenement in _evenements_dans_la_fenetre(
            evenements, ip_source, fenetre_secondes, maintenant
        )
        if evenement.type_evenement == type_evenement
    )


def nombre_echecs_authentification_consecutifs(
    evenements: list[EvenementReseau],
    ip_source: str,
) -> int:
    """Nombre d'échecs d'authentification consécutifs les plus récents pour
    `ip_source`, jusqu'à la première tentative réussie (ou le début de
    l'historique).

    Indicateur utilisé par la règle Brute Force (docs/cahier_des_charges.md,
    section 7.4).
    """
    evenements_source = sorted(
        (e for e in evenements if e.ip_source == ip_source),
        key=lambda e: e.horodatage,
    )

    compteur = 0
    for evenement in reversed(evenements_source):
        if evenement.type_evenement == "echec_authentification":
            compteur += 1
        elif evenement.type_evenement == "authentification_reussie":
            break
    return compteur
