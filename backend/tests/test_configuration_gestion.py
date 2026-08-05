"""Tests de la gestion de la configuration et de la liste noire
(docs/cahier_des_charges.md, section 6 « Gestion de la configuration »)."""

import json
from datetime import datetime

import pytest

from app.auth.models import Role, Utilisateur
from app.capture.events import EvenementReseau
from app.configuration.models import StatutListeNoire
from app.configuration.service import (
    AdresseDejaListee,
    PortInvalide,
    adresses_blacklistees_actives,
    ajouter_adresse_liste_noire,
    changer_statut_liste_noire,
    definir_parametre,
    definir_ports_interdits,
    lister_liste_noire,
    lister_parametres,
    obtenir_entree_liste_noire,
    obtenir_parametre,
    ports_interdits_actifs,
)
from app.database.enums import Gravite
from app.detection.engine import MoteurDetection
from app.detection.models import Regle, StatutRegle

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def _admin(db_session) -> Utilisateur:
    role = Role(nom="Administrateur")
    utilisateur = Utilisateur(nom_utilisateur="admin", mot_de_passe_hash="x", role=role)
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


# --- Paramètres génériques -------------------------------------------------


def test_definir_parametre_cree_si_absent(db_session):
    admin = _admin(db_session)

    parametre = definir_parametre(db_session, "interface_surveillee", "eth0", admin)

    assert parametre.valeur == "eth0"
    assert parametre.utilisateur_modification is admin
    assert parametre.date_derniere_modification is not None


def test_definir_parametre_remplace_si_existant(db_session):
    admin = _admin(db_session)
    definir_parametre(db_session, "interface_surveillee", "eth0", admin)

    resultat = definir_parametre(db_session, "interface_surveillee", "eth1", admin)

    assert resultat.valeur == "eth1"
    assert len(lister_parametres(db_session)) == 1


def test_lister_parametres_tries_par_nom(db_session):
    admin = _admin(db_session)
    definir_parametre(db_session, "zeta", "1", admin)
    definir_parametre(db_session, "alpha", "2", admin)

    resultat = lister_parametres(db_session)

    assert [p.nom_parametre for p in resultat] == ["alpha", "zeta"]


def test_obtenir_parametre_introuvable_retourne_none(db_session):
    assert obtenir_parametre(db_session, "inexistant") is None


# --- Ports interdits ---------------------------------------------------


def test_definir_ports_interdits_stocke_en_configuration(db_session):
    admin = _admin(db_session)

    resultat = definir_ports_interdits(db_session, [23, 3389], admin)

    assert resultat == frozenset({23, 3389})
    assert ports_interdits_actifs(db_session) == frozenset({23, 3389})


def test_definir_ports_interdits_refuse_port_hors_plage(db_session):
    admin = _admin(db_session)

    with pytest.raises(PortInvalide):
        definir_ports_interdits(db_session, [70000], admin)


def test_definir_ports_interdits_refuse_port_negatif(db_session):
    admin = _admin(db_session)

    with pytest.raises(PortInvalide):
        definir_ports_interdits(db_session, [-1], admin)


def test_definir_ports_interdits_refuse_valeur_non_entiere(db_session):
    admin = _admin(db_session)

    with pytest.raises(PortInvalide):
        definir_ports_interdits(db_session, [23, "quatre-vingts"], admin)


# --- Liste noire -------------------------------------------------------


def test_ajouter_adresse_liste_noire(db_session):
    entree = ajouter_adresse_liste_noire(db_session, "203.0.113.66", "Renseignement manuel")

    assert entree.id is not None
    assert entree.statut is StatutListeNoire.ACTIVE
    assert adresses_blacklistees_actives(db_session) == frozenset({"203.0.113.66"})


def test_ajouter_adresse_liste_noire_refuse_doublon(db_session):
    ajouter_adresse_liste_noire(db_session, "203.0.113.66", None)

    with pytest.raises(AdresseDejaListee):
        ajouter_adresse_liste_noire(db_session, "203.0.113.66", "Autre motif")


def test_retirer_adresse_liste_noire_la_desactive(db_session):
    entree = ajouter_adresse_liste_noire(db_session, "203.0.113.66", None)

    resultat = changer_statut_liste_noire(db_session, entree, StatutListeNoire.INACTIVE)

    assert resultat.statut is StatutListeNoire.INACTIVE
    assert adresses_blacklistees_actives(db_session) == frozenset()


