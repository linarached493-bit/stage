"""Entité Alerte (docs/conception_base_de_donnees.md, section 3.3)."""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.models import Utilisateur
from app.database.base import Base
from app.database.enums import Gravite
from app.detection.models import Regle


class StatutAlerte(str, enum.Enum):
    NOUVELLE = "nouvelle"
    EN_COURS = "en_cours"
    TRAITEE = "traitee"
    FAUX_POSITIF = "faux_positif"


class Alerte(Base):
    __tablename__ = "alertes"

    id: Mapped[int] = mapped_column(primary_key=True)
    regle_id: Mapped[int] = mapped_column(ForeignKey("regles.id"), nullable=False)
    type_menace: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_source: Mapped[str] = mapped_column(String(45), nullable=False)
    ip_destination: Mapped[str | None] = mapped_column(String(45))
    ports: Mapped[str | None] = mapped_column(String(100))
    gravite: Mapped[Gravite] = mapped_column(
        Enum(Gravite, native_enum=False, length=20), nullable=False
    )
    horodatage_detection: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    statut_traitement: Mapped[StatutAlerte] = mapped_column(
        Enum(StatutAlerte, native_enum=False, length=20),
        default=StatutAlerte.NOUVELLE,
        nullable=False,
    )
    utilisateur_qualification_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"))
    date_derniere_maj_statut: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    regle: Mapped["Regle"] = relationship(back_populates="alertes")
    utilisateur_qualification: Mapped["Utilisateur | None"] = relationship()
