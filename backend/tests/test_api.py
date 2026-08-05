"""Test d'intégration de bout en bout de l'API : connexion, jeton,
consultation protégée des alertes et des règles. Utilise la base SQLite
de test (voir conftest.py) à la place de PostgreSQL, via une
substitution de la dépendance `get_db`.
"""

import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.alerts.models import Alerte
from app.alerts.service import creer_alertes
from app.auth.models import Role, StatutCompte, Utilisateur
from app.auth.security import hash_password
from app.capture.events import EvenementReseau
from app.configuration.models import AdresseListeNoire, ParametreConfiguration
from app.configuration.service import adresses_blacklistees_actives, ports_interdits_actifs
from app.database.enums import Gravite
from app.database.session import get_db
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle
from app.eventlog.models import LogEvenement, NiveauLog
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


# --- Gestion des règles (docs/cahier_des_charges.md, UC3) -------------------

_CONDITION_PORT_SCAN = {
    "indicateur": "ports_distincts_par_source",
    "seuil": 15,
    "fenetre_secondes": 60,
}


def test_creer_regle_refuse_sans_authentification(client):
    reponse = client.post(
        "/v1/regles",
        json={
            "nom": "Port Scan",
            "type_menace": "port_scan",
            "condition_declenchement": _CONDITION_PORT_SCAN,
            "gravite": "moyen",
        },
    )

    assert reponse.status_code == 401


