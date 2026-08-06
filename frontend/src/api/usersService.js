// Service Utilisateurs (docs/conception_api_rest.md, section 4.2).
// Réservé à l'Administrateur côté backend (app/auth/router.py) : un
// utilisateur d'un autre rôle recevra une erreur 403 sur ces appels.

import { requeteAuthentifiee } from "./httpClient";

export function fetchUtilisateurs(jeton) {
  return requeteAuthentifiee("/v1/utilisateurs", jeton);
}

export function fetchUtilisateurDetail(jeton, utilisateurId) {
  return requeteAuthentifiee(`/v1/utilisateurs/${utilisateurId}`, jeton);
}

export function creerUtilisateur(jeton, { nomUtilisateur, motDePasse, roleId }) {
  return requeteAuthentifiee("/v1/utilisateurs", jeton, {
    method: "POST",
    body: JSON.stringify({
      nom_utilisateur: nomUtilisateur,
      mot_de_passe: motDePasse,
      role_id: roleId,
    }),
  });
}

export function modifierUtilisateur(jeton, utilisateurId, { nomUtilisateur, roleId }) {
  return requeteAuthentifiee(`/v1/utilisateurs/${utilisateurId}`, jeton, {
    method: "PUT",
    body: JSON.stringify({ nom_utilisateur: nomUtilisateur, role_id: roleId }),
  });
}

export function changerStatutUtilisateur(jeton, utilisateurId, statutCompte) {
  return requeteAuthentifiee(`/v1/utilisateurs/${utilisateurId}/statut`, jeton, {
    method: "PATCH",
    body: JSON.stringify({ statut_compte: statutCompte }),
  });
}
