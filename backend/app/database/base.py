"""Base déclarative SQLAlchemy partagée par toutes les entités.

Voir docs/conception_base_de_donnees.md pour le dictionnaire de données
et docs/architecture_logicielle.md (section 4.9) pour la mission du
module Base de données.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
