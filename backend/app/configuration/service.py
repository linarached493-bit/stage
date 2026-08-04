"""Module Configuration (docs/architecture_logicielle.md, section 4.10).

Met à disposition la liste noire active et la liste des ports interdits,
consommées par le Moteur de détection pour les règles « communication
avec une IP blacklistée » et « utilisation de ports interdits ».
"""

import json

from sqlalchemy.orm import Session

from app.configuration.models import AdresseListeNoire, ParametreConfiguration, StatutListeNoire

NOM_PARAMETRE_PORTS_INTERDITS = "ports_interdits"


def adresses_blacklistees_actives(session: Session) -> frozenset[str]:
    lignes = (
        session.query(AdresseListeNoire.adresse_ip)
        .filter(AdresseListeNoire.statut == StatutListeNoire.ACTIVE)
        .all()
    )
    return frozenset(adresse_ip for (adresse_ip,) in lignes)


def ports_interdits_actifs(session: Session) -> frozenset[int]:
    """Liste des ports interdits, stockée comme paramètre de configuration
    générique (`ParametreConfiguration`, valeur JSON) plutôt que dans une
    entité dédiée, conformément au rôle de ce module (docs/architecture_
    logicielle.md, section 4.10 : « paramètres, seuils, listes noires »).
    Retourne un ensemble vide si le paramètre n'est pas encore défini.
    """
    parametre = (
        session.query(ParametreConfiguration)
        .filter(ParametreConfiguration.nom_parametre == NOM_PARAMETRE_PORTS_INTERDITS)
        .first()
    )
    if parametre is None:
        return frozenset()
    return frozenset(json.loads(parametre.valeur))
