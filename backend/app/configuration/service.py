"""Module Configuration (docs/architecture_logicielle.md, section 4.10).

Met à disposition la liste noire active, consommée par le Moteur de
détection pour la règle « communication avec une IP blacklistée ».
"""

from sqlalchemy.orm import Session

from app.configuration.models import AdresseListeNoire, StatutListeNoire


def adresses_blacklistees_actives(session: Session) -> frozenset[str]:
    lignes = (
        session.query(AdresseListeNoire.adresse_ip)
        .filter(AdresseListeNoire.statut == StatutListeNoire.ACTIVE)
        .all()
    )
    return frozenset(adresse_ip for (adresse_ip,) in lignes)
