"""Module Configuration (docs/architecture_logicielle.md, section 4.10).

Met à disposition la liste noire active et la liste des ports interdits,
consommées par le Moteur de détection pour les règles « communication
avec une IP blacklistée » et « utilisation de ports interdits » ; expose
également la gestion complète de ces paramètres (docs/cahier_des_charges.md,
section 6 « Gestion de la configuration »).
"""

import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.auth.models import Utilisateur
from app.configuration.models import AdresseListeNoire, ParametreConfiguration, StatutListeNoire

NOM_PARAMETRE_PORTS_INTERDITS = "ports_interdits"

PORT_MINIMUM = 1
PORT_MAXIMUM = 65535


class AdresseDejaListee(Exception):
    """Violation de la contrainte d'unicité sur `adresse_ip`
    (docs/conception_base_de_donnees.md, section 6.1)."""


class PortInvalide(Exception):
    """Un port fourni n'est pas un entier valide dans la plage
    [1, 65535]."""


# --- Consommation par le moteur de détection (déjà existant) --------------


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
    parametre = obtenir_parametre(session, NOM_PARAMETRE_PORTS_INTERDITS)
    if parametre is None:
        return frozenset()
    return frozenset(json.loads(parametre.valeur))


# --- Paramètres génériques --------------------------------------------------


def lister_parametres(session: Session) -> list[ParametreConfiguration]:
    return (
        session.query(ParametreConfiguration).order_by(ParametreConfiguration.nom_parametre).all()
    )


def obtenir_parametre(session: Session, nom: str) -> ParametreConfiguration | None:
    return (
        session.query(ParametreConfiguration)
        .filter(ParametreConfiguration.nom_parametre == nom)
        .first()
    )


def definir_parametre(
    session: Session,
    nom: str,
    valeur: str,
    utilisateur: Utilisateur,
    description: str | None = None,
) -> ParametreConfiguration:
    """Crée le paramètre s'il n'existe pas encore, le remplace sinon
    (sémantique PUT idempotente, cohérente avec docs/conception_api_rest.md,
    section 4.7 : « PUT /v1/configuration/{nom} — modifie la valeur »)."""
    parametre = obtenir_parametre(session, nom)
    if parametre is None:
        parametre = ParametreConfiguration(
            nom_parametre=nom, valeur=valeur, description=description
        )
        session.add(parametre)
    else:
        parametre.valeur = valeur
        if description is not None:
            parametre.description = description

    parametre.utilisateur_modification = utilisateur
    parametre.date_derniere_modification = datetime.now(UTC)
    session.commit()
    session.refresh(parametre)
    return parametre


# --- Ports interdits (vue typée sur le paramètre générique ci-dessus) ------


def _valider_ports(ports: list[int]) -> None:
    for port in ports:
        if (
            isinstance(port, bool)
            or not isinstance(port, int)
            or not (PORT_MINIMUM <= port <= PORT_MAXIMUM)
        ):
            raise PortInvalide(
                f"Port invalide : {port!r} "
                f"(attendu un entier entre {PORT_MINIMUM} et {PORT_MAXIMUM})."
            )


def definir_ports_interdits(
    session: Session, ports: list[int], utilisateur: Utilisateur
) -> frozenset[int]:
    _valider_ports(ports)
    ensemble = frozenset(ports)
    definir_parametre(
        session,
        NOM_PARAMETRE_PORTS_INTERDITS,
        json.dumps(sorted(ensemble)),
        utilisateur,
        description="Ports interdits par la politique de sécurité du CCM.",
    )
    return ensemble


# --- Liste noire -------------------------------------------------------


def lister_liste_noire(session: Session) -> list[AdresseListeNoire]:
    return session.query(AdresseListeNoire).order_by(AdresseListeNoire.adresse_ip).all()


def obtenir_entree_liste_noire(session: Session, entree_id: int) -> AdresseListeNoire | None:
    return session.get(AdresseListeNoire, entree_id)


def ajouter_adresse_liste_noire(
    session: Session, adresse_ip: str, motif_source: str | None
) -> AdresseListeNoire:
    deja_presente = (
        session.query(AdresseListeNoire).filter(AdresseListeNoire.adresse_ip == adresse_ip).first()
    )
    if deja_presente is not None:
        raise AdresseDejaListee(adresse_ip)

    entree = AdresseListeNoire(adresse_ip=adresse_ip, motif_source=motif_source)
    session.add(entree)
    session.commit()
    session.refresh(entree)
    return entree


def changer_statut_liste_noire(
    session: Session, entree: AdresseListeNoire, statut: StatutListeNoire
) -> AdresseListeNoire:
    """Retrait = désactivation (statut INACTIVE), jamais de suppression
    physique : même principe que pour Alertes/Utilisateurs/Règles
    (docs/conception_base_de_donnees.md, section 6.3), et cohérent avec
    le fait que `AdresseListeNoire.statut` existe précisément pour cela."""
    entree.statut = statut
    session.commit()
    session.refresh(entree)
    return entree