def test_creer_regle_refusee_a_lanalyste(client, db_session):
    """Restriction volontaire de cette étape : seul l'Administrateur peut
    écrire sur les règles (voir app/detection/router.py)."""
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.post(
        "/v1/regles",
        json={
            "nom": "Port Scan",
            "type_menace": "port_scan",
            "condition_declenchement": _CONDITION_PORT_SCAN,
            "gravite": "moyen",
        },
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_creer_regle_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.post(
        "/v1/regles",
        json={
            "nom": "Port Scan",
            "description": "Balayage de ports",
            "type_menace": "port_scan",
            "condition_declenchement": _CONDITION_PORT_SCAN,
            "gravite": "moyen",
        },
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["nom"] == "Port Scan"
    assert corps["statut"] == "active"
    assert corps["condition_declenchement"] == _CONDITION_PORT_SCAN
    assert corps["auteur"] == "admin"


def test_creer_regle_refuse_nom_deja_utilise(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")
    corps_regle = {
        "nom": "Port Scan",
        "type_menace": "port_scan",
        "condition_declenchement": _CONDITION_PORT_SCAN,
        "gravite": "moyen",
    }
    client.post("/v1/regles", json=corps_regle, headers={"Authorization": f"Bearer {jeton}"})

    reponse = client.post(
        "/v1/regles", json=corps_regle, headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 409


def test_creer_regle_refuse_indicateur_inconnu(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.post(
        "/v1/regles",
        json={
            "nom": "Règle bidon",
            "type_menace": "inconnue",
            "condition_declenchement": {"indicateur": "indicateur_inexistant", "seuil": 1},
            "gravite": "moyen",
        },
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 422


def test_consulter_regle_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(_CONDITION_PORT_SCAN),
        gravite=Gravite.MOYEN,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.get(f"/v1/regles/{regle.id}", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    assert reponse.json()["id"] == regle.id
    assert reponse.json()["condition_declenchement"] == _CONDITION_PORT_SCAN


def test_consulter_regle_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.get("/v1/regles/999", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 404


def test_modifier_regle_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(_CONDITION_PORT_SCAN),
        gravite=Gravite.MOYEN,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.put(
        f"/v1/regles/{regle.id}",
        json={"condition_declenchement": {**_CONDITION_PORT_SCAN, "seuil": 30}},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert reponse.json()["condition_declenchement"]["seuil"] == 30


def test_modifier_regle_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.put(
        "/v1/regles/999",
        json={"gravite": "eleve"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 404


def test_modifier_regle_refuse_condition_invalide(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(_CONDITION_PORT_SCAN),
        gravite=Gravite.MOYEN,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.put(
        f"/v1/regles/{regle.id}",
        json={"condition_declenchement": {"indicateur": "indicateur_inexistant", "seuil": 1}},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 422


def test_changer_statut_regle_via_api(client, db_session):
    auteur = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(_CONDITION_PORT_SCAN),
        gravite=Gravite.MOYEN,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.patch(
        f"/v1/regles/{regle.id}/statut",
        json={"statut": "inactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "inactive"


def test_changer_statut_regle_refuse_a_lanalyste(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin_temp")
    regle = Regle(
        nom="Port Scan",
        type_menace="port_scan",
        condition_declenchement=json.dumps(_CONDITION_PORT_SCAN),
        gravite=Gravite.MOYEN,
        auteur=admin,
    )
    db_session.add(regle)
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")
    db_session.commit()

    jeton = _connecter(client, "analyste")
    reponse = client.patch(
        f"/v1/regles/{regle.id}/statut",
        json={"statut": "inactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_changer_statut_regle_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.patch(
        "/v1/regles/999/statut",
        json={"statut": "inactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 404


# --- Gestion des alertes (docs/cahier_des_charges.md, UC8) -----------------


def _creer_regle_pour_alerte(db_session, auteur: Utilisateur) -> Regle:
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
    return regle


def _creer_alerte(db_session, regle: Regle, **overrides) -> Alerte:
    parametres = {
        "regle": regle,
        "type_menace": regle.type_menace,
        "ip_source": "192.168.1.99",
        "gravite": regle.gravite,
    }
    parametres.update(overrides)
    alerte = Alerte(**parametres)
    db_session.add(alerte)
    db_session.commit()
    return alerte


def test_lister_alertes_filtre_par_gravite_via_api(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    _creer_alerte(db_session, regle, gravite=Gravite.MOYEN)
    _creer_alerte(db_session, regle, gravite=Gravite.ELEVE)

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/alertes", params={"gravite": "eleve"}, headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["gravite"] == "eleve"


def test_consulter_alerte_via_api(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)

    jeton = _connecter(client, "admin")
    reponse = client.get(f"/v1/alertes/{alerte.id}", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["id"] == alerte.id
    assert corps["regle"] == "Port Scan"
    assert corps["historique"] == []


def test_consulter_alerte_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.get("/v1/alertes/999", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 404


def test_acquitter_alerte_refuse_sans_authentification(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)

    reponse = client.patch(f"/v1/alertes/{alerte.id}/acquitter", json={})

    assert reponse.status_code == 401


def test_acquitter_alerte_refusee_a_lecture_seule(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/acquitter", json={}, headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 403


def test_acquitter_alerte_via_api(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)

    jeton = _connecter(client, "admin")
    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/acquitter",
        json={"commentaire": "Pris en charge"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["statut_traitement"] == "en_cours"
    assert len(corps["historique"]) == 1
    assert corps["historique"][0]["commentaire"] == "Pris en charge"
    assert corps["historique"][0]["utilisateur"] == "admin"


def test_acquitter_alerte_deja_en_cours_renvoie_conflit(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)
    jeton = _connecter(client, "admin")
    client.patch(
        f"/v1/alertes/{alerte.id}/acquitter", json={}, headers={"Authorization": f"Bearer {jeton}"}
    )

    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/acquitter", json={}, headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 409


def test_fermer_alerte_via_api(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)

    jeton = _connecter(client, "admin")
    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/fermer",
        json={"statut_final": "faux_positif", "commentaire": "Trafic legitime"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["statut_traitement"] == "faux_positif"
    assert corps["historique"][-1]["commentaire"] == "Trafic legitime"


def test_fermer_alerte_refuse_statut_final_invalide(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)

    jeton = _connecter(client, "admin")
    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/fermer",
        json={"statut_final": "en_cours"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 422


def test_fermer_alerte_deja_fermee_renvoie_conflit(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)
    jeton = _connecter(client, "admin")
    client.patch(
        f"/v1/alertes/{alerte.id}/fermer",
        json={"statut_final": "traitee"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/fermer",
        json={"statut_final": "traitee"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 409


def test_fermer_alerte_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.patch(
        "/v1/alertes/999/fermer",
        json={"statut_final": "traitee"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 404


def test_commenter_alerte_via_api(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)

    jeton = _connecter(client, "admin")
    reponse = client.post(
        f"/v1/alertes/{alerte.id}/commentaires",
        json={"commentaire": "Analyse en cours, en attente de confirmation."},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["statut_traitement"] == "nouvelle"
    assert len(corps["historique"]) == 1
    assert corps["historique"][0]["commentaire"] == "Analyse en cours, en attente de confirmation."


def test_commenter_alerte_refuse_a_lecture_seule(client, db_session):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.post(
        f"/v1/alertes/{alerte.id}/commentaires",
        json={"commentaire": "Je ne devrais pas pouvoir faire ceci."},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_historique_accumule_commentaire_puis_acquittement_puis_fermeture_via_api(
    client, db_session
):
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = _creer_regle_pour_alerte(db_session, admin)
    alerte = _creer_alerte(db_session, regle)
    jeton = _connecter(client, "admin")
    entetes = {"Authorization": f"Bearer {jeton}"}

    client.post(
        f"/v1/alertes/{alerte.id}/commentaires",
        json={"commentaire": "Observation initiale"},
        headers=entetes,
    )
    client.patch(f"/v1/alertes/{alerte.id}/acquitter", json={}, headers=entetes)
    reponse = client.patch(
        f"/v1/alertes/{alerte.id}/fermer",
        json={"statut_final": "traitee", "commentaire": "Confirmee et traitee"},
        headers=entetes,
    )

    assert reponse.status_code == 200
    historique = reponse.json()["historique"]
    assert [entree["statut"] for entree in historique] == ["nouvelle", "en_cours", "traitee"]
    assert historique[0]["commentaire"] == "Observation initiale"
    assert historique[2]["commentaire"] == "Confirmee et traitee"


# --- Gestion des logs (docs/cahier_des_charges.md, UC4) ---------------------


def _creer_log(db_session, **overrides) -> LogEvenement:
    parametres = {
        "type_evenement": "connexion",
        "niveau": NiveauLog.INFO,
        "ip_source": "192.168.1.10",
    }
    parametres.update(overrides)
    log = LogEvenement(**parametres)
    db_session.add(log)
    db_session.commit()
    return log


def test_lister_logs_refuse_sans_authentification(client):
    reponse = client.get("/v1/logs")

    assert reponse.status_code == 401


def test_lister_logs_refuse_a_lecture_seule(client, db_session):
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.get("/v1/logs", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 403


def test_lister_logs_accessible_a_ladministrateur_et_a_lanalyste(client, db_session):
    for nom_role, nom_utilisateur in [
        ("Administrateur", "admin"),
        ("Analyste sécurité", "analyste"),
    ]:
        _creer_utilisateur(db_session, nom_role, nom_utilisateur)
        jeton = _connecter(client, nom_utilisateur)

        reponse = client.get("/v1/logs", headers={"Authorization": f"Bearer {jeton}"})

        assert reponse.status_code == 200, f"échec pour le profil {nom_role}"


def test_lister_logs_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    _creer_log(db_session, ip_source="192.168.1.10")
    _creer_log(db_session, ip_source="10.0.0.5")

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/logs", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    assert len(reponse.json()) == 2


def test_lister_logs_filtre_par_niveau_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    _creer_log(db_session, niveau=NiveauLog.INFO)
    _creer_log(db_session, niveau=NiveauLog.ERREUR)

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/logs", params={"niveau": "erreur"}, headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["niveau"] == "erreur"


def test_lister_logs_filtre_par_type_evenement_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    _creer_log(db_session, type_evenement="connexion")
    _creer_log(db_session, type_evenement="echec_authentification")

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/logs",
        params={"type_evenement": "echec_authentification"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["type_evenement"] == "echec_authentification"


def test_lister_logs_filtre_par_periode_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    ancien = datetime(2020, 1, 1, 0, 0, 0)
    recent = datetime.now()
    _creer_log(db_session, horodatage=ancien)
    _creer_log(db_session, horodatage=recent)

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/logs",
        params={"date_debut": (recent - timedelta(hours=1)).isoformat()},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert len(reponse.json()) == 1


def test_rechercher_logs_par_adresse_ip_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    _creer_log(db_session, ip_source="192.168.1.10")
    _creer_log(db_session, ip_source="10.0.0.5")

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/logs",
        params={"adresse_ip": "192.168.1.10"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["ip_source"] == "192.168.1.10"


def test_rechercher_logs_par_texte_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    _creer_log(db_session, type_evenement="connexion", protocole="TCP")
    _creer_log(db_session, type_evenement="icmp", protocole="ICMP")

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/logs", params={"recherche": "ICMP"}, headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["type_evenement"] == "icmp"


def test_consulter_log_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    log = _creer_log(db_session, protocole="TCP", ports="443")

    jeton = _connecter(client, "admin")
    reponse = client.get(f"/v1/logs/{log.id}", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["id"] == log.id
    assert corps["protocole"] == "TCP"
    assert corps["ports"] == "443"


def test_consulter_log_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.get("/v1/logs/999", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 404


def test_consulter_log_refuse_a_lecture_seule(client, db_session):
    log = _creer_log(db_session)
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.get(f"/v1/logs/{log.id}", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 403


# --- Gestion de la configuration et de la liste noire -----------------------
# (docs/cahier_des_charges.md, section 6)


def test_lister_configuration_refuse_sans_authentification(client):
    reponse = client.get("/v1/configuration")

    assert reponse.status_code == 401


def test_lister_configuration_refuse_a_lecture_seule(client, db_session):
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.get("/v1/configuration", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 403


def test_lister_configuration_accessible_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.get("/v1/configuration", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200


def test_modifier_parametre_refusee_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.put(
        "/v1/configuration/interface_surveillee",
        json={"valeur": "eth0"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_modifier_parametre_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.put(
        "/v1/configuration/interface_surveillee",
        json={"valeur": "eth0", "description": "Interface réseau surveillée"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["nom_parametre"] == "interface_surveillee"
    assert corps["valeur"] == "eth0"


def test_consulter_parametre_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    db_session.add(ParametreConfiguration(nom_parametre="fenetre_defaut", valeur="60"))
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/configuration/fenetre_defaut", headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 200
    assert reponse.json()["valeur"] == "60"


def test_consulter_parametre_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.get(
        "/v1/configuration/inexistant", headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 404


def test_consulter_ports_interdits_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    db_session.add(
        ParametreConfiguration(nom_parametre="ports_interdits", valeur=json.dumps([23, 3389]))
    )
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.get(
        "/v1/configuration/ports-interdits", headers={"Authorization": f"Bearer {jeton}"}
    )

    assert reponse.status_code == 200
    assert sorted(reponse.json()["ports"]) == [23, 3389]


def test_modifier_ports_interdits_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.put(
        "/v1/configuration/ports-interdits",
        json={"ports": [23, 3389]},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert sorted(reponse.json()["ports"]) == [23, 3389]


def test_modifier_ports_interdits_refuse_port_invalide(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.put(
        "/v1/configuration/ports-interdits",
        json={"ports": [70000]},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 422


def test_modifier_ports_interdits_refusee_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.put(
        "/v1/configuration/ports-interdits",
        json={"ports": [23]},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_lister_liste_noire_refuse_sans_authentification(client):
    reponse = client.get("/v1/liste-noire")

    assert reponse.status_code == 401


def test_lister_liste_noire_refuse_a_lecture_seule(client, db_session):
    _creer_utilisateur(db_session, "Lecture seule", "lecteur")

    jeton = _connecter(client, "lecteur")
    reponse = client.get("/v1/liste-noire", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 403


def test_ajouter_adresse_liste_noire_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")

    jeton = _connecter(client, "admin")
    reponse = client.post(
        "/v1/liste-noire",
        json={"adresse_ip": "203.0.113.66", "motif_source": "Renseignement manuel"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["adresse_ip"] == "203.0.113.66"
    assert corps["statut"] == "active"


def test_ajouter_adresse_liste_noire_refusee_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")

    jeton = _connecter(client, "analyste")
    reponse = client.post(
        "/v1/liste-noire",
        json={"adresse_ip": "203.0.113.66"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_ajouter_adresse_liste_noire_refuse_doublon(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")
    client.post(
        "/v1/liste-noire",
        json={"adresse_ip": "203.0.113.66"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    reponse = client.post(
        "/v1/liste-noire",
        json={"adresse_ip": "203.0.113.66"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 409


def test_lister_liste_noire_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    db_session.add(AdresseListeNoire(adresse_ip="203.0.113.66"))
    db_session.add(AdresseListeNoire(adresse_ip="198.51.100.10"))
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.get("/v1/liste-noire", headers={"Authorization": f"Bearer {jeton}"})

    assert reponse.status_code == 200
    assert len(reponse.json()) == 2


def test_retirer_adresse_liste_noire_via_api(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    entree = AdresseListeNoire(adresse_ip="203.0.113.66")
    db_session.add(entree)
    db_session.commit()

    jeton = _connecter(client, "admin")
    reponse = client.patch(
        f"/v1/liste-noire/{entree.id}/statut",
        json={"statut": "inactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "inactive"


def test_retirer_adresse_liste_noire_refuse_a_lanalyste(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin_temp")
    entree = AdresseListeNoire(adresse_ip="203.0.113.66")
    db_session.add(entree)
    _creer_utilisateur(db_session, "Analyste sécurité", "analyste")
    db_session.commit()

    jeton = _connecter(client, "analyste")
    reponse = client.patch(
        f"/v1/liste-noire/{entree.id}/statut",
        json={"statut": "inactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 403


def test_retirer_adresse_liste_noire_introuvable(client, db_session):
    _creer_utilisateur(db_session, "Administrateur", "admin")
    jeton = _connecter(client, "admin")

    reponse = client.patch(
        "/v1/liste-noire/999/statut",
        json={"statut": "inactive"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 404


def test_scenario_ip_blacklistee_prise_en_compte_immediate_via_api(client, db_session):
    """Ajout via l'API -> immédiatement visible par le moteur de
    détection, sans redémarrage ni modification de code."""
    admin = _creer_utilisateur(db_session, "Administrateur", "admin")
    regle = Regle(
        nom="IP blacklistée",
        type_menace="ip_blacklistee",
        condition_declenchement=json.dumps({"indicateur": "adresse_dans_liste_noire", "seuil": 1}),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
        auteur=admin,
    )
    db_session.add(regle)
    db_session.commit()

    jeton = _connecter(client, "admin")
    client.post(
        "/v1/liste-noire",
        json={"adresse_ip": "203.0.113.66"},
        headers={"Authorization": f"Bearer {jeton}"},
    )

    evenements = [
        EvenementReseau(
            ip_source="203.0.113.66",
            type_evenement="connexion",
            horodatage=datetime.now(),
            port=443,
        )
    ]
    detections = MoteurDetection(
        [regle], adresses_blacklistees=adresses_blacklistees_actives(db_session)
    ).evaluer(evenements, datetime.now())

    assert len(detections) == 1
