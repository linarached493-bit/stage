"""Entités Rôle et Utilisateur (docs/conception_base_de_donnees.md,
sections 3.1 et 3.2).
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StatutCompte(str, enum.Enum):
    ACTIF = "actif"
    DESACTIVE = "desactive"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    utilisateurs: Mapped[list["Utilisateur"]] = relationship(back_populates="role")


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_utilisateur: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    statut_compte: Mapped[StatutCompte] = mapped_column(
        Enum(StatutCompte, native_enum=False, length=20),
        default=StatutCompte.ACTIF,
        nullable=False,
    )
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    date_derniere_connexion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    role: Mapped["Role"] = relationship(back_populates="utilisateurs")
