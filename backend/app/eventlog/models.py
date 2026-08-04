"""Entité Log (docs/conception_base_de_donnees.md, section 3.4)."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.alerts.models import Alerte
from app.database.base import Base


class LogEvenement(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    horodatage: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    type_evenement: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_source: Mapped[str] = mapped_column(String(45), nullable=False)
    ip_destination: Mapped[str | None] = mapped_column(String(45))
    ports: Mapped[str | None] = mapped_column(String(100))
    protocole: Mapped[str | None] = mapped_column(String(20))
    alerte_id: Mapped[int | None] = mapped_column(ForeignKey("alertes.id"))

    alerte: Mapped["Alerte | None"] = relationship()
