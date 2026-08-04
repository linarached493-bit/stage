"""Entités Configuration et Liste noire (docs/conception_base_de_donnees.md,
sections 3.7 et 3.8).
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.models import Utilisateur
from app.database.base import Base


class StatutListeNoire(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ParametreConfiguration(Base):
    __tablename__ = "configuration"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_parametre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    valeur: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    utilisateur_modification_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"))
    date_derniere_modification: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    utilisateur_modification: Mapped["Utilisateur | None"] = relationship()


class AdresseListeNoire(Base):
    __tablename__ = "liste_noire"

    id: Mapped[int] = mapped_column(primary_key=True)
    adresse_ip: Mapped[str] = mapped_column(String(45), unique=True, nullable=False)
    motif_source: Mapped[str | None] = mapped_column(String(255))
    date_ajout: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    statut: Mapped[StatutListeNoire] = mapped_column(
        Enum(StatutListeNoire, native_enum=False, length=20),
        default=StatutListeNoire.ACTIVE,
        nullable=False,
    )
