"""Tests de la gestion des utilisateurs (docs/cahier_des_charges.md, UC6)."""

import pytest

from app.auth.models import Role, StatutCompte
from app.auth.service import (
    NomUtilisateurDejaUtilise,
    RoleIntrouvable,
    changer_statut_utilisateur,
    creer_utilisateur,
    lister_utilisateurs,
    modifier_utilisateur,
    obtenir_utilisateur,
)


def _role(db_session, nom: str = "Administrateur") -> Role:
    role = Role(nom=nom)
    db_session.add(role)
    db_session.commit()
    return role


def test_creer_utilisateur_hache_le_mot_de_passe_et_active_le_compte(db_session):
    role = _role(db_session)

    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    assert utilisateur.id is not None
    assert utilisateur.mot_de_passe_hash != "Passw0rd!"
    assert utilisateur.role_id == role.id
    assert utilisateur.statut_compte is StatutCompte.ACTIF


def test_creer_utilisateur_refuse_nom_deja_utilise(db_session):
    role = _role(db_session)
    creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    with pytest.raises(NomUtilisateurDejaUtilise):
        creer_utilisateur(db_session, "admin", "AutreMotDePasse!", role.id)


def test_creer_utilisateur_refuse_role_inexistant(db_session):
    with pytest.raises(RoleIntrouvable):
        creer_utilisateur(db_session, "admin", "Passw0rd!", role_id=999)


def test_lister_utilisateurs_par_ordre_alphabetique(db_session):
    role = _role(db_session)
    creer_utilisateur(db_session, "zoe", "Passw0rd!", role.id)
    creer_utilisateur(db_session, "alice", "Passw0rd!", role.id)

    resultat = lister_utilisateurs(db_session)

    assert [u.nom_utilisateur for u in resultat] == ["alice", "zoe"]


def test_obtenir_utilisateur_introuvable_retourne_none(db_session):
    assert obtenir_utilisateur(db_session, 999) is None


def test_obtenir_utilisateur_existant(db_session):
    role = _role(db_session)
    cree = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    assert obtenir_utilisateur(db_session, cree.id).nom_utilisateur == "admin"


def test_modifier_utilisateur_change_le_role(db_session):
    role_admin = _role(db_session, "Administrateur")
    role_analyste = Role(nom="Analyste sécurité")
    db_session.add(role_analyste)
    db_session.commit()
    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role_admin.id)

    resultat = modifier_utilisateur(db_session, utilisateur, role_id=role_analyste.id)

    assert resultat.role_id == role_analyste.id


def test_modifier_utilisateur_refuse_role_inexistant(db_session):
    role = _role(db_session)
    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    with pytest.raises(RoleIntrouvable):
        modifier_utilisateur(db_session, utilisateur, role_id=999)


def test_modifier_utilisateur_renomme(db_session):
    role = _role(db_session)
    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    resultat = modifier_utilisateur(db_session, utilisateur, nom_utilisateur="admin2")

    assert resultat.nom_utilisateur == "admin2"


def test_modifier_utilisateur_refuse_nom_deja_pris_par_un_autre(db_session):
    role = _role(db_session)
    creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)
    autre = creer_utilisateur(db_session, "analyste", "Passw0rd!", role.id)

    with pytest.raises(NomUtilisateurDejaUtilise):
        modifier_utilisateur(db_session, autre, nom_utilisateur="admin")


def test_modifier_utilisateur_autorise_a_garder_son_propre_nom(db_session):
    """Renommer un utilisateur avec son nom actuel ne doit pas être
    confondu avec un conflit d'unicité (auto-exclusion de la requête)."""
    role = _role(db_session)
    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    resultat = modifier_utilisateur(db_session, utilisateur, nom_utilisateur="admin")

    assert resultat.nom_utilisateur == "admin"


def test_changer_statut_utilisateur_desactive_le_compte(db_session):
    role = _role(db_session)
    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)

    resultat = changer_statut_utilisateur(db_session, utilisateur, StatutCompte.DESACTIVE)

    assert resultat.statut_compte is StatutCompte.DESACTIVE


def test_changer_statut_utilisateur_reactive_le_compte(db_session):
    role = _role(db_session)
    utilisateur = creer_utilisateur(db_session, "admin", "Passw0rd!", role.id)
    changer_statut_utilisateur(db_session, utilisateur, StatutCompte.DESACTIVE)

    resultat = changer_statut_utilisateur(db_session, utilisateur, StatutCompte.ACTIF)

    assert resultat.statut_compte is StatutCompte.ACTIF
