// Libellés et couleurs (tone) associés à l'énumération renvoyée par le
// backend (app/eventlog/models.py:NiveauLog).
export const NIVEAUX = [
  { valeur: "info", libelle: "Info" },
  { valeur: "avertissement", libelle: "Avertissement" },
  { valeur: "erreur", libelle: "Erreur" },
];

const TONES_NIVEAU = { info: "info", avertissement: "avertissement", erreur: "danger" };

export function libelleNiveau(valeur) {
  return NIVEAUX.find((n) => n.valeur === valeur)?.libelle ?? valeur;
}

export function toneNiveau(valeur) {
  return TONES_NIVEAU[valeur] ?? "neutre";
}

// Vocabulaire connu des `type_evenement` réellement produits par le système
// (app/capture/sniffer.py pour la couche réseau ; indicateur Brute Force
// pour la couche applicative). `LogEvenement.type_evenement` est une simple
// colonne texte, pas un enum contraint côté base — mais le backend filtre
// par égalité stricte (app/eventlog/service.py:lister_logs), donc un champ
// texte libre exposerait l'utilisateur à des filtres qui ne correspondent
// jamais silencieusement à rien : une liste fermée est plus sûre ici.
export const TYPES_EVENEMENT = [
  { valeur: "connexion", libelle: "Connexion" },
  { valeur: "syn", libelle: "SYN" },
  { valeur: "icmp", libelle: "ICMP" },
  { valeur: "echec_authentification", libelle: "Échec d'authentification" },
  { valeur: "authentification_reussie", libelle: "Authentification réussie" },
];

// LIMITATION CONNUE : LogOut n'expose aucun champ `message` libre (voir
// app/eventlog/schemas.py) — seuls type_evenement, niveau, ip_source,
// ip_destination, ports, protocole et alerte_id existent. Ce résumé
// compose donc une ligne lisible à partir des champs réellement
// disponibles, faute de message stocké côté backend. Écart signalé dans
// le rapport de ce tour.
export function resumeMessage(log) {
  const parties = [log.type_evenement];
  if (log.protocole) parties.push(log.protocole);
  if (log.ip_destination) {
    parties.push(
      log.ports ? `vers ${log.ip_destination}:${log.ports}` : `vers ${log.ip_destination}`,
    );
  }
  if (log.alerte_id != null) parties.push(`alerte #${log.alerte_id}`);
  return parties.join(" — ");
}
