// Client HTTP centralisé vers l'API Backend (docs/conception_api_rest.md).
// Seul point d'échange autorisé entre l'Interface Web et le système.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function login(nomUtilisateur, motDePasse) {
  const corps = new URLSearchParams({ username: nomUtilisateur, password: motDePasse });
  const reponse = await fetch(`${API_BASE_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: corps,
  });
  if (!reponse.ok) {
    throw new ApiError("Identifiants invalides ou compte désactivé.", reponse.status);
  }
  const donnees = await reponse.json();
  return donnees.access_token;
}

export async function fetchAlertes(jeton) {
  const reponse = await fetch(`${API_BASE_URL}/v1/alertes`, {
    headers: { Authorization: `Bearer ${jeton}` },
  });
  if (!reponse.ok) {
    throw new ApiError("Impossible de récupérer les alertes.", reponse.status);
  }
  return reponse.json();
}
