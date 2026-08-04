"""Test de bout en bout : événements réseau simulés -> détection -> alerte
persistée. Couvre le flux complet décrit en section 4 de
docs/specifications_techniques.md, sans dépendre d'une capture réseau
réelle ni de PostgreSQL (base SQLite de test, voir tests/conftest.py).
"""

import json
from datetime import datetime, timedelta

from app.alerts.models import Alerte, StatutAlerte
from app.alerts.service import creer_alertes
from app.auth.models import Role, Utilisateur
from app.capture.events import EvenementReseau
from app.configuration.models import AdresseListeNoire
from app.configuration.service import adresses_blacklistees_actives
from app.database.enums import Gravite
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def test_scenario_port_scan_de_bout_en_bout(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(
            {"indicateur": "ports_distincts_par_source", "seuil": 15, "fenetre_secondes": 60}
        ),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    # Simulation d'un balayage de ports : une source sollicite 20 ports en quelques secondes.
    evenements = [
        EvenementReseau(
            ip_source="203.0.113.77",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(3000, 3020))
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)
    alertes = creer_alertes(db_session, detections)

    assert len(alertes) == 1
    alerte_persistee = db_session.query(Alerte).one()
    assert alerte_persistee.ip_source == "203.0.113.77"
    assert alerte_persistee.type_menace == "port_scan"
    assert alerte_persistee.gravite is Gravite.MOYEN
    assert alerte_persistee.statut_traitement is StatutAlerte.NOUVELLE
    assert alerte_persistee.regle.nom == "Port Scan"


def test_trafic_normal_ne_genere_aucune_alerte(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(
            {"indicateur": "ports_distincts_par_source", "seuil": 15, "fenetre_secondes": 60}
        ),
        gravite=Gravite.MOYEN,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    evenements = [
        EvenementReseau(
            ip_source="192.168.1.20", type_evenement="connexion", horodatage=MAINTENANT, port=443
        )
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)
    alertes = creer_alertes(db_session, detections)

    assert alertes == []
    assert db_session.query(Alerte).count() == 0


def test_scenario_ip_blacklistee_de_bout_en_bout(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = Regle(
        nom="IP blacklistée",
        type_menace="ip_blacklistee",
        condition_declenchement=json.dumps({"indicateur": "adresse_dans_liste_noire", "seuil": 1}),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.add(
        AdresseListeNoire(adresse_ip="203.0.113.66", motif_source="Renseignement manuel")
    )
    db_session.commit()

    evenements = [
        EvenementReseau(
            ip_source="203.0.113.66", type_evenement="connexion", horodatage=MAINTENANT, port=443
        )
    ]

    liste_noire = adresses_blacklistees_actives(db_session)
    detections = MoteurDetection([regle], adresses_blacklistees=liste_noire).evaluer(
        evenements, MAINTENANT
    )
    alertes = creer_alertes(db_session, detections)

    assert len(alertes) == 1
    alerte_persistee = db_session.query(Alerte).one()
    assert alerte_persistee.ip_source == "203.0.113.66"
    assert alerte_persistee.type_menace == "ip_blacklistee"
    assert alerte_persistee.gravite is Gravite.ELEVE


def test_scenario_tentatives_repetees_connexion_de_bout_en_bout(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = Regle(
        nom="Tentatives répétées de connexion",
        type_menace="tentatives_repetees_connexion",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_evenements_par_source",
                "type_evenement": "connexion",
                "seuil": 20,
                "fenetre_secondes": 60,
            }
        ),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    # 25 connexions vers le même port en une minute : reconnaissance
    # active ou tentative d'exploitation automatisée.
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.44",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=443,
        )
        for i in range(25)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)
    alertes = creer_alertes(db_session, detections)

    assert len(alertes) == 1
    alerte_persistee = db_session.query(Alerte).one()
    assert alerte_persistee.ip_source == "198.51.100.44"
    assert alerte_persistee.type_menace == "tentatives_repetees_connexion"
    assert alerte_persistee.gravite is Gravite.MOYEN
    assert alerte_persistee.statut_traitement is StatutAlerte.NOUVELLE


def test_scenario_syn_flood_de_bout_en_bout(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = Regle(
        nom="SYN Flood",
        type_menace="syn_flood",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_evenements_par_source",
                "type_evenement": "syn",
                "seuil": 100,
                "fenetre_secondes": 10,
            }
        ),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    # 150 paquets SYN en rafale, sans finalisation de la connexion :
    # saturation de la table de connexions de la cible.
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
    alertes = creer_alertes(db_session, detections)

    assert len(alertes) == 1
    alerte_persistee = db_session.query(Alerte).one()
    assert alerte_persistee.ip_source == "198.51.100.7"
    assert alerte_persistee.type_menace == "syn_flood"
    assert alerte_persistee.gravite is Gravite.ELEVE
    assert alerte_persistee.statut_traitement is StatutAlerte.NOUVELLE


def test_scenario_icmp_flood_de_bout_en_bout(db_session):
    role = Role(nom="Administrateur")
    auteur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    regle = Regle(
        nom="ICMP Flood",
        type_menace="icmp_flood",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_evenements_par_source",
                "type_evenement": "icmp",
                "seuil": 150,
                "fenetre_secondes": 10,
            }
        ),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    # 200 requêtes ICMP Echo Request en rafale : saturation de la bande
    # passante ou des ressources de traitement de la cible.
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.9",
            type_evenement="icmp",
            horodatage=MAINTENANT - timedelta(milliseconds=i * 10),
        )
        for i in range(200)
    ]

    detections = MoteurDetection([regle]).evaluer(evenements, MAINTENANT)
    alertes = creer_alertes(db_session, detections)

    assert len(alertes) == 1
    alerte_persistee = db_session.query(Alerte).one()
    assert alerte_persistee.ip_source == "198.51.100.9"
    assert alerte_persistee.type_menace == "icmp_flood"
    assert alerte_persistee.gravite is Gravite.ELEVE
    assert alerte_persistee.statut_traitement is StatutAlerte.NOUVELLE
