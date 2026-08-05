"""Tests de la Capture réseau (docs/plan_de_developpement.md, tâche CAP-1).

Aucun test ne réalise de capture réseau réelle (nécessiterait Npcap /
root, non disponibles ici) : tous construisent des paquets Scapy en
mémoire, ce qui suffit à valider entièrement la logique de
transformation (`paquet_vers_evenement`, `traiter_paquets`), seule
responsabilité de ce module.
"""

import json
from datetime import UTC, datetime, timedelta

from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import Ether

from app.alerts.models import Alerte, StatutAlerte
from app.alerts.service import creer_alertes
from app.auth.models import Role, Utilisateur
from app.capture.events import EvenementReseau
from app.capture.sniffer import paquet_vers_evenement, traiter_paquets
from app.database.enums import Gravite
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle

HORODATAGE_FIXE = 1_700_000_000.0


def _horodatage_attendu() -> datetime:
    return datetime.fromtimestamp(HORODATAGE_FIXE, tz=UTC)


def _paquet_tcp(flags: str, dport: int = 443, src: str = "192.168.1.10") -> object:
    paquet = IP(src=src, dst="10.0.0.1") / TCP(dport=dport, flags=flags)
    paquet.time = HORODATAGE_FIXE
    return paquet


def _paquet_udp(dport: int = 53, src: str = "192.168.1.10") -> object:
    paquet = IP(src=src, dst="10.0.0.1") / UDP(dport=dport)
    paquet.time = HORODATAGE_FIXE
    return paquet


def _paquet_icmp(src: str = "192.168.1.10") -> object:
    paquet = IP(src=src, dst="10.0.0.1") / ICMP()
    paquet.time = HORODATAGE_FIXE
    return paquet


# --- Transformation paquet -> événement -------------------------------------


def test_paquet_tcp_syn_pur_devient_evenement_syn():
    evenement = paquet_vers_evenement(_paquet_tcp(flags="S", dport=443))

    assert evenement == EvenementReseau(
        ip_source="192.168.1.10",
        ip_destination="10.0.0.1",
        type_evenement="syn",
        horodatage=_horodatage_attendu(),
        port=443,
        protocole="TCP",
    )


def test_paquet_tcp_etabli_devient_evenement_connexion():
    """Un SYN-ACK (poignée de main déjà entamée) n'est pas un SYN pur :
    il est classé comme connexion, pas comme signal de flood."""
    evenement = paquet_vers_evenement(_paquet_tcp(flags="SA", dport=443))

    assert evenement.type_evenement == "connexion"
    assert evenement.port == 443
    assert evenement.protocole == "TCP"


def test_paquet_tcp_ack_seul_devient_evenement_connexion():
    evenement = paquet_vers_evenement(_paquet_tcp(flags="A", dport=22))

    assert evenement.type_evenement == "connexion"


def test_paquet_udp_devient_evenement_connexion():
    evenement = paquet_vers_evenement(_paquet_udp(dport=53))

    assert evenement == EvenementReseau(
        ip_source="192.168.1.10",
        ip_destination="10.0.0.1",
        type_evenement="connexion",
        horodatage=_horodatage_attendu(),
        port=53,
        protocole="UDP",
    )


def test_paquet_icmp_devient_evenement_icmp():
    evenement = paquet_vers_evenement(_paquet_icmp())

    assert evenement == EvenementReseau(
        ip_source="192.168.1.10",
        ip_destination="10.0.0.1",
        type_evenement="icmp",
        horodatage=_horodatage_attendu(),
        port=None,
        protocole="ICMP",
    )


# --- Rejet des paquets non pris en charge -----------------------------------


def test_paquet_sans_couche_ip_est_rejete():
    assert paquet_vers_evenement(Ether()) is None


def test_paquet_ip_sans_protocole_reconnu_est_rejete():
    paquet = IP(src="192.168.1.10", dst="10.0.0.1")
    paquet.time = HORODATAGE_FIXE

    assert paquet_vers_evenement(paquet) is None


# --- Transmission au gestionnaire --------------------------------------------


def test_traiter_paquets_ne_transmet_que_les_paquets_reconnus():
    evenements_recus = []
    paquets = [
        _paquet_tcp(flags="S", dport=80),
        Ether(),  # rejeté
        _paquet_icmp(),
    ]

    traiter_paquets(paquets, evenements_recus.append)

    assert len(evenements_recus) == 2
    assert evenements_recus[0].type_evenement == "syn"
    assert evenements_recus[1].type_evenement == "icmp"


# --- Compatibilité avec le moteur de détection existant ---------------------


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


def test_paquets_captures_declenchent_la_regle_port_scan_sans_modification_du_moteur():
    maintenant = _horodatage_attendu()
    paquets = [_paquet_tcp(flags="S", dport=port) for port in range(2000, 2020)]
    evenements = []
    traiter_paquets(paquets, evenements.append)

    detections = MoteurDetection([_regle_port_scan(seuil=15)]).evaluer(evenements, maintenant)

    assert len(detections) == 1
    assert detections[0].ip_source == "192.168.1.10"


def test_paquets_captures_declenchent_la_regle_syn_flood_sans_modification_du_moteur():
    paquets = [_paquet_tcp(flags="S", dport=80) for _ in range(150)]
    for decalage, paquet in enumerate(paquets):
        paquet.time = HORODATAGE_FIXE + decalage * 0.01

    evenements = []
    traiter_paquets(paquets, evenements.append)
    maintenant = max(e.horodatage for e in evenements)

    detections = MoteurDetection([_regle_syn_flood(seuil=100)]).evaluer(evenements, maintenant)

    assert len(detections) == 1
    assert detections[0].regle.type_menace == "syn_flood"


# --- Scénario complet : capture -> événement -> moteur -> alerte -----------


def test_scenario_complet_capture_jusqua_lalerte_persistee(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = _regle_port_scan(seuil=15)
    regle.auteur = auteur
    db_session.add(regle)
    db_session.commit()

    # Simule un balayage de ports réel : 20 paquets TCP SYN vers des ports
    # distincts, capturés puis convertis en événements.
    paquets = [_paquet_tcp(flags="S", dport=port) for port in range(3000, 3020)]
    for decalage, paquet in enumerate(paquets):
        paquet.time = HORODATAGE_FIXE + decalage * 0.01
    evenements = []
    traiter_paquets(paquets, evenements.append)
    maintenant = max(e.horodatage for e in evenements) + timedelta(seconds=1)

    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    alertes = creer_alertes(db_session, detections)

    assert len(alertes) == 1
    alerte_persistee = db_session.query(Alerte).one()
    assert alerte_persistee.ip_source == "192.168.1.10"
    assert alerte_persistee.type_menace == "port_scan"
    assert alerte_persistee.statut_traitement is StatutAlerte.NOUVELLE
