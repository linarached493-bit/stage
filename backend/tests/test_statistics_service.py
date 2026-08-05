"""Tests du service Statistiques (docs/cahier_des_charges.md, UC5)."""

import json
from datetime import datetime

from app.alerts.models import Alerte, StatutAlerte
from app.auth.models import Role, Utilisateur
from app.configuration.models import AdresseListeNoire, StatutListeNoire
from app.database.enums import Gravite
from app.detection.models import Regle, StatutRegle
from app.eventlog.models import LogEvenement
from app.statistics.service import calculer_statistiques

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def _admin(db_session) -> Utilisateur:
    role = Role(nom="Administrateur")
    utilisateur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def _regle(db_session, auteur: Utilisateur, nom: str, statut: StatutRegle) -> Regle:
    regle = Regle(
        nom=nom,
        type_menace="port_scan",
        condition_declenchement=json.dumps(
            {"indicateur": "ports_distincts_par_source", "seuil": 15, "fenetre_secondes": 60}
        ),
        gravite=Gravite.MOYEN,
        statut=statut,
        auteur=auteur,
    )
    db_session.add(regle)
    db_session.commit()
    return regle


# --- Base vide ---------------------------------------------------------


def test_statistiques_sur_base_vide(db_session):
    resultat = calculer_statistiques(db_session)

    assert resultat["nombre_total_alertes"] == 0
    assert resultat["alertes_par_gravite"] == {}
    assert resultat["alertes_par_statut"] == {}
    assert resultat["alertes_par_type_menace"] == {}
    assert resultat["regles_actives"] == 0
    assert resultat["regles_inactives"] == 0
    assert resultat["utilisateurs_par_role"] == {}
    assert resultat["adresses_liste_noire"] == 0
    assert resultat["nombre_total_logs"] == 0


# --- Alertes -----------------------------------------------------------


def test_nombre_total_alertes(db_session):
    admin = _admin(db_session)
    regle = _regle(db_session, admin, "Port Scan", StatutRegle.ACTIVE)
    db_session.add_all(
        [
            Alerte(
                regle=regle, type_menace="port_scan", ip_source="10.0.0.1", gravite=Gravite.MOYEN
            ),
            Alerte(
                regle=regle, type_menace="port_scan", ip_source="10.0.0.2", gravite=Gravite.ELEVE
            ),
        ]
    )
    db_session.commit()

    assert calculer_statistiques(db_session)["nombre_total_alertes"] == 2


def test_repartition_alertes_par_gravite(db_session):
    admin = _admin(db_session)
    regle = _regle(db_session, admin, "Port Scan", StatutRegle.ACTIVE)
    db_session.add_all(
        [
            Alerte(
                regle=regle, type_menace="port_scan", ip_source="10.0.0.1", gravite=Gravite.MOYEN
            ),
            Alerte(
                regle=regle, type_menace="port_scan", ip_source="10.0.0.2", gravite=Gravite.MOYEN
            ),
            Alerte(
                regle=regle, type_menace="port_scan", ip_source="10.0.0.3", gravite=Gravite.ELEVE
            ),
        ]
    )
    db_session.commit()

    assert calculer_statistiques(db_session)["alertes_par_gravite"] == {"moyen": 2, "eleve": 1}


def test_repartition_alertes_par_statut(db_session):
    admin = _admin(db_session)
    regle = _regle(db_session, admin, "Port Scan", StatutRegle.ACTIVE)
    db_session.add_all(
        [
            Alerte(
                regle=regle,
                type_menace="port_scan",
                ip_source="10.0.0.1",
                gravite=Gravite.MOYEN,
                statut_traitement=StatutAlerte.NOUVELLE,
            ),
            Alerte(
                regle=regle,
                type_menace="port_scan",
                ip_source="10.0.0.2",
                gravite=Gravite.MOYEN,
                statut_traitement=StatutAlerte.TRAITEE,
            ),
        ]
    )
    db_session.commit()

    assert calculer_statistiques(db_session)["alertes_par_statut"] == {"nouvelle": 1, "traitee": 1}


