"""Tests de la gestion des règles de détection (docs/cahier_des_charges.md, UC3)."""

import json
from datetime import datetime, timedelta

import pytest

from app.auth.models import Role, Utilisateur
from app.capture.events import EvenementReseau
from app.database.enums import Gravite
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle
from app.detection.service import (
    ConditionDeclenchementInvalide,
    NomRegleDejaUtilise,
    changer_statut_regle,
    creer_regle,
    lister_regles,
    modifier_regle,
    obtenir_regle,
    valider_condition_declenchement,
)

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)
CONDITION_VALIDE = {"indicateur": "ports_distincts_par_source", "seuil": 15, "fenetre_secondes": 60}


def _auteur(db_session) -> Utilisateur:
    role = Role(nom="Administrateur")
    utilisateur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def _creer_regle(db_session, auteur: Utilisateur, nom: str = "Port Scan", **overrides) -> Regle:
    parametres = {
        "nom": nom,
        "description": None,
        "type_menace": "port_scan",
        "condition_declenchement": CONDITION_VALIDE,
        "gravite": Gravite.MOYEN,
        "auteur": auteur,
    }
    parametres.update(overrides)
    return creer_regle(db_session, **parametres)


def _evenements_port_scan() -> list[EvenementReseau]:
    return [
        EvenementReseau(
            ip_source="192.168.1.99",
            type_evenement="connexion",
            horodatage=MAINTENANT - timedelta(seconds=i),
            port=port,
        )
        for i, port in enumerate(range(1000, 1020))  # 20 ports distincts
    ]


# --- Validation des paramètres -----------------------------------------


def test_valider_condition_declenchement_accepte_un_indicateur_connu():
    valider_condition_declenchement(CONDITION_VALIDE)  # ne doit pas lever


def test_valider_condition_declenchement_refuse_un_indicateur_inconnu():
    with pytest.raises(ConditionDeclenchementInvalide):
        valider_condition_declenchement({"indicateur": "indicateur_qui_nexiste_pas", "seuil": 5})


def test_valider_condition_declenchement_refuse_seuil_manquant():
    with pytest.raises(ConditionDeclenchementInvalide):
        valider_condition_declenchement({"indicateur": "ports_distincts_par_source"})


def test_valider_condition_declenchement_refuse_seuil_non_entier():
    with pytest.raises(ConditionDeclenchementInvalide):
        valider_condition_declenchement(
            {"indicateur": "ports_distincts_par_source", "seuil": "quinze"}
        )


# --- Création ------------------------------------------------------------


def test_creer_regle(db_session):
    auteur = _auteur(db_session)

    regle = _creer_regle(db_session, auteur, description="Balayage de ports")

    assert regle.id is not None
    assert regle.statut is StatutRegle.ACTIVE
    assert json.loads(regle.condition_declenchement) == CONDITION_VALIDE
    assert regle.auteur is auteur
    assert regle.date_derniere_modification is None


def test_creer_regle_refuse_nom_deja_utilise(db_session):
    auteur = _auteur(db_session)
    _creer_regle(db_session, auteur)

    with pytest.raises(NomRegleDejaUtilise):
        _creer_regle(db_session, auteur)


def test_creer_regle_refuse_condition_invalide(db_session):
    auteur = _auteur(db_session)

    with pytest.raises(ConditionDeclenchementInvalide):
        _creer_regle(
            db_session, auteur, condition_declenchement={"indicateur": "inconnu", "seuil": 1}
        )


# --- Consultation ----------------------------------------------------------


def test_lister_regles_par_ordre_alphabetique(db_session):
    auteur = _auteur(db_session)
    _creer_regle(db_session, auteur, nom="Zeta")
    _creer_regle(db_session, auteur, nom="Alpha")

    resultat = lister_regles(db_session)

    assert [r.nom for r in resultat] == ["Alpha", "Zeta"]


def test_obtenir_regle_introuvable_retourne_none(db_session):
    assert obtenir_regle(db_session, 999) is None


def test_obtenir_regle_existante(db_session):
    auteur = _auteur(db_session)
    creee = _creer_regle(db_session, auteur)

    assert obtenir_regle(db_session, creee.id).nom == "Port Scan"


