// Libellés et couleurs (tone) associés à l'énumération renvoyée par le
// backend (app/auth/models.py:StatutCompte).

export const STATUTS_COMPTE = [
  { valeur: "actif", libelle: "Actif" },
  { valeur: "desactive", libelle: "Désactivé" },
];

const TONES_STATUT_COMPTE = { actif: "succes", desactive: "neutre" };

export function libelleStatutCompte(valeur) {
  return STATUTS_COMPTE.find((s) => s.valeur === valeur)?.libelle ?? valeur;
}

export function toneStatutCompte(valeur) {
  return TONES_STATUT_COMPTE[valeur] ?? "neutre";
}
