import pytest

from app.auth.models import Role, StatutCompte, Utilisateur
from app.auth.security import (
    TokenInvalide,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.auth.service import authenticate_user


def test_hash_password_ne_stocke_jamais_le_mot_de_passe_en_clair():
    hache = hash_password("mot-de-passe-secret")

    assert hache != "mot-de-passe-secret"
    assert verify_password("mot-de-passe-secret", hache)
    assert not verify_password("mauvais-mot-de-passe", hache)


def test_access_token_round_trip():
    token = create_access_token(sujet="42", role="Administrateur")
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "Administrateur"


def test_token_invalide_leve_une_erreur():
    with pytest.raises(TokenInvalide):
        decode_access_token("ceci-nest-pas-un-jeton-valide")


def _creer_utilisateur(db_session, statut=StatutCompte.ACTIF) -> Utilisateur:
    role = Role(nom="Analyste sécurité")
    utilisateur = Utilisateur(
        nom_utilisateur="analyste",
        mot_de_passe_hash=hash_password("Passw0rd!"),
        role=role,
        statut_compte=statut,
    )
    db_session.add(utilisateur)
    db_session.commit()
    return utilisateur


def test_authenticate_user_avec_identifiants_corrects(db_session):
    _creer_utilisateur(db_session)

    utilisateur = authenticate_user(db_session, "analyste", "Passw0rd!")

    assert utilisateur is not None
    assert utilisateur.nom_utilisateur == "analyste"


def test_authenticate_user_refuse_mauvais_mot_de_passe(db_session):
    _creer_utilisateur(db_session)

    assert authenticate_user(db_session, "analyste", "mauvais-mot-de-passe") is None


def test_authenticate_user_refuse_compte_desactive(db_session):
    _creer_utilisateur(db_session, statut=StatutCompte.DESACTIVE)

    assert authenticate_user(db_session, "analyste", "Passw0rd!") is None


def test_authenticate_user_refuse_utilisateur_inconnu(db_session):
    assert authenticate_user(db_session, "inconnu", "peu-importe") is None
