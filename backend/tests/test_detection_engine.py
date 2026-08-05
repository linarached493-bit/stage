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


def _regle_tentatives_repetees_connexion(seuil: int = 20) -> Regle:
    return Regle(
        nom="Tentatives répétées de connexion",
        type_menace="tentatives_repetees_connexion",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_evenements_par_source",
                "type_evenement": "connexion",
                "seuil": seuil,
                "fenetre_secondes": 60,
            }
        ),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
    )


def _regle_syn_flood(seuil: int = 100) -> Regle:
    return Regle(
        nom="SYN Flood",
        type_menace="syn_flood",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_evenements_par_source",
                "type_evenement": "syn",
                "seuil": seuil,
                "fenetre_secondes": 10,
            }
        ),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
    )


def _regle_icmp_flood(seuil: int = 150) -> Regle:
    return Regle(
        nom="ICMP Flood",
        type_menace="icmp_flood",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_evenements_par_source",
                "type_evenement": "icmp",
                "seuil": seuil,
                "fenetre_secondes": 10,
            }
        ),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
    )


def _regle_ports_interdits() -> Regle:
    return Regle(
        nom="Utilisation de ports interdits",
        type_menace="ports_interdits",
        condition_declenchement=json.dumps({"indicateur": "port_interdit_utilise", "seuil": 1}),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
    )


def _regle_activite_inhabituelle(seuil: int = 3) -> Regle:
    return Regle(
        nom="Activité réseau inhabituelle",
        type_menace="activite_inhabituelle",
        condition_declenchement=json.dumps(
            {
                "indicateur": "types_evenements_distincts_par_source",
                "seuil": seuil,
                "fenetre_secondes": 30,
            }
        ),
        gravite=Gravite.MOYEN,
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


def test_moteur_detecte_des_tentatives_repetees_de_connexion():
    regle = _regle_tentatives_repetees_connexion(seuil=20)
    # Même port sollicité 25 fois : un Port Scan (ports distincts) ne le
    # détecterait pas, mais la fréquence de connexion, si.
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.30",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=443,
        )
        for i in range(25)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "192.168.1.30"
    assert detections[0].regle.type_menace == "tentatives_repetees_connexion"


def test_moteur_ne_declenche_pas_tentatives_repetees_sous_le_seuil():
    regle = _regle_tentatives_repetees_connexion(seuil=20)
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.30",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=443,
        )
        for i in range(5)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_moteur_detecte_un_syn_flood_simule():
    regle = _regle_syn_flood(seuil=100)
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.7",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
            port=80,
        )
        for i in range(150)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "198.51.100.7"
    assert detections[0].regle.type_menace == "syn_flood"


def test_moteur_ne_declenche_pas_syn_flood_sous_le_seuil():
    regle = _regle_syn_flood(seuil=100)
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.7",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
            port=80,
        )
        for i in range(10)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_syn_flood_et_tentatives_repetees_sont_independants():
    """Même indicateur générique, `type_evenement` différent : les deux
    règles ne doivent réagir qu'à leur propre type d'événement."""
    evenements_syn = [
        EvenementReseau(
            ip_source="198.51.100.7",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
            port=80,
        )
        for i in range(150)
    ]
    evenements_connexion = [
        EvenementReseau(
            ip_source="192.168.1.30",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=443,
        )
        for i in range(25)
    ]

    detections = MoteurDetection(
        [_regle_syn_flood(seuil=100), _regle_tentatives_repetees_connexion(seuil=20)]
    ).evaluer(evenements_syn + evenements_connexion, MAINTENANT)

    resultats = {(d.regle.type_menace, d.ip_source) for d in detections}
    assert resultats == {
        ("syn_flood", "198.51.100.7"),
        ("tentatives_repetees_connexion", "192.168.1.30"),
    }


def test_moteur_detecte_un_icmp_flood_simule():
    regle = _regle_icmp_flood(seuil=150)
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.9",
            type_evenement="icmp",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
        )
        for i in range(200)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "198.51.100.9"
    assert detections[0].regle.type_menace == "icmp_flood"


def test_moteur_ne_declenche_pas_icmp_flood_sous_le_seuil():
    regle = _regle_icmp_flood(seuil=150)
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.9",
            type_evenement="icmp",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
        )
        for i in range(20)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_icmp_flood_independant_des_autres_menaces_volumetriques():
    """Même indicateur générique que SYN Flood et Tentatives répétées de
    connexion : chaque règle ne doit réagir qu'à son propre
    `type_evenement`, même quand les trois trafics sont mélangés."""
    evenements_icmp = [
        EvenementReseau(
            ip_source="198.51.100.9",
            type_evenement="icmp",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
        )
        for i in range(200)
    ]
    evenements_syn = [
        EvenementReseau(
            ip_source="198.51.100.7",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
            port=80,
        )
        for i in range(150)
    ]
    evenements_connexion = [
        EvenementReseau(
            ip_source="192.168.1.30",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=443,
        )
        for i in range(25)
    ]

    detections = MoteurDetection(
        [
            _regle_icmp_flood(seuil=150),
            _regle_syn_flood(seuil=100),
            _regle_tentatives_repetees_connexion(seuil=20),
        ]
    ).evaluer(evenements_icmp + evenements_syn + evenements_connexion, MAINTENANT)

    resultats = {(d.regle.type_menace, d.ip_source) for d in detections}
    assert resultats == {
        ("icmp_flood", "198.51.100.9"),
        ("syn_flood", "198.51.100.7"),
        ("tentatives_repetees_connexion", "192.168.1.30"),
    }


