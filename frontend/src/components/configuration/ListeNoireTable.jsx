import Badge from "../Badge";
import { libelleStatutRegle, toneStatutRegle } from "../rules/ruleLabels";

// StatutListeNoire (app/configuration/models.py) partage exactement le
// vocabulaire active/inactive de StatutRegle : les libellés et couleurs
// sont donc réutilisés depuis components/rules/ruleLabels.js plutôt que
// redéfinis ici, pour éviter toute duplication.
function ListeNoireTable({ entrees, changementStatutEnCoursId, onChangerStatut }) {
  if (entrees.length === 0) {
    return <p>Aucune adresse dans la liste noire.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Adresse IP</th>
          <th>Motif</th>
          <th>Date d&apos;ajout</th>
          <th>Statut</th>
          <th aria-hidden="true"></th>
        </tr>
      </thead>
      <tbody>
        {entrees.map((entree) => {
          const estActive = entree.statut === "active";
          return (
            <tr key={entree.id}>
              <td>{entree.adresse_ip}</td>
              <td>{entree.motif_source || "—"}</td>
              <td>{new Date(entree.date_ajout).toLocaleString()}</td>
              <td>
                <Badge tone={toneStatutRegle(entree.statut)}>
                  {libelleStatutRegle(entree.statut)}
                </Badge>
              </td>
              <td>
                <button
                  type="button"
                  disabled={changementStatutEnCoursId === entree.id}
                  onClick={() => onChangerStatut(entree.id, estActive ? "inactive" : "active")}
                >
                  {estActive ? "Désactiver" : "Activer"}
                </button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default ListeNoireTable;
