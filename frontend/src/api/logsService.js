// Service Logs (docs/conception_api_rest.md, section 4.4). Consultation
// uniquement : app/eventlog/service.py n'expose aucune fonction de
// création, modification ou suppression, donc ce service non plus.

import { requeteAuthentifiee } from "./httpClient";

function construireParametresRecherche(filtres) {
  const parametres = new URLSearchParams();
  if (filtres?.niveau) parametres.set("niveau", filtres.niveau);
  if (filtres?.typeEvenement) parametres.set("type_evenement", filtres.typeEvenement);
  if (filtres?.adresseIp) parametres.set("adresse_ip", filtres.adresseIp);
  if (filtres?.dateDebut) parametres.set("date_debut", filtres.dateDebut);
  if (filtres?.dateFin) parametres.set("date_fin", filtres.dateFin);
  if (filtres?.recherche) parametres.set("recherche", filtres.recherche);
  const chaine = parametres.toString();
  return chaine ? `?${chaine}` : "";
}

export function fetchLogs(jeton, filtres) {
  return requeteAuthentifiee(`/v1/logs${construireParametresRecherche(filtres)}`, jeton);
}

export function fetchLogDetail(jeton, logId) {
  return requeteAuthentifiee(`/v1/logs/${logId}`, jeton);
}
