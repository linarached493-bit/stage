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
