"""Entité Log (docs/conception_base_de_donnees.md, section 3.4).

`niveau` n'est **pas** prévu dans la conception de la base de données
(Livrable 5) : ajout nécessaire pour satisfaire le filtre « par niveau »
explicitement demandé pour la gestion des logs. Volontairement distinct
de `gravite` sur `Alerte` (qui qualifie une menace de sécurité) :
`niveau` qualifie la sévérité *technique* d'un événement journalisé
(succès d'une opération, situation dégradée, échec), ce qui préserve la
séparation entre logs techniques et alertes de sécurité déjà exigée par
ce livrable. Écart signalé dans le bilan de ce livrable.
"""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.alerts.models import Alerte
from app.database.base import Base


class NiveauLog(str, enum.Enum):
    INFO = "info"
    AVERTISSEMENT = "avertissement"
    ERREUR = "erreur"


class LogEvenement(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    horodatage: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    type_evenement: Mapped[str] = mapped_column(String(100), nullable=False)
    niveau: Mapped[NiveauLog] = mapped_column(
        Enum(NiveauLog, native_enum=False, length=20),
        default=NiveauLog.INFO,
        nullable=False,
    )
    ip_source: Mapped[str] = mapped_column(String(45), nullable=False)
    ip_destination: Mapped[str | None] = mapped_column(String(45))
    ports: Mapped[str | None] = mapped_column(String(100))
    protocole: Mapped[str | None] = mapped_column(String(20))
    alerte_id: Mapped[int | None] = mapped_column(ForeignKey("alertes.id"))

    alerte: Mapped["Alerte | None"] = relationship()
