// Client HTTP bas niveau : URL de base, en-têtes JSON, gestion des erreurs.
// Point d'accès unique vers l'API Backend (docs/specifications_techniques.md,
// section 7). Les services de chaque ressource (authService.js, ...) s'appuient
// sur ce module plutôt que d'appeler `fetch` directement.

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function traiterReponse(reponse) {
  if (!reponse.ok) {
    throw new ApiError(`La requête a échoué (code ${reponse.status}).`, reponse.status);
  }
  if (reponse.status === 204) {
    return null;
  }
  return reponse.json();
}

export async function requeteJson(chemin, options = {}) {
  const reponse = await fetch(`${API_BASE_URL}${chemin}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  return traiterReponse(reponse);
}

// Requête JSON authentifiée : ajoute l'en-tête Authorization Bearer attendu
// par toutes les ressources protégées de l'API (voir app/auth/dependencies.py).
export async function requeteAuthentifiee(chemin, jeton, options = {}) {
  return requeteJson(chemin, {
    ...options,
    headers: {
      Authorization: `Bearer ${jeton}`,
      ...options.headers,
    },
  });
}
