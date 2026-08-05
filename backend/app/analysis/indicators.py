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

    Indicateur générique de fréquence, réutilisé tel quel par plusieurs
    règles distinguées uniquement par la valeur de `type_evenement` dans
    leur condition : Tentatives répétées de connexion
    (`type_evenement="connexion"`, docs/cahier_des_charges.md, section 7.5),
    SYN Flood (`type_evenement="syn"`, section 7.2) et ICMP Flood
    (`type_evenement="icmp"`, section 7.3) — ces trois règles ont été
    ajoutées sans aucune modification de cette fonction, uniquement par
    de nouvelles lignes Règle (voir docs/preparation_implementation.md,
    section 3.3 sur la généricité de l'entité Règle).
    """
    return sum(
        1
        for evenement in _evenements_dans_la_fenetre(
            evenements, ip_source, fenetre_secondes, maintenant
        )
        if evenement.type_evenement == type_evenement
    )


def nombre_types_evenements_distincts(
    evenements: list[EvenementReseau],
    ip_source: str,
    fenetre_secondes: int,
    maintenant: datetime,
) -> int:
    """Nombre de types d'événements distincts (connexion, échec
    d'authentification, syn, icmp, ...) observés pour `ip_source` sur la
    fenêtre des `fenetre_secondes` dernières secondes avant `maintenant`.

    Indicateur utilisé par la règle Activité réseau inhabituelle
    (docs/cahier_des_charges.md, section 7.7). Définition volontairement
    simple, sans apprentissage automatique ni profil statistique appris :
    un trafic normal provenant d'une même source est en général homogène
    (un client web se limite presque toujours à des connexions, par
    exemple) ; une source qui mélange en peu de temps un nombre inhabituel
    de types d'événements différents s'écarte de cet usage typique et
    constitue un signal simple de reconnaissance ou d'activité
    multi-vecteurs. Réutilise le même filtre de fenêtre glissante que
    `nombre_ports_distincts`, en comptant les types d'événements distincts
    au lieu des ports distincts.
    """
    types = {
        evenement.type_evenement
        for evenement in _evenements_dans_la_fenetre(
            evenements, ip_source, fenetre_secondes, maintenant
        )
    }
    return len(types)


def nombre_evenements_avec_port_interdit(
    evenements: list[EvenementReseau],
    ip_source: str,
    ports_interdits: frozenset[int],
) -> int:
    """Nombre d'événements de `ip_source` dont le port utilisé figure dans
    `ports_interdits`.

    Indicateur générique d'appartenance à un ensemble de ports fourni de
    l'extérieur (et non figé dans le code), utilisé par la règle
    Utilisation de ports interdits (docs/cahier_des_charges.md,
    section 7.9). Aucune fenêtre temporelle : une seule communication
    sur un port interdit suffit à qualifier l'événement, contrairement
    aux indicateurs volumétriques ci-dessus.

    Suit le même principe que la règle IP blacklistée (comparaison à un
    ensemble de référence porté par `ContexteDetection`, voir
    app/detection/engine.py), mais appliqué au port plutôt qu'à
    l'adresse IP source ; réutilisable pour toute future règle fondée
    sur l'appartenance du port à un ensemble configurable (ports
    autorisés, ports sensibles, etc.).
    """
    return sum(
        1
        for evenement in evenements
        if evenement.ip_source == ip_source
        and evenement.port is not None
        and evenement.port in ports_interdits
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