def test_moteur_detecte_une_utilisation_de_port_interdit():
    regle = _regle_ports_interdits()
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.40", type_evenement="connexion", horodatage=MAINTENANT, port=3389
        )
    ]

    detections = MoteurDetection([regle], ports_interdits=frozenset({23, 3389})).evaluer(
        evenements, MAINTENANT
    )

    assert len(detections) == 1
    assert detections[0].ip_source == "192.168.1.40"
    assert detections[0].regle.type_menace == "ports_interdits"


def test_moteur_ne_declenche_rien_si_seuls_des_ports_autorises_sont_utilises():
    regle = _regle_ports_interdits()
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.40", type_evenement="connexion", horodatage=MAINTENANT, port=443
        ),
        EvenementReseau(
            ip_source="192.168.1.40", type_evenement="connexion", horodatage=MAINTENANT, port=80
        ),
    ]

    detections = MoteurDetection([regle], ports_interdits=frozenset({23, 3389})).evaluer(
        evenements, MAINTENANT
    )

    assert detections == []


def test_moteur_sans_ports_interdits_fournis_ne_detecte_rien_par_defaut():
    """Compatibilité ascendante, comme pour la liste noire : construire
    le moteur sans préciser les ports interdits ne doit jamais lever
    d'erreur ni déclencher cette règle par accident."""
    regle = _regle_ports_interdits()
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.40", type_evenement="connexion", horodatage=MAINTENANT, port=3389
        )
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_ports_interdits_independant_des_autres_menaces():
    """Une communication sur un port interdit ne doit pas, à elle seule,
    déclencher les règles Port Scan ou Tentatives répétées de connexion,
    et inversement."""
    evenements_port_interdit = [
        EvenementReseau(
            ip_source="192.168.1.40", type_evenement="connexion", horodatage=MAINTENANT, port=3389
        )
    ]
    evenements_scan = [
        EvenementReseau(
            ip_source="192.168.1.99",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(1000, 1020))
    ]

    detections = MoteurDetection(
        [_regle_ports_interdits(), _regle_port_scan(seuil=15)],
        ports_interdits=frozenset({3389}),
    ).evaluer(evenements_port_interdit + evenements_scan, MAINTENANT)

    resultats = {(d.regle.type_menace, d.ip_source) for d in detections}
    assert resultats == {
        ("ports_interdits", "192.168.1.40"),
        ("port_scan", "192.168.1.99"),
    }


def test_moteur_detecte_une_activite_reseau_inhabituelle():
    regle = _regle_activite_inhabituelle(seuil=3)
    # Une même source mélange connexion, échec d'authentification et SYN
    # en quelques secondes : combinaison atypique pour un hôte normal.
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=1),
            port=443,
        ),
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="echec_authentification",
            horodatage=MAINTENANT - timedelta(seconds=2),
        ),
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(seconds=3),
            port=22,
        ),
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert len(detections) == 1
    assert detections[0].ip_source == "192.168.1.60"
    assert detections[0].regle.type_menace == "activite_inhabituelle"


def test_moteur_ne_declenche_rien_sur_trafic_homogene_meme_volumineux():
    """Absence de faux positif : un trafic important mais d'un seul type
    (comportement normal d'un client) ne doit pas déclencher la règle,
    même si le volume est élevé."""
    regle = _regle_activite_inhabituelle(seuil=3)
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=443,
        )
        for i in range(50)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)

    assert detections == []


def test_activite_inhabituelle_independante_des_autres_menaces():
    """Un mélange de types d'événements sur une source ne doit pas, à lui
    seul, déclencher les règles volumétriques (SYN Flood ici), et
    inversement."""
    evenements_inhabituels = [
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=1),
            port=443,
        ),
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="echec_authentification",
            horodatage=MAINTENANT - timedelta(seconds=2),
        ),
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(seconds=3),
            port=22,
        ),
    ]
    evenements_syn_flood = [
        EvenementReseau(
            ip_source="198.51.100.7",
            type_evenement="syn",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
            port=80,
        )
        for i in range(150)
    ]

    detections = MoteurDetection(
        [_regle_activite_inhabituelle(seuil=3), _regle_syn_flood(seuil=100)]
    ).evaluer(evenements_inhabituels + evenements_syn_flood, MAINTENANT)

    resultats = {(d.regle.type_menace, d.ip_source) for d in detections}
    assert resultats == {
        ("activite_inhabituelle", "192.168.1.60"),
        ("syn_flood", "198.51.100.7"),
    }


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
