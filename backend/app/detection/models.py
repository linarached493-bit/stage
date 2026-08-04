"""Entité Règle (docs/conception_base_de_donnees.md, section 3.5).

`condition_declenchement` stocke une condition structurée au format
JSON (seuil, fenêtre d'observation, indicateur observé), interprétée
par le moteur de détection (voir app/detection/engine.py).
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.models import Utilisateur
from app.database.base import Base
from app.database.enums import Gravite

if TYPE_CHECKING:
    # Import différé pour l'analyse statique uniquement : un import réel
    # créerait un cycle (app.alerts.models importe déjà app.detection.models).
    from app.alerts.models import Alerte


class StatutRegle(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Regle(Base):
    __tablename__ = "regles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_menace: Mapped[str] = mapped_column(String(100), nullable=False)
    condition_declenchement: Mapped[str] = mapped_column(Text, nullable=False)
    gravite: Mapped[Gravite] = mapped_column(
        Enum(Gravite, native_enum=False, length=20), nullable=False
    )
    statut: Mapped[StatutRegle] = mapped_column(
        Enum(StatutRegle, native_enum=False, length=20),
        default=StatutRegle.ACTIVE,
        nullable=False,
    )
    auteur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    date_derniere_modification: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    auteur: Mapped["Utilisateur"] = relationship()
    alertes: Mapped[list["Alerte"]] = relationship(back_populates="regle")
