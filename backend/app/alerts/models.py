"""Entité Alerte (docs/conception_base_de_donnees.md, section 3.3).

`HistoriqueAlerte` n'est **pas** prévue dans la conception de la base de
données (Livrable 5) : ajout nécessaire pour satisfaire l'exigence de
traçabilité de la gestion des alertes (acquittement, fermeture,
commentaires), qui ne peut pas être couverte par le seul couple
`statut_traitement` / `date_derniere_maj_statut` (qui ne conserve que le
dernier changement, pas l'historique complet). Écart signalé dans le
bilan de ce livrable.
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
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
    historique: Mapped[list["HistoriqueAlerte"]] = relationship(
        back_populates="alerte", order_by="HistoriqueAlerte.horodatage"
    )


class HistoriqueAlerte(Base):
    """Une entrée par événement de traitement (acquittement, fermeture ou
    simple commentaire) : `statut` est le statut de l'alerte *après* cet
    événement (inchangé pour un commentaire seul)."""

    __tablename__ = "historique_alertes"

    id: Mapped[int] = mapped_column(primary_key=True)
    alerte_id: Mapped[int] = mapped_column(ForeignKey("alertes.id"), nullable=False)
    statut: Mapped[StatutAlerte] = mapped_column(
        Enum(StatutAlerte, native_enum=False, length=20), nullable=False
    )
    commentaire: Mapped[str | None] = mapped_column(Text)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"), nullable=False)
    horodatage: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    alerte: Mapped["Alerte"] = relationship(back_populates="historique")
    utilisateur: Mapped["Utilisateur"] = relationship()
