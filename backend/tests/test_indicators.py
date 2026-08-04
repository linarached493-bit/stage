from datetime import datetime, timedelta

from app.analysis.indicators import (
    nombre_echecs_authentification_consecutifs,
    nombre_ports_distincts,
)
from app.capture.events import EvenementReseau

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def _evenement_connexion(ip_source: str, port: int, secondes_avant: int = 0) -> EvenementReseau:
    return EvenementReseau(
        ip_source=ip_source,
        type_evenement="connexion",
        horodatage=MAINTENANT - timedelta(seconds=secondes_avant),
        port=port,
    )


def test_nombre_ports_distincts_compte_les_ports_uniques_dans_la_fenetre():
    evenements = [
        _evenement_connexion("192.168.1.50", port, secondes_avant=i)
        for i, port in enumerate(range(20, 40))
    ]

    resultat = nombre_ports_distincts(
        evenements, "192.168.1.50", fenetre_secondes=60, maintenant=MAINTENANT
    )

    assert resultat == 20


def test_nombre_ports_distincts_ignore_les_evenements_hors_fenetre():
    evenements = [
        _evenement_connexion("192.168.1.50", 22, secondes_avant=5),
        _evenement_connexion("192.168.1.50", 80, secondes_avant=500),  # hors fenêtre de 60s
    ]

    resultat = nombre_ports_distincts(
        evenements, "192.168.1.50", fenetre_secondes=60, maintenant=MAINTENANT
    )

    assert resultat == 1


def test_nombre_ports_distincts_ignore_les_autres_sources():
    evenements = [
        _evenement_connexion("192.168.1.50", 22),
        _evenement_connexion("10.0.0.9", 23),
    ]

    resultat = nombre_ports_distincts(
        evenements, "192.168.1.50", fenetre_secondes=60, maintenant=MAINTENANT
    )

    assert resultat == 1


def _evenement_auth(ip_source: str, reussi: bool, secondes_avant: int) -> EvenementReseau:
    return EvenementReseau(
        ip_source=ip_source,
        type_evenement="authentification_reussie" if reussi else "echec_authentification",
        horodatage=MAINTENANT - timedelta(seconds=secondes_avant),
    )


def test_echecs_consecutifs_compte_jusqua_la_derniere_reussite():
    evenements = [
        _evenement_auth("10.0.0.5", reussi=True, secondes_avant=100),
        _evenement_auth("10.0.0.5", reussi=False, secondes_avant=40),
        _evenement_auth("10.0.0.5", reussi=False, secondes_avant=30),
        _evenement_auth("10.0.0.5", reussi=False, secondes_avant=20),
    ]

    resultat = nombre_echecs_authentification_consecutifs(evenements, "10.0.0.5")

    assert resultat == 3


def test_echecs_consecutifs_zero_si_derniere_tentative_reussie():
    evenements = [
        _evenement_auth("10.0.0.5", reussi=False, secondes_avant=30),
        _evenement_auth("10.0.0.5", reussi=True, secondes_avant=10),
    ]

    resultat = nombre_echecs_authentification_consecutifs(evenements, "10.0.0.5")

    assert resultat == 0
