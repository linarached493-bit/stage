"""Fixtures partagées : base de données de test en mémoire (SQLite).

Utilisée uniquement pour les tests, indépendamment de PostgreSQL (voir
docker-compose.yml pour la base de données réelle du projet).
"""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Base


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    # StaticPool : une base ":memory:" est propre à sa connexion. Sans
    # cela, chaque nouvelle connexion piochée dans le pool (par ex.
    # depuis un autre thread, comme le fait TestClient) verrait une
    # base vide différente de celle où `create_all` a été exécuté.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
