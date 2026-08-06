// Service Statistiques (docs/conception_api_rest.md, section 4.6). Un seul
// endpoint, sans paramètre, réservé à l'Administrateur et l'Analyste
// sécurité côté backend (app/statistics/router.py).

import { requeteAuthentifiee } from "./httpClient";

export function fetchStatistiques(jeton) {
  return requeteAuthentifiee("/v1/statistiques", jeton);
}
