"""Schéma Pydantic de la ressource Statistiques
(docs/conception_api_rest.md, section 4.6)."""

from pydantic import BaseModel


class StatistiquesOut(BaseModel):
    nombre_total_alertes: int
    alertes_par_gravite: dict[str, int]
    alertes_par_statut: dict[str, int]
    alertes_par_type_menace: dict[str, int]
    regles_actives: int
    regles_inactives: int
    utilisateurs_par_role: dict[str, int]
    adresses_liste_noire: int
    nombre_total_logs: int
