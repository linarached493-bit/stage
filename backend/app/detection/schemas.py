"""Schémas Pydantic de la ressource Règles
(docs/conception_api_rest.md, section 4.5)."""

from pydantic import BaseModel


class RegleOut(BaseModel):
    id: int
    nom: str
    type_menace: str
    gravite: str
    statut: str

    model_config = {"from_attributes": True}
