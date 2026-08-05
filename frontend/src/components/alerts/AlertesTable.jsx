import Badge from "../Badge";
import { libelleGravite, libelleStatut, toneGravite, toneStatut } from "./alertLabels";

function AlertesTable({ alertes, alerteSelectionneeId, onSelectionner }) {
  if (alertes.length === 0) {
    return <p>Aucune alerte ne correspond aux critères.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Identifiant</th>
          <th>Menace</th>
          <th>Gravité</th>
          <th>Statut</th>
          <th>Date de création</th>
          <th>IP source</th>
          <th aria-hidden="true"></th>
        </tr>
      </thead>
      <tbody>
        {alertes.map((alerte) => (
          <tr key={alerte.id} aria-current={alerte.id === alerteSelectionneeId || undefined}>
            <td>{alerte.id}</td>
            <td>{alerte.type_menace}</td>
            <td>
              <Badge tone={toneGravite(alerte.gravite)}>{libelleGravite(alerte.gravite)}</Badge>
            </td>
            <td>
              <Badge tone={toneStatut(alerte.statut_traitement)}>
                {libelleStatut(alerte.statut_traitement)}
              </Badge>
            </td>
            <td>{new Date(alerte.horodatage_detection).toLocaleString()}</td>
            <td>{alerte.ip_source}</td>
            <td>
              <button type="button" onClick={() => onSelectionner(alerte.id)}>
                Détails
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default AlertesTable;
