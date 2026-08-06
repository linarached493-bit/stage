// Libellés associés à la ressource Règles. La gravité (`GRAVITES`,
// `libelleGravite`, `toneGravite`) n'est PAS redéfinie ici : elle est
// réutilisée telle quelle depuis components/alerts/alertLabels.js, les
// deux ressources partageant exactement le même enum backend
// (app/database/enums.py:Gravite) — voir ce module pour ce cas.

// Reflète app/detection/engine.py:CALCULATEURS_INDICATEURS, un ensemble
// fermé déjà validé côté backend (valider_condition_declenchement) :
// contrairement à components/users/roles.js, cette liste n'est pas une
// hypothèse fragile, c'est la liste exhaustive des indicateurs que le
// moteur de détection sait calculer.
export const INDICATEURS = [
  { valeur: "ports_distincts_par_source", libelle: "Nombre de ports distincts" },
  { valeur: "echecs_consecutifs", libelle: "Échecs d'authentification consécutifs" },
  { valeur: "adresse_dans_liste_noire", libelle: "Adresse dans la liste noire" },
  { valeur: "nombre_evenements_par_source", libelle: "Nombre d'événements d'un type donné" },
  { valeur: "port_interdit_utilise", libelle: "Utilisation d'un port interdit" },
  { valeur: "types_evenements_distincts_par_source", libelle: "Types d'événements distincts" },
  { valeur: "nombre_total_evenements_par_source", libelle: "Volume total d'événements" },
];

export const STATUTS_REGLE = [
  { valeur: "active", libelle: "Active" },
  { valeur: "inactive", libelle: "Inactive" },
];

const TONES_STATUT_REGLE = { active: "succes", inactive: "neutre" };

export function libelleStatutRegle(valeur) {
  return STATUTS_REGLE.find((s) => s.valeur === valeur)?.libelle ?? valeur;
}

export function toneStatutRegle(valeur) {
  return TONES_STATUT_REGLE[valeur] ?? "neutre";
}

// Résumé compact des paramètres de déclenchement (condition_declenchement),
// réutilisé à la fois dans la liste et le détail d'une règle : seul endroit
// à modifier si un nouveau champ de condition doit être affiché.
export function resumeCondition(condition) {
  const parties = [`indicateur : ${condition.indicateur}`, `seuil ≥ ${condition.seuil}`];
  if (condition.fenetre_secondes != null) {
    parties.push(`fenêtre ${condition.fenetre_secondes}s`);
  }
  if (condition.type_evenement) {
    parties.push(`type : ${condition.type_evenement}`);
  }
  return parties.join(", ");
}
