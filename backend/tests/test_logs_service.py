"""Tests de la gestion des logs (docs/cahier_des_charges.md, UC4)."""

import json
from datetime import datetime, timedelta

from app.alerts.models import Alerte
from app.auth.models import Role, Utilisateur
from app.database.enums import Gravite
from app.detection.models import Regle, StatutRegle
from app.eventlog.models import LogEvenement, NiveauLog
from app.eventlog.service import lister_logs, obtenir_log

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def _log(db_session, **overrides) -> LogEvenement:
    parametres = {
        "horodatage": MAINTENANT,
        "type_evenement": "connexion",
        "niveau": NiveauLog.INFO,
        "ip_source": "192.168.1.10",
    }
    parametres.update(overrides)
    log = LogEvenement(**parametres)
    db_session.add(log)
    db_session.commit()
    return log


# --- Consultation globale et tri ------------------------------------------


def test_lister_logs_sans_filtre(db_session):
    _log(db_session)
    _log(db_session, ip_source="10.0.0.5")

    assert len(lister_logs(db_session)) == 2


def test_lister_logs_tries_du_plus_recent_au_plus_ancien(db_session):
    ancien = _log(db_session, horodatage=MAINTENANT - timedelta(hours=1))
    recent = _log(db_session, horodatage=MAINTENANT)

    resultat = lister_logs(db_session)

    assert [log.id for log in resultat] == [recent.id, ancien.id]


def test_obtenir_log_introuvable_retourne_none(db_session):
    assert obtenir_log(db_session, 999) is None


def test_obtenir_log_existant(db_session):
    log = _log(db_session)

    assert obtenir_log(db_session, log.id).id == log.id


# --- Filtre par période ------------------------------------------------------


def test_lister_logs_filtre_par_periode(db_session):
    _log(db_session, horodatage=MAINTENANT - timedelta(days=10))
    _log(db_session, horodatage=MAINTENANT)

    resultat = lister_logs(
        db_session,
        date_debut=MAINTENANT - timedelta(days=1),
        date_fin=MAINTENANT + timedelta(days=1),
    )

    assert len(resultat) == 1


# --- Filtre par niveau ---------------------------------------------------


def test_lister_logs_filtre_par_niveau(db_session):
    _log(db_session, niveau=NiveauLog.INFO)
    _log(db_session, niveau=NiveauLog.ERREUR)

    resultat = lister_logs(db_session, niveau=NiveauLog.ERREUR)

    assert len(resultat) == 1
    assert resultat[0].niveau is NiveauLog.ERREUR


# --- Filtre par type d'événement --------------------------------------------


def test_lister_logs_filtre_par_type_evenement(db_session):
    _log(db_session, type_evenement="connexion")
    _log(db_session, type_evenement="echec_authentification")

    resultat = lister_logs(db_session, type_evenement="echec_authentification")

    assert len(resultat) == 1
    assert resultat[0].type_evenement == "echec_authentification"


# --- Recherche par adresse IP ------------------------------------------------


def test_lister_logs_recherche_par_adresse_ip_source_ou_destination(db_session):
    _log(db_session, ip_source="192.168.1.10")
    _log(db_session, ip_source="10.0.0.5", ip_destination="192.168.1.10")
    _log(db_session, ip_source="172.16.0.1")

    resultat = lister_logs(db_session, adresse_ip="192.168.1.10")

    assert len(resultat) == 2


def test_lister_logs_recherche_par_adresse_ip_partielle(db_session):
    _log(db_session, ip_source="192.168.1.10")
    _log(db_session, ip_source="10.0.0.5")

    resultat = lister_logs(db_session, adresse_ip="192.168.1")

    assert len(resultat) == 1


# --- Recherche textuelle --------------------------------------------------


def test_lister_logs_recherche_textuelle(db_session):
    _log(db_session, type_evenement="connexion", protocole="TCP")
    _log(db_session, type_evenement="icmp", protocole="ICMP")

    resultat = lister_logs(db_session, recherche="ICMP")

    assert len(resultat) == 1
    assert resultat[0].type_evenement == "icmp"


# --- Combinaison de filtres --------------------------------------------------


def test_lister_logs_combine_plusieurs_filtres(db_session):
    _log(db_session, niveau=NiveauLog.ERREUR, type_evenement="echec_authentification")
    _log(db_session, niveau=NiveauLog.ERREUR, type_evenement="connexion")
    _log(db_session, niveau=NiveauLog.INFO, type_evenement="echec_authentification")

    resultat = lister_logs(
        db_session, niveau=NiveauLog.ERREUR, type_evenement="echec_authentification"
    )

    assert len(resultat) == 1


# --- Séparation logs techniques / alertes de sécurité ------------------------


def test_log_associe_a_une_alerte_reste_consultable_par_reference(db_session):
    """Le log référence l'alerte par identifiant sans fusionner les deux
    concepts (séparation logs techniques / alertes de sécurité)."""
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
    alerte = Alerte(
        regle=regle, type_menace="port_scan", ip_source="192.168.1.10", gravite=Gravite.MOYEN
    )
    db_session.add_all([regle, alerte])
    db_session.commit()

    log = _log(db_session, alerte=alerte)

    assert obtenir_log(db_session, log.id).alerte_id == alerte.id
