"""Module Analyse (docs/architecture_logicielle.md, section 4.2).

Transforme une liste d'événements réseau bruts en indicateurs
numériques exploitables par le Moteur de détection.
"""

from datetime import datetime, timedelta

from app.capture.events import EvenementReseau


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
    debut_fenetre = maintenant - timedelta(seconds=fenetre_secondes)
    ports = {
        evenement.port
        for evenement in evenements
        if evenement.ip_source == ip_source
        and evenement.port is not None
        and debut_fenetre <= evenement.horodatage <= maintenant
    }
    return len(ports)


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
