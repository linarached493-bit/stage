// Service Règles (docs/conception_api_rest.md, section 4.5). Lecture
// ouverte à l'Administrateur et l'Analyste sécurité, écriture réservée à
// l'Administrateur côté backend (app/detection/router.py) : un utilisateur
// d'un autre rôle recevra une erreur 403/401 sur les appels correspondants.

import { requeteAuthentifiee } from "./httpClient";

export function fetchRegles(jeton) {
  return requeteAuthentifiee("/v1/regles", jeton);
}

export function fetchRegleDetail(jeton, regleId) {
  return requeteAuthentifiee(`/v1/regles/${regleId}`, jeton);
}

function corpsRegle({ nom, description, typeMenace, conditionDeclenchement, gravite }) {
  return JSON.stringify({
    nom,
    description: description || null,
    type_menace: typeMenace,
    condition_declenchement: conditionDeclenchement,
    gravite,
  });
}

export function creerRegle(jeton, donnees) {
  return requeteAuthentifiee("/v1/regles", jeton, {
    method: "POST",
    body: corpsRegle(donnees),
  });
}

export function modifierRegle(jeton, regleId, donnees) {
  return requeteAuthentifiee(`/v1/regles/${regleId}`, jeton, {
    method: "PUT",
    body: corpsRegle(donnees),
  });
}

export function changerStatutRegle(jeton, regleId, statut) {
  return requeteAuthentifiee(`/v1/regles/${regleId}/statut`, jeton, {
    method: "PATCH",
    body: JSON.stringify({ statut }),
  });
}
