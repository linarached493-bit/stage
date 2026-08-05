// Service Alertes (docs/conception_api_rest.md). La connexion vit désormais
// dans authService.js (voir context/AuthContext.jsx) : ce module ne garde
// que ce qui concerne encore la ressource Alertes, pour éviter toute
// duplication avec httpClient.js.

import { requeteAuthentifiee } from "./httpClient";

export { ApiError } from "./httpClient";

export function fetchAlertes(jeton) {
  return requeteAuthentifiee("/v1/alertes", jeton);
}
