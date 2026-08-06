import Badge from "../Badge";
import { libelleStatutCompte, toneStatutCompte } from "./userLabels";

function UtilisateursTable({ utilisateurs, utilisateurSelectionneId, onSelectionner }) {
  if (utilisateurs.length === 0) {
    return <p>Aucun utilisateur enregistré.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Identifiant</th>
          <th>Nom d&apos;utilisateur</th>
          <th>Rôle</th>
          <th>Statut</th>
          <th>Date de création</th>
          <th aria-hidden="true"></th>
        </tr>
      </thead>
      <tbody>
        {utilisateurs.map((utilisateur) => (
          <tr
            key={utilisateur.id}
            aria-current={utilisateur.id === utilisateurSelectionneId || undefined}
          >
            <td>{utilisateur.id}</td>
            <td>{utilisateur.nom_utilisateur}</td>
            <td>{utilisateur.role}</td>
            <td>
              <Badge tone={toneStatutCompte(utilisateur.statut_compte)}>
                {libelleStatutCompte(utilisateur.statut_compte)}
              </Badge>
            </td>
            <td>{new Date(utilisateur.date_creation).toLocaleString()}</td>
            <td>
              <button type="button" onClick={() => onSelectionner(utilisateur.id)}>
                Détails
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default UtilisateursTable;
