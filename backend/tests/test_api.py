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
from app.configuration.models import ParametreConfiguration
from app.configuration.service import ports_interdits_actifs
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


def test_scenario_icmp_flood_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
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

    maintenant = datetime.now()
    evenements = [
        EvenementReseau(
            ip_source="198.51.100.9",
            type_evenement="icmp",
            horodatage=maintenant - timedelta(milliseconds=i * 10),
        )
        for i in range(200)
    ]
    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "198.51.100.9"
    assert alertes[0]["type_menace"] == "icmp_flood"
    assert alertes[0]["gravite"] == "eleve"


def test_scenario_ports_interdits_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Utilisation de ports interdits",
        type_menace="ports_interdits",
        condition_declenchement=json.dumps({"indicateur": "port_interdit_utilise", "seuil": 1}),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.add(
        ParametreConfiguration(nom_parametre="ports_interdits", valeur=json.dumps([23, 3389]))
    )
    db_session.commit()

    maintenant = datetime.now()
    evenements = [
        EvenementReseau(
            ip_source="192.168.1.40", type_evenement="connexion", horodatage=maintenant, port=3389
        )
    ]
    ports_interdits = ports_interdits_actifs(db_session)
    detections = MoteurDetection([regle], ports_interdits=ports_interdits).evaluer(
        evenements, maintenant
    )
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "192.168.1.40"
    assert alertes[0]["type_menace"] == "ports_interdits"
    assert alertes[0]["gravite"] == "moyen"


def test_scenario_activite_inhabituelle_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Activité réseau inhabituelle",
        type_menace="activite_inhabituelle",
        condition_declenchement=json.dumps(
            {
                "indicateur": "types_evenements_distincts_par_source",
                "seuil": 3,
                "fenetre_secondes": 30,
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
            ip_source="192.168.1.60",
            type_evenement="connexion",
            horodatage=maintenant - timedelta(seconds=1),
            port=443,
        ),
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="echec_authentification",
            horodatage=maintenant - timedelta(seconds=2),
        ),
        EvenementReseau(
            ip_source="192.168.1.60",
            type_evenement="syn",
            horodatage=maintenant - timedelta(seconds=3),
            port=22,
        ),
    ]
    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "192.168.1.60"
    assert alertes[0]["type_menace"] == "activite_inhabituelle"
    assert alertes[0]["gravite"] == "moyen"


def test_scenario_trafic_anormal_simple_visible_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Trafic anormal simple",
        type_menace="trafic_anormal_simple",
        condition_declenchement=json.dumps(
            {
                "indicateur": "nombre_total_evenements_par_source",
                "seuil": 25,
                "fenetre_secondes": 30,
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
            ip_source="192.168.1.70",
            type_evenement="connexion",
            horodatage=maintenant - timedelta(seconds=i),
            port=443,
        )
        for i in range(30)
    ]
    detections = MoteurDetection([regle]).evaluer(evenements, maintenant)
    creer_alertes(db_session, detections)

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/alertes", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    alertes = reponse.json()
    assert len(alertes) == 1
    assert alertes[0]["ip_source"] == "192.168.1.70"
    assert alertes[0]["type_menace"] == "trafic_anormal_simple"
    assert alertes[0]["gravite"] == "moyen"


# --- Ressource Utilisateurs (docs/cahier_des_charges.md, UC6) --------------


def test_lister_utilisateurs_refuse_sans_authentification(client):
    reponse = client.get("/v1/utilisateurs")

    assert reponse.status_code == 401


def test_lister_utilisateurs_refuse_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.get("/v1/utilisateurs", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 403


def test_lister_utilisateurs_accessible_a_ladministrateur(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/utilisateurs", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    noms = {u["nom_utilisateur"] for u in reponse.json()}
    assert noms == {"admin"}


def test_creer_utilisateur_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    role_analyste = Role(nom="Analyste sécurité")
    db_session.add(role_analyste)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.post(
        "/v1/utilisateurs",
        json={
            "nom_utilisateur": "nouvel_analyste",
            "mot_de_passe": "Passw0rd!",
            "role_id": role_analyste.id,
        },
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["nom_utilisateur"] == "nouvel_analyste"
    assert corps["role"] == "Analyste sécurité"
    assert corps["statut_compte"] == "actif"
    assert "mot_de_passe" not in corps
    assert "mot_de_passe_hash" not in corps


def test_creer_utilisateur_refuse_nom_deja_utilise(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.post(
        "/v1/utilisateurs",
        json={"nom_utilisateur": "admin", "mot_de_passe": "Autre1234!", "role_id": 1},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 409


def test_creer_utilisateur_refuse_role_inexistant(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.post(
        "/v1/utilisateurs",
        json={"nom_utilisateur": "nouveau", "mot_de_passe": "Passw0rd!", "role_id": 999},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 422


def test_creer_utilisateur_refuse_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.post(
        "/v1/utilisateurs",
        json={"nom_utilisateur": "intrus", "mot_de_passe": "Passw0rd!", "role_id": 1},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_consulter_utilisateur_via_api(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.get(
        f"/v1/utilisateurs/{admin.id}", headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 200
    assert reponse.json()["id"] == admin.id


def test_consulter_utilisateur_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/utilisateurs/999", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 404


def test_modifier_utilisateur_change_de_role_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    cible = _creer_utilisateur(db_session, "Lecture seule", "lecteur")
    role_analyste = Role(nom="Analyste sécurité")
    db_session.add(role_analyste)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.put(
        f"/v1/utilisateurs/{cible.id}",
        json={"role_id": role_analyste.id},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert reponse.json()["role"] == "Analyste sécurité"


def test_changer_statut_utilisateur_desactive_empeche_la_connexion(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    cible = _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "admin")
    reponse = client.patch(
        f"/v1/utilisateurs/{cible.id}/statut",
        json={"statut_compte": "desactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert reponse.json()["statut_compte"] == "desactive"

    # Vérification croisée avec l'Authentification déjà existante : un
    # compte désactivé ne peut plus se connecter.
    reponse_login = client.post(
        "/v1/auth/login", data={"username": "analyste", "password": "Passw0rd!"}
    )
    assert reponse_login.status_code == 401