def test_retirer_adresse_reste_consultable_apres_desactivation(db_session):
    """Retrait = désactivation, jamais de suppression physique."""
    entree = ajouter_adresse_liste_noire(db_session, "203.0.113.66", None)
    identifiant = entree.id

    changer_statut_liste_noire(db_session, entree, StatutListeNoire.INACTIVE)

    assert obtenir_entree_liste_noire(db_session, identifiant) is not None


def test_lister_liste_noire(db_session):
    ajouter_adresse_liste_noire(db_session, "203.0.113.66", None)
    ajouter_adresse_liste_noire(db_session, "198.51.100.10", None)

    assert len(lister_liste_noire(db_session)) == 2


def test_obtenir_entree_introuvable_retourne_none(db_session):
    assert obtenir_entree_liste_noire(db_session, 999) is None


# --- Prise en compte immédiate par le moteur de détection -------------------


def _regle_ip_blacklistee(admin: Utilisateur) -> Regle:
    return Regle(
        nom="IP blacklistée",
        type_menace="ip_blacklistee",
        condition_declenchement=json.dumps({"indicateur": "adresse_dans_liste_noire", "seuil": 1}),
        gravite=Gravite.ELEVE,
        statut=StatutRegle.ACTIVE,
        auteur=admin,
    )


def _evenement_connexion(ip: str, port: int) -> list[EvenementReseau]:
    return [
        EvenementReseau(ip_source=ip, type_evenement="connexion", horodatage=MAINTENANT, port=port)
    ]


def test_ajout_liste_noire_immediatement_pris_en_compte_par_le_moteur(db_session):
    admin = _admin(db_session)
    regle = _regle_ip_blacklistee(admin)
    evenements = _evenement_connexion("203.0.113.66", 443)

    assert (
        MoteurDetection(
            [regle], adresses_blacklistees=adresses_blacklistees_actives(db_session)
        ).evaluer(evenements, MAINTENANT)
        == []
    )

    ajouter_adresse_liste_noire(db_session, "203.0.113.66", None)

    detections = MoteurDetection(
        [regle], adresses_blacklistees=adresses_blacklistees_actives(db_session)
    ).evaluer(evenements, MAINTENANT)
    assert len(detections) == 1


def test_retrait_liste_noire_immediatement_pris_en_compte_par_le_moteur(db_session):
    admin = _admin(db_session)
    regle = _regle_ip_blacklistee(admin)
    entree = ajouter_adresse_liste_noire(db_session, "203.0.113.66", None)
    evenements = _evenement_connexion("203.0.113.66", 443)
    assert (
        len(
            MoteurDetection(
                [regle], adresses_blacklistees=adresses_blacklistees_actives(db_session)
            ).evaluer(evenements, MAINTENANT)
        )
        == 1
    )

    changer_statut_liste_noire(db_session, entree, StatutListeNoire.INACTIVE)

    detections = MoteurDetection(
        [regle], adresses_blacklistees=adresses_blacklistees_actives(db_session)
    ).evaluer(evenements, MAINTENANT)
    assert detections == []


def _regle_ports_interdits(admin: Utilisateur) -> Regle:
    return Regle(
        nom="Utilisation de ports interdits",
        type_menace="ports_interdits",
        condition_declenchement=json.dumps({"indicateur": "port_interdit_utilise", "seuil": 1}),
        gravite=Gravite.MOYEN,
        statut=StatutRegle.ACTIVE,
        auteur=admin,
    )


def test_modification_ports_interdits_immediatement_prise_en_compte(db_session):
    admin = _admin(db_session)
    regle = _regle_ports_interdits(admin)
    evenements = _evenement_connexion("192.168.1.40", 3389)

    assert (
        MoteurDetection([regle], ports_interdits=ports_interdits_actifs(db_session)).evaluer(
            evenements, MAINTENANT
        )
        == []
    )

    definir_ports_interdits(db_session, [3389], admin)

    detections = MoteurDetection(
        [regle], ports_interdits=ports_interdits_actifs(db_session)
    ).evaluer(evenements, MAINTENANT)
    assert len(detections) == 1