def test_repartition_alertes_par_type_menace(db_session):
    admin = _admin(db_session)
    regle = _regle(db_session, admin, "Port Scan", StatutRegle.ACTIVE)
    db_session.add_all(
        [
            Alerte(
                regle=regle, type_menace="port_scan", ip_source="10.0.0.1", gravite=Gravite.MOYEN
            ),
            Alerte(
                regle=regle, type_menace="syn_flood", ip_source="10.0.0.2", gravite=Gravite.ELEVE
            ),
            Alerte(
                regle=regle, type_menace="syn_flood", ip_source="10.0.0.3", gravite=Gravite.ELEVE
            ),
        ]
    )
    db_session.commit()

    assert calculer_statistiques(db_session)["alertes_par_type_menace"] == {
        "port_scan": 1,
        "syn_flood": 2,
    }


# --- Règles --------------------------------------------------------------


def test_nombre_regles_actives_et_inactives(db_session):
    admin = _admin(db_session)
    _regle(db_session, admin, "Port Scan", StatutRegle.ACTIVE)
    _regle(db_session, admin, "SYN Flood", StatutRegle.ACTIVE)
    _regle(db_session, admin, "ICMP Flood", StatutRegle.INACTIVE)

    resultat = calculer_statistiques(db_session)

    assert resultat["regles_actives"] == 2
    assert resultat["regles_inactives"] == 1


# --- Utilisateurs --------------------------------------------------------


def test_utilisateurs_par_role_inclut_les_roles_sans_membre(db_session):
    role_admin = Role(nom="Administrateur")
    role_lecture = Role(nom="Lecture seule")
    db_session.add_all([role_admin, role_lecture])
    db_session.add(Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role_admin))
    db_session.add(Utilisateur(nom_utilisateur="admin2", mot_de_passe_hash="x", role=role_admin))
    db_session.commit()

    resultat = calculer_statistiques(db_session)["utilisateurs_par_role"]

    assert resultat == {"Administrateur": 2, "Lecture seule": 0}


# --- Liste noire -------------------------------------------------------


def test_adresses_liste_noire_compte_seulement_les_actives(db_session):
    db_session.add_all(
        [
            AdresseListeNoire(adresse_ip="203.0.113.66", statut=StatutListeNoire.ACTIVE),
            AdresseListeNoire(adresse_ip="203.0.113.67", statut=StatutListeNoire.ACTIVE),
            AdresseListeNoire(adresse_ip="203.0.113.68", statut=StatutListeNoire.INACTIVE),
        ]
    )
    db_session.commit()

    assert calculer_statistiques(db_session)["adresses_liste_noire"] == 2


# --- Logs ----------------------------------------------------------------


def test_nombre_total_logs(db_session):
    db_session.add_all(
        [
            LogEvenement(type_evenement="connexion", ip_source="10.0.0.1"),
            LogEvenement(type_evenement="icmp", ip_source="10.0.0.2"),
            LogEvenement(type_evenement="syn", ip_source="10.0.0.3"),
        ]
    )
    db_session.commit()

    assert calculer_statistiques(db_session)["nombre_total_logs"] == 3


# --- Vue d'ensemble combinée -----------------------------------------------


def test_statistiques_combinees_sur_jeu_de_donnees_complet(db_session):
    admin = _admin(db_session)
    regle = _regle(db_session, admin, "Port Scan", StatutRegle.ACTIVE)
    _regle(db_session, admin, "ICMP Flood", StatutRegle.INACTIVE)
    db_session.add(
        Alerte(regle=regle, type_menace="port_scan", ip_source="10.0.0.1", gravite=Gravite.MOYEN)
    )
    db_session.add(AdresseListeNoire(adresse_ip="203.0.113.66"))
    db_session.add(LogEvenement(type_evenement="connexion", ip_source="10.0.0.1"))
    db_session.commit()

    resultat = calculer_statistiques(db_session)

    assert resultat["nombre_total_alertes"] == 1
    assert resultat["regles_actives"] == 1
    assert resultat["regles_inactives"] == 1
    assert resultat["adresses_liste_noire"] == 1
    assert resultat["nombre_total_logs"] == 1
    assert resultat["utilisateurs_par_role"] == {"Administrateur": 1}
