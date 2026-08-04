"""Test d'intégration de bout en bout de l'API : connexion, jeton,
consultation protégée des alertes et des règles. Utilise la base SQLite
de test (voir conftest.py) à la place de PostgreSQL, via une
substitution de la dépendance `get_db`.
"""

import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.alerts.service import creer_alertes
from app.auth.models import Role, StatutCompte, Utilisateur
from app.auth.security import hash_password
from app.capture.events import EvenementReseau
from app.database.enums import Gravite
from app.database.session import get_db
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle
from app.main import app


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _creer_utilisateur(db_session, nom_role: str, nom_utilisateur: str) -> Utilisateur:
    role = Role(nom=nom_role)
    utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        mot_de_passe_hash=hash_password("Passw0rd!"),
        role=role,
        statut_compte=StatutCompte.ACTIF,
    )
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def _connecter(client: TestClient, nom_utilisateur: str) -> str:
    reponse = client.post(
        "/v1/auth/login", data={"username": nom_utilisateur, "password": "Passw0rd!"}
    )
    assert reponse.status_code == 200
    return reponse.json()["access_token"]


def test_login_refuse_identifiants_invalides(client):
    reponse = client.post("/v1/auth/login", data={"username": "inconnu", "password": "x"})

    assert reponse.status_code == 401


def test_login_puis_consultation_session(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.get("/v1/auth/session", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    assert reponse.json() == {"id": 1, "nom_utilisateur": "analyste", "role": "Analyste sécurité"}


def test_alertes_refuse_acces_sans_authentification(client):
    reponse = client.get("/v1/alertes")

    assert reponse.status_code == 401


def test_alertes_accessible_par_les_trois_profils(client, db_session):
    for nom_role, nom_utilisateur in [
        ("Administrateur", "admin"),
        ("Analyste sécurité", "analyste"),
        ("Lecture seule", "lecteur"),
    ]:
        _creer_utilisateur(db_session, nom_role, nom_utilisateur)
        jeton = _connecter(client, nom_utilisateur)

        reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

        assert reponse.status_code == 200, f"échec pour le profil {nom_role}"


def test_scenario_complet_scan_de_ports_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
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

    maintenant = datetime.now()
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.23",
            type_evenement="connexion",
            horodatage=maintenant - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(4000, 4020))
    ]
    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "198.51.100.23"
    assert alertes[0]["type_menace"] == "port_scan"
    assert alertes[0]["statut_traitement"] == "nouvelle"


def test_regles_refusees_au_profil_lecture_seule(client, db_session):
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.get("/v1/regles", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 403


def test_regles_accessible_a_lanalyste(client, db_session):
    auteur = _creer_utilisateur(db_session, "Analyste sécurité", "analyste")
    db_session.add(
        Regle(
            nom="Brute Force",
            type_menace="brute_force",
            condition_declenchement=json.dumps({"indicateur": "echecs_consecutifs", "seuil": 5}),
            gravite=Gravite.ELEVE,
            auteur=auteur,
        )
    )
    db_session.commit()

    jeton = _connecter(client, "analyste")
    reponse = client.get("/v1/regles", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    assert len(reponse.json()) == 1
    assert reponse.json()[0]["nom"] == "Brute Force"


def test_scenario_tentatives_repetees_connexion_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
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

    maintenant = datetime.now()
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.44",
            type_evenement="connexion",
            horodatage=maintenant - timedelta(seconds=i),
            port=443,
        )
        for i in range(25)
    ]
    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "198.51.100.44"
    assert alertes[0]["type_menace"] == "tentatives_repetees_connexion"


def test_scenario_syn_flood_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
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

    maintenant = datetime.now()
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.7",
            type_evenement="syn",
            horodatage=maintenant - timedelta(milliseconds=i * 10),
            port=80,
        )
        for i in range(150)
    ]
    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "198.51.100.7"
    assert alertes[0]["type_menace"] == "syn_flood"
    assert alertes[0]["gravite"] == "eleve"
