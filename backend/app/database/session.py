"""Fabrique de sessions SQLAlchemy vers la base de données configurée.

Le moteur n'est créé qu'à la demande (et mis en cache) plutôt qu'à
l'import du module, afin que les tests puissent substituer leur propre
session (voir backend/tests/conftest.py) sans nécessiter de base de
données PostgreSQL disponible.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI fournissant une session par requête."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
