"""Schémas Pydantic de la ressource Authentification
(docs/conception_api_rest.md, section 4.1)."""

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UtilisateurOut(BaseModel):
    id: int
    nom_utilisateur: str
    role: str

    model_config = {"from_attributes": True}
