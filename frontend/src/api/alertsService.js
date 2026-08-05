// Service Alertes (docs/conception_api_rest.md, section 4.3). Remplace
// l'ancien client.js (retiré : ne couvrait que la lecture, sans filtres ni
// actions de traitement).

import { requeteAuthentifiee } from "./httpClient";

function construireParametresRecherche(filtres) {
  const parametres = new URLSearchParams();
  if (filtres?.gravite) parametres.set("gravite", filtres.gravite);
  if (filtres?.statut) parametres.set("statut", filtres.statut);
  const chaine = parametres.toString();
  return chaine ? `?${chaine}` : "";
}

export function fetchAlertes(jeton, filtres) {
  return requeteAuthentifiee(`/v1/alertes${construireParametresRecherche(filtres)}`, jeton);
}

export function fetchAlerteDetail(jeton, alerteId) {
  return requeteAuthentifiee(`/v1/alertes/${alerteId}`, jeton);
}

export function acquitterAlerte(jeton, alerteId, commentaire) {
  return requeteAuthentifiee(`/v1/alertes/${alerteId}/acquitter`, jeton, {
    method: "PATCH",
    body: JSON.stringify({ commentaire: commentaire || null }),
  });
}

export function fermerAlerte(jeton, alerteId, statutFinal, commentaire) {
  return requeteAuthentifiee(`/v1/alertes/${alerteId}/fermer`, jeton, {
    method: "PATCH",
    body: JSON.stringify({ statut_final: statutFinal, commentaire: commentaire || null }),
  });
}

export function ajouterCommentaire(jeton, alerteId, commentaire) {
  return requeteAuthentifiee(`/v1/alertes/${alerteId}/commentaires`, jeton, {
    method: "POST",
    body: JSON.stringify({ commentaire }),
  });
}
