// Services Configuration et Liste noire (docs/conception_api_rest.md,
// sections 4.7 et 4.8). Deux ressources backend distinctes
// (configuration_router, liste_noire_router — app/configuration/router.py)
// mais un seul fichier ici, comme le sont leurs modèles/service Python.

import { requeteAuthentifiee } from "./httpClient";

// --- Paramètres génériques + ports interdits --------------------------

export function fetchParametres(jeton) {
  return requeteAuthentifiee("/v1/configuration", jeton);
}

export function modifierParametre(jeton, nom, valeur, description) {
  return requeteAuthentifiee(`/v1/configuration/${encodeURIComponent(nom)}`, jeton, {
    method: "PUT",
    body: JSON.stringify({ valeur, description: description || null }),
  });
}

export function fetchPortsInterdits(jeton) {
  return requeteAuthentifiee("/v1/configuration/ports-interdits", jeton);
}

export function modifierPortsInterdits(jeton, ports) {
  return requeteAuthentifiee("/v1/configuration/ports-interdits", jeton, {
    method: "PUT",
    body: JSON.stringify({ ports }),
  });
}

// --- Liste noire --------------------------------------------------------

export function fetchListeNoire(jeton) {
  return requeteAuthentifiee("/v1/liste-noire", jeton);
}

export function ajouterAdresseListeNoire(jeton, adresseIp, motifSource) {
  return requeteAuthentifiee("/v1/liste-noire", jeton, {
    method: "POST",
    body: JSON.stringify({ adresse_ip: adresseIp, motif_source: motifSource || null }),
  });
}

export function changerStatutListeNoire(jeton, entreeId, statut) {
  return requeteAuthentifiee(`/v1/liste-noire/${entreeId}/statut`, jeton, {
    method: "PATCH",
    body: JSON.stringify({ statut }),
  });
}
