// Service Authentification (docs/conception_api_rest.md, section 4.1).

import { API_BASE_URL, ApiError, requeteAuthentifiee } from "./httpClient";

// POST /v1/auth/login attend un corps x-www-form-urlencoded (Password Flow
// OAuth2, voir app/auth/router.py:login) : traité séparément du client JSON
// générique ci-dessus, qui ne convient pas à ce format de requête.
export async function seConnecter(nomUtilisateur, motDePasse) {
  const corps = new URLSearchParams({ username: nomUtilisateur, password: motDePasse });
  const reponse = await fetch(`${API_BASE_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: corps,
  });

  if (!reponse.ok) {
    throw new ApiError("Identifiants invalides ou compte désactivé.", reponse.status);
  }
  return reponse.json(); // Token : { access_token, token_type }
}

// GET /v1/auth/session : profil de l'utilisateur associé au jeton fourni.
export function consulterSession(jeton) {
  return requeteAuthentifiee("/v1/auth/session", jeton);
}
