import json
from datetime import datetime, timedelta

from app.capture.events import EvenementReseau
from app.database.enums import Gravite
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def _regle_port_scan(seuil: int = 15) -> Regle:
    return Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(
            {"indicateur": "ports_distincts_par_source", "seuil": seuil, "fenetre_secondes": 60}
        ),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
    )


def _regle_brute_force(seuil: int = 5) -> Regle:
    return Regle(
        nom="Brute Force",
        type_menace="brute_force",
        condition_declenchement=json.dumps({"indicateur": "echecs_consecutifs", "seuil": seuil}),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
    )


def _regle_ip_blacklistee() -> Regle:
    return Regle(
        nom="IP blacklistée",
        type_menace="ip_blacklistee",
        condition_declenchement=json.dumps({"indicateur": "adresse_dans_liste_noire", "seuil": 1}),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
    )


def test_moteur_detecte_un_port_scan_simule():
    regle = _regle_port_scan(seuil=15)
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.99",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(1000, 1020))
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "192.168.1.99"
    assert detections[0].regle is regle


def test_moteur_detecte_une_attaque_brute_force_simulee():
    regle = _regle_brute_force(seuil=5)
    evenements = [
        EvenementReseau(
            ip_source="10.0.0.7",
            type_evenement="echec_authentification",
            horodatage=MAINTENANT - timedelta(seconds=i),
        )
        for i in range(6)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "10.0.0.7"
    assert detections[0].regle.type_menace == "brute_force"


def test_moteur_ne_declenche_rien_sous_le_seuil():
    regle = _regle_port_scan(seuil=15)
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.10",
            type_evenement="connexion",
            horodatage=MAINTENANT,
            port=port,
        )
        for port in (80, 443, 22)  # trafic normal : 3 ports seulement
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_moteur_ignore_les_regles_inactives():
    regle = _regle_port_scan(seuil=15)
    regle.statut = StatutRegle.INACTIVE
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.99",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(1000, 1020))
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_moteur_evalue_plusieurs_regles_et_sources_independamment():
    evenements_scan = [
        EvenementReseau(
            ip_source="192.168.1.99",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(2000, 2020))
    ]
    evenements_brute_force = [
        EvenementReseau(
            ip_source="10.0.0.7",
            type_evenement="echec_authentification",
            horodatage=MAINTENANT - timedelta(seconds=i),
        )
        for i in range(6)
    ]

    detections = MoteurDetection([_regle_port_scan(), _regle_brute_force()]).evaluer(
        evenements_scan + evenements_brute_force, MAINTENANT
    )

    sources_detectees = {d.ip_source for d in detections}
    assert sources_detectees == {"192.168.1.99", "10.0.0.7"}


def test_moteur_detecte_une_communication_avec_une_ip_blacklistee():
    regle = _regle_ip_blacklistee()
    evenements = [
        EvenementReseau(
            ip_source="203.0.113.66", type_evenement="connexion", horodatage=MAINTENANT, port=443
        )
    ]

    detections = MoteurDetection(
        [regle], adresses_blacklistees=frozenset({"203.0.113.66"})
    ).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "203.0.113.66"
    assert detections[0].regle.type_menace == "ip_blacklistee"


def test_moteur_ignore_une_ip_non_blacklistee():
    regle = _regle_ip_blacklistee()
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.5", type_evenement="connexion", horodatage=MAINTENANT, port=443
        )
    ]

    detections = MoteurDetection(
        [regle], adresses_blacklistees=frozenset({"203.0.113.66"})
    ).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_moteur_sans_liste_noire_fournie_ne_detecte_rien_par_defaut():
    """Compatibilité ascendante : construire le moteur sans préciser la
    liste noire (comme le fait le code déjà existant) ne doit jamais
    lever d'erreur ni déclencher cette règle par accident."""
    regle = _regle_ip_blacklistee()
    evenements = [
        EvenementReseau(
            ip_source="203.0.113.66", type_evenement="connexion", horodatage=MAINTENANT, port=443
        )
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []
