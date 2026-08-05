"""Tests de la gestion des alertes : consultation filtrée, acquittement,
fermeture, commentaires, historique (docs/cahier_des_charges.md, UC8).
"""

import json
from datetime import datetime, timedelta

import pytest

from app.alerts.models import Alerte, StatutAlerte
from app.alerts.service import (
    StatutFermetureInvalide,
    TransitionAlerteInvalide,
    acquitter_alerte,
    ajouter_commentaire,
    fermer_alerte,
    lister_alertes,
    obtenir_alerte,
)
from app.auth.models import Role, Utilisateur
from app.database.enums import Gravite
from app.detection.models import Regle, StatutRegle

MAINTENANT = datetime(2026, 8, 4, 10, 0, 0)


def _utilisateur(
    db_session, nom: str = "analyste", nom_role: str = "Analyste sécurité"
) -> Utilisateur:
    role = Role(nom=nom_role)
    utilisateur = Utilisateur(nom_utilisateur=nom, mot_de_passe_hash="x", role=role)
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def _regle(db_session, auteur: Utilisateur) -> Regle:
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


def _alerte(db_session, regle: Regle, **overrides) -> Alerte:
    parametres = {
        "regle": regle,
        "type_menace": regle.type_menace,
        "ip_source": "192.168.1.99",
        "gravite": regle.gravite,
        "horodatage_detection": MAINTENANT,
    }
    parametres.update(overrides)
    alerte = Alerte(**parametres)
    db_session.add(alerte)
    db_session.commit()
    return alerte


# --- Consultation filtrée ---------------------------------------------------


def test_lister_alertes_sans_filtre(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    _alerte(db_session, regle)
    _alerte(db_session, regle, ip_source="10.0.0.5")

    assert len(lister_alertes(db_session)) == 2


def test_lister_alertes_filtre_par_gravite(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    _alerte(db_session, regle, gravite=Gravite.MOYEN)
    _alerte(db_session, regle, gravite=Gravite.ELEVE)

    resultat = lister_alertes(db_session, gravite=Gravite.ELEVE)

    assert len(resultat) == 1
    assert resultat[0].gravite is Gravite.ELEVE


def test_lister_alertes_filtre_par_statut(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    _alerte(db_session, regle, statut_traitement=StatutAlerte.NOUVELLE)
    _alerte(db_session, regle, statut_traitement=StatutAlerte.TRAITEE)

    resultat = lister_alertes(db_session, statut=StatutAlerte.TRAITEE)

    assert len(resultat) == 1
    assert resultat[0].statut_traitement is StatutAlerte.TRAITEE


def test_lister_alertes_filtre_par_periode(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    _alerte(db_session, regle, horodatage_detection=MAINTENANT - timedelta(days=10))
    _alerte(db_session, regle, horodatage_detection=MAINTENANT)

    resultat = lister_alertes(
        db_session,
        date_debut=MAINTENANT - timedelta(days=1),
        date_fin=MAINTENANT + timedelta(days=1),
    )

    assert len(resultat) == 1
    assert resultat[0].horodatage_detection == MAINTENANT


def test_lister_alertes_combine_plusieurs_filtres(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    _alerte(db_session, regle, gravite=Gravite.ELEVE, statut_traitement=StatutAlerte.NOUVELLE)
    _alerte(db_session, regle, gravite=Gravite.ELEVE, statut_traitement=StatutAlerte.TRAITEE)
    _alerte(db_session, regle, gravite=Gravite.MOYEN, statut_traitement=StatutAlerte.NOUVELLE)

    resultat = lister_alertes(db_session, gravite=Gravite.ELEVE, statut=StatutAlerte.NOUVELLE)

    assert len(resultat) == 1


def test_obtenir_alerte_introuvable_retourne_none(db_session):
    assert obtenir_alerte(db_session, 999) is None


# --- Acquittement ------------------------------------------------------------


def test_acquitter_alerte_passe_en_cours(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)

    resultat = acquitter_alerte(db_session, alerte, auteur, commentaire="Pris en charge")

    assert resultat.statut_traitement is StatutAlerte.EN_COURS
    assert resultat.utilisateur_qualification is auteur
    assert len(resultat.historique) == 1
    assert resultat.historique[0].statut is StatutAlerte.EN_COURS
    assert resultat.historique[0].commentaire == "Pris en charge"
    assert resultat.historique[0].utilisateur is auteur


def test_acquitter_alerte_refuse_si_deja_en_cours(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)
    acquitter_alerte(db_session, alerte, auteur)

    with pytest.raises(TransitionAlerteInvalide):
        acquitter_alerte(db_session, alerte, auteur)


def test_acquitter_alerte_refuse_si_deja_fermee(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)
    fermer_alerte(db_session, alerte, auteur, StatutAlerte.TRAITEE)

    with pytest.raises(TransitionAlerteInvalide):
        acquitter_alerte(db_session, alerte, auteur)


# --- Fermeture -----------------------------------------------------------


def test_fermer_alerte_depuis_nouvelle(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)

    resultat = fermer_alerte(
        db_session, alerte, auteur, StatutAlerte.TRAITEE, commentaire="Confirmée"
    )

    assert resultat.statut_traitement is StatutAlerte.TRAITEE


def test_fermer_alerte_depuis_en_cours_en_faux_positif(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)
    acquitter_alerte(db_session, alerte, auteur)

    resultat = fermer_alerte(db_session, alerte, auteur, StatutAlerte.FAUX_POSITIF)

    assert resultat.statut_traitement is StatutAlerte.FAUX_POSITIF


def test_fermer_alerte_refuse_statut_final_non_terminal(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)

    with pytest.raises(StatutFermetureInvalide):
        fermer_alerte(db_session, alerte, auteur, StatutAlerte.EN_COURS)


def test_fermer_alerte_refuse_si_deja_fermee(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)
    fermer_alerte(db_session, alerte, auteur, StatutAlerte.TRAITEE)

    with pytest.raises(TransitionAlerteInvalide):
        fermer_alerte(db_session, alerte, auteur, StatutAlerte.FAUX_POSITIF)


# --- Commentaire ----------------------------------------------------------


def test_ajouter_commentaire_ne_change_pas_le_statut(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)

    resultat = ajouter_commentaire(db_session, alerte, auteur, "Vérification en cours")

    assert resultat.statut_traitement is StatutAlerte.NOUVELLE
    assert len(resultat.historique) == 1
    assert resultat.historique[0].statut is StatutAlerte.NOUVELLE
    assert resultat.historique[0].commentaire == "Vérification en cours"


# --- Historique --------------------------------------------------------------


def test_historique_conserve_toutes_les_etapes_dans_lordre(db_session):
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)

    ajouter_commentaire(db_session, alerte, auteur, "Première observation")
    acquitter_alerte(db_session, alerte, auteur, commentaire="Prise en charge")
    resultat = fermer_alerte(
        db_session, alerte, auteur, StatutAlerte.TRAITEE, commentaire="Résolue"
    )

    assert [e.statut for e in resultat.historique] == [
        StatutAlerte.NOUVELLE,
        StatutAlerte.EN_COURS,
        StatutAlerte.TRAITEE,
    ]
    assert [e.commentaire for e in resultat.historique] == [
        "Première observation",
        "Prise en charge",
        "Résolue",
    ]


def test_alerte_creee_par_le_moteur_reste_consultable_apres_traitement(db_session):
    """Aucune suppression physique : l'alerte reste consultable par son
    identifiant après avoir été acquittée puis fermée."""
    auteur = _utilisateur(db_session)
    regle = _regle(db_session, auteur)
    alerte = _alerte(db_session, regle)
    identifiant = alerte.id

    acquitter_alerte(db_session, alerte, auteur)
    fermer_alerte(db_session, alerte, auteur, StatutAlerte.TRAITEE)

    assert obtenir_alerte(db_session, identifiant) is not None
