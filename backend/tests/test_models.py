"""Vérifie que le schéma de données (docs/conception_base_de_donnees.md)
se crée correctement et que les relations et contraintes principales
fonctionnent comme spécifié.
"""

import json

import pytest
from sqlalchemy.exc import IntegrityError

from app.alerts.models import Alerte, StatutAlerte
from app.auth.models import Role, StatutCompte, Utilisateur
from app.configuration.models import AdresseListeNoire, ParametreConfiguration
from app.database.enums import Gravite
from app.detection.models import Regle, StatutRegle
from app.eventlog.models import LogEvenement


def _creer_utilisateur_admin(db_session) -> Utilisateur:
    role = Role(nom="Administrateur", description="Acces complet")
    utilisateur = Utilisateur(
        nom_utilisateur="admin",
        mot_de_passe_hash="hash-factice",
        role=role,
        statut_compte=StatutCompte.ACTIF,
    )
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def test_role_nom_unique(db_session):
    db_session.add(Role(nom="Administrateur"))
    db_session.add(Role(nom="Administrateur"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_utilisateur_rattache_a_un_role(db_session):
    utilisateur = _creer_utilisateur_admin(db_session)

    assert utilisateur.id is not None
    assert utilisateur.role.nom == "Administrateur"
    assert utilisateur.statut_compte is StatutCompte.ACTIF


def test_regle_declenche_une_alerte(db_session):
    utilisateur = _creer_utilisateur_admin(db_session)

    regle = Regle(
        nom="Port Scan",
        description="Nombre de ports distincts sollicites par une meme source",
        type_menace="port_scan",
        condition_declenchement=json.dumps(
            {"indicateur": "ports_distincts_par_source", "seuil": 15, "fenetre_secondes": 10}
        ),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
        auteur=utilisateur,
    )
    db_session.add(regle)
    db_session.commit()

    alerte = Alerte(
        regle=regle,
        type_menace=regle.type_menace,
        ip_source="192.168.1.50",
        gravite=regle.gravite,
        statut_traitement=StatutAlerte.NOUVELLE,
    )
    db_session.add(alerte)
    db_session.commit()

    assert alerte.id is not None
    assert alerte.regle.nom == "Port Scan"
    assert regle.alertes == [alerte]


def test_log_peut_etre_associe_a_une_alerte_ou_non(db_session):
    utilisateur = _creer_utilisateur_admin(db_session)
    regle = Regle(
        nom="Brute Force",
        type_menace="brute_force",
        condition_declenchement=json.dumps({"indicateur": "echecs_consecutifs", "seuil": 5}),
        gravite=Gravite.ELEVE,
        auteur=utilisateur,
    )
    alerte = Alerte(
        regle=regle,
        type_menace=regle.type_menace,
        ip_source="10.0.0.5",
        gravite=regle.gravite,
    )
    db_session.add_all([regle, alerte])
    db_session.commit()

    log_avec_alerte = LogEvenement(
        type_evenement="echec_authentification",
        ip_source="10.0.0.5",
        alerte=alerte,
    )
    log_sans_alerte = LogEvenement(type_evenement="connexion_normale", ip_source="10.0.0.6")
    db_session.add_all([log_avec_alerte, log_sans_alerte])
    db_session.commit()

    assert log_avec_alerte.alerte_id == alerte.id
    assert log_sans_alerte.alerte_id is None


def test_configuration_et_liste_noire(db_session):
    entree = AdresseListeNoire(adresse_ip="203.0.113.10", motif_source="Renseignement manuel")
    parametre = ParametreConfiguration(nom_parametre="interface_surveillee", valeur="eth0")
    db_session.add_all([entree, parametre])
    db_session.commit()

    assert entree.statut.value == "active"
    assert parametre.valeur == "eth0"
