import Badge from "../Badge";
import { libelleNiveau, resumeMessage, toneNiveau } from "./logLabels";

function LogsTable({ logs, logSelectionneId, onSelectionner }) {
  if (logs.length === 0) {
    return <p>Aucun log ne correspond aux critères.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Niveau</th>
          <th>Type d&apos;événement</th>
          <th>IP source</th>
          <th>Message</th>
          <th aria-hidden="true"></th>
        </tr>
      </thead>
      <tbody>
        {logs.map((log) => (
          <tr key={log.id} aria-current={log.id === logSelectionneId || undefined}>
            <td>{new Date(log.horodatage).toLocaleString()}</td>
            <td>
              <Badge tone={toneNiveau(log.niveau)}>{libelleNiveau(log.niveau)}</Badge>
            </td>
            <td>{log.type_evenement}</td>
            <td>{log.ip_source}</td>
            <td>{resumeMessage(log)}</td>
            <td>
              <button type="button" onClick={() => onSelectionner(log.id)}>
                Détails
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default LogsTable;
