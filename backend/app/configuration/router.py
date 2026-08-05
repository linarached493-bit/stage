"""Ressources Configuration et Liste noire (docs/conception_api_rest.md,
sections 4.7 et 4.8 ; docs/architecture_logicielle.md, section 4.10).

Lecture : Administrateur et Analyste sécurité. Écriture : Administrateur
seul. Le profil Lecture seule n'a accès à aucune des deux ressources,
conformément à la consigne de ce livrable.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.auth.models import Utilisateur
from app.configuration.models import AdresseListeNoire
from app.configuration.schemas import (
    AdresseListeNoireCreate,
    AdresseListeNoireOut,
    AdresseListeNoireStatutUpdate,
    ParametreOut,
    ParametreUpdate,
    PortsInterditsOut,
    PortsInterditsUpdate,
)
from app.configuration.service import (
    AdresseDejaListee,
    PortInvalide,
    ajouter_adresse_liste_noire,
    changer_statut_liste_noire,
    definir_parametre,
    definir_ports_interdits,
    lister_liste_noire,
    lister_parametres,
    obtenir_entree_liste_noire,
    obtenir_parametre,
    ports_interdits_actifs,
)
from app.database.session import get_db

configuration_router = APIRouter(prefix="/v1/configuration", tags=["Configuration"])
liste_noire_router = APIRouter(prefix="/v1/liste-noire", tags=["Liste noire"])

_verifier_lecture = require_role("Administrateur", "Analyste sécurité")
_verifier_administrateur = require_role("Administrateur")


# --- Configuration (paramètres génériques) ----------------------------------


@configuration_router.get("", response_model=list[ParametreOut])
def lister_configuration(
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_lecture),
) -> list[ParametreOut]:
    return [ParametreOut.depuis_modele(p) for p in lister_parametres(session)]


# Déclarées avant "/{nom}" : une route dynamique enregistrée en premier
# intercepterait "ports-interdits" comme valeur de `nom` et empêcherait
# jamais d'atteindre ces deux routes dédiées.
@configuration_router.get("/ports-interdits", response_model=PortsInterditsOut)
def consulter_ports_interdits(
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_lecture),
) -> PortsInterditsOut:
    return PortsInterditsOut(ports=sorted(ports_interdits_actifs(session)))


@configuration_router.put("/ports-interdits", response_model=PortsInterditsOut)
def modifier_ports_interdits(
    donnees: PortsInterditsUpdate,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> PortsInterditsOut:
    try:
        ports = definir_ports_interdits(session, donnees.ports, utilisateur)
    except PortInvalide as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return PortsInterditsOut(ports=sorted(ports))


@configuration_router.get("/{nom}", response_model=ParametreOut)
def consulter_parametre(
    nom: str,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_lecture),
) -> ParametreOut:
    parametre = obtenir_parametre(session, nom)
    if parametre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paramètre introuvable.")
    return ParametreOut.depuis_modele(parametre)


@configuration_router.put("/{nom}", response_model=ParametreOut)
def modifier_parametre(
    nom: str,
    donnees: ParametreUpdate,
    session: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> ParametreOut:
    parametre = definir_parametre(session, nom, donnees.valeur, utilisateur, donnees.description)
    return ParametreOut.depuis_modele(parametre)


# --- Liste noire ----------------------------------------------------------


def _obtenir_entree_ou_404(session: Session, entree_id: int) -> AdresseListeNoire:
    entree = obtenir_entree_liste_noire(session, entree_id)
    if entree is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entrée de liste noire introuvable."
        )
    return entree


@liste_noire_router.get("", response_model=list[AdresseListeNoireOut])
def lister_entrees(
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_lecture),
) -> list[AdresseListeNoire]:
    return lister_liste_noire(session)


@liste_noire_router.post(
    "", response_model=AdresseListeNoireOut, status_code=status.HTTP_201_CREATED
)
def ajouter_entree(
    donnees: AdresseListeNoireCreate,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> AdresseListeNoire:
    try:
        return ajouter_adresse_liste_noire(session, donnees.adresse_ip, donnees.motif_source)
    except AdresseDejaListee as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse IP figure déjà dans la liste noire.",
        ) from exc


@liste_noire_router.patch("/{entree_id}/statut", response_model=AdresseListeNoireOut)
def modifier_statut_entree(
    entree_id: int,
    donnees: AdresseListeNoireStatutUpdate,
    session: Session = Depends(get_db),
    _utilisateur: Utilisateur = Depends(_verifier_administrateur),
) -> AdresseListeNoire:
    entree = _obtenir_entree_ou_404(session, entree_id)
    return changer_statut_liste_noire(session, entree, donnees.statut)
