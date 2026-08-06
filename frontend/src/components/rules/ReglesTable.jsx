import Badge from "../Badge";
import { libelleGravite, toneGravite } from "../alerts/alertLabels";
import { libelleStatutRegle, resumeCondition, toneStatutRegle } from "./ruleLabels";

function ReglesTable({ regles, regleSelectionneeId, onSelectionner }) {
  if (regles.length === 0) {
    return <p>Aucune règle enregistrée.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Nom</th>
          <th>Menace</th>
          <th>Gravité</th>
          <th>Statut</th>
          <th>Paramètres de déclenchement</th>
          <th aria-hidden="true"></th>
        </tr>
      </thead>
      <tbody>
        {regles.map((regle) => (
          <tr key={regle.id} aria-current={regle.id === regleSelectionneeId || undefined}>
            <td>{regle.nom}</td>
            <td>{regle.type_menace}</td>
            <td>
              <Badge tone={toneGravite(regle.gravite)}>{libelleGravite(regle.gravite)}</Badge>
            </td>
            <td>
              <Badge tone={toneStatutRegle(regle.statut)}>{libelleStatutRegle(regle.statut)}</Badge>
            </td>
            <td>{resumeCondition(regle.condition_declenchement)}</td>
            <td>
              <button type="button" onClick={() => onSelectionner(regle.id)}>
                Détails
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ReglesTable;
