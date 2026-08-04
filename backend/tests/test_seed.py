from app.auth.models import Role
from app.database.seed import seed_roles


def test_seed_roles_crée_les_trois_roles(db_session):
    crees = seed_roles(db_session)

    assert {r.nom for r in crees} == {"Administrateur", "Analyste sécurité", "Lecture seule"}
    assert db_session.query(Role).count() == 3


def test_seed_roles_est_idempotent(db_session):
    seed_roles(db_session)
    deuxieme_appel = seed_roles(db_session)

    assert deuxieme_appel == []
    assert db_session.query(Role).count() == 3
