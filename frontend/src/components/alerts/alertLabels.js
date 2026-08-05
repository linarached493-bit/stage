// Libellés et couleurs (tone) associés aux valeurs d'énumération renvoyées
// par le backend (app/database/enums.py:Gravite, app/alerts/models.py:
// StatutAlerte) : seul endroit à modifier si le vocabulaire évolue.

export const GRAVITES = [
  { valeur: "moyen", libelle: "Moyen" },
  { valeur: "eleve", libelle: "Élevé" },
];

export const STATUTS = [
  { valeur: "nouvelle", libelle: "Nouvelle" },
  { valeur: "en_cours", libelle: "En cours" },
  { valeur: "traitee", libelle: "Traitée" },
  { valeur: "faux_positif", libelle: "Faux positif" },
];

const TONES_GRAVITE = { moyen: "avertissement", eleve: "danger" };
const TONES_STATUT = {
  nouvelle: "info",
  en_cours: "avertissement",
  traitee: "succes",
  faux_positif: "neutre",
};

export function libelleGravite(valeur) {
  return GRAVITES.find((g) => g.valeur === valeur)?.libelle ?? valeur;
}

export function libelleStatut(valeur) {
  return STATUTS.find((s) => s.valeur === valeur)?.libelle ?? valeur;
}

export function toneGravite(valeur) {
  return TONES_GRAVITE[valeur] ?? "neutre";
}

export function toneStatut(valeur) {
  return TONES_STATUT[valeur] ?? "neutre";
}
