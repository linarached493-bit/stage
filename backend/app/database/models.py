"""Point d'agrégation de toutes les entités.

Chaque entité est définie dans le module métier qui la possède
(voir README.md à la racine du projet pour le mapping module -> dossier).
Ce fichier centralise leur import afin que SQLAlchemy puisse résoudre
les relations déclarées entre modules avant toute utilisation de la
base de données (création du schéma, requêtes).

Entité Statistique : volontairement absente. La décision retenue
(docs/preparation_implementation.md, section 3.3) est un calcul à la
demande plutôt qu'une persistance, donc aucune table dédiée.
"""

from app.alerts.models import Alerte  # noqa: F401
from app.auth.models import Role, Utilisateur  # noqa: F401
from app.configuration.models import AdresseListeNoire, ParametreConfiguration  # noqa: F401
from app.database.base import Base
from app.detection.models import Regle  # noqa: F401
from app.eventlog.models import LogEvenement  # noqa: F401

__all__ = [
    "Base",
    "Alerte",
    "Role",
    "Utilisateur",
    "AdresseListeNoire",
    "ParametreConfiguration",
    "Regle",
    "LogEvenement",
]