# --- Modification ----------------------------------------------------------


def test_modifier_regle_change_le_seuil_et_horodate_la_modification(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)

    resultat = modifier_regle(
        db_session, regle, auteur=auteur, condition_declenchement={**CONDITION_VALIDE, "seuil": 30}
    )

    assert json.loads(resultat.condition_declenchement)["seuil"] == 30
    assert resultat.date_derniere_modification is not None


def test_modifier_regle_refuse_condition_invalide(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)

    with pytest.raises(ConditionDeclenchementInvalide):
        modifier_regle(
            db_session,
            regle,
            auteur=auteur,
            condition_declenchement={"indicateur": "inconnu", "seuil": 1},
        )


def test_modifier_regle_refuse_nom_deja_pris_par_une_autre(db_session):
    auteur = _auteur(db_session)
    _creer_regle(db_session, auteur, nom="Port Scan")
    autre = _creer_regle(
        db_session,
        auteur,
        nom="Brute Force",
        type_menace="brute_force",
        condition_declenchement={"indicateur": "echecs_consecutifs", "seuil": 5},
        gravite=Gravite.ELEVE,
    )

    with pytest.raises(NomRegleDejaUtilise):
        modifier_regle(db_session, autre, auteur=auteur, nom="Port Scan")


def test_modifier_regle_autorise_a_garder_son_propre_nom(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)

    resultat = modifier_regle(db_session, regle, auteur=auteur, nom="Port Scan")

    assert resultat.nom == "Port Scan"


# --- Activation / désactivation ---------------------------------------------


def test_changer_statut_regle_desactive(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)

    resultat = changer_statut_regle(db_session, regle, StatutRegle.INACTIVE, auteur=auteur)

    assert resultat.statut is StatutRegle.INACTIVE


def test_changer_statut_regle_reactive(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)
    changer_statut_regle(db_session, regle, StatutRegle.INACTIVE, auteur=auteur)

    resultat = changer_statut_regle(db_session, regle, StatutRegle.ACTIVE, auteur=auteur)

    assert resultat.statut is StatutRegle.ACTIVE


# --- Prise en compte immédiate par le moteur de détection -------------------
# (aucune modification d'app/detection/engine.py n'était nécessaire : le
# moteur relit toujours le statut courant des règles qu'on lui fournit.)


def test_regle_desactivee_nest_plus_utilisee_par_le_moteur(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)
    evenements = _evenements_port_scan()
    assert len(MoteurDetection([regle]).evaluer(evenements, MAINTENANT)) == 1

    changer_statut_regle(db_session, regle, StatutRegle.INACTIVE, auteur=auteur)

    regle_actualisee = obtenir_regle(db_session, regle.id)
    assert MoteurDetection([regle_actualisee]).evaluer(evenements, MAINTENANT) == []


def test_regle_reactivee_immediatement_prise_en_compte(db_session):
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)
    changer_statut_regle(db_session, regle, StatutRegle.INACTIVE, auteur=auteur)
    evenements = _evenements_port_scan()
    assert (
        MoteurDetection([obtenir_regle(db_session, regle.id)]).evaluer(evenements, MAINTENANT) == []
    )

    changer_statut_regle(db_session, regle, StatutRegle.ACTIVE, auteur=auteur)

    regle_reactivee = obtenir_regle(db_session, regle.id)
    assert len(MoteurDetection([regle_reactivee]).evaluer(evenements, MAINTENANT)) == 1


def test_modification_du_seuil_immediatement_prise_en_compte(db_session):
    """Une règle modifiée (seuil relevé) change immédiatement le
    comportement du moteur, sans qu'aucun indicateur n'ait été touché."""
    auteur = _auteur(db_session)
    regle = _creer_regle(db_session, auteur)
    evenements = _evenements_port_scan()
    assert len(MoteurDetection([regle]).evaluer(evenements, MAINTENANT)) == 1

    modifier_regle(
        db_session, regle, auteur=auteur, condition_declenchement={**CONDITION_VALIDE, "seuil": 50}
    )

    regle_modifiee = obtenir_regle(db_session, regle.id)
    assert MoteurDetection([regle_modifiee]).evaluer(evenements, MAINTENANT) == []
