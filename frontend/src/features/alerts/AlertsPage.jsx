import { useEffect, useState } from "react";
import { fetchAlertes } from "../../api/client";

function AlertsPage({ jeton, onDeconnexion }) {
  const [alertes, setAlertes] = useState([]);
  const [erreur, setErreur] = useState(null);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    fetchAlertes(jeton)
      .then(setAlertes)
      .catch(() => setErreur("Impossible de récupérer les alertes."))
      .finally(() => setChargement(false));
  }, [jeton]);

  return (
    <main>
      <header>
        <h1>Alertes</h1>
        <button type="button" onClick={onDeconnexion}>
          Se déconnecter
        </button>
      </header>
      {chargement && <p>Chargement...</p>}
      {erreur && <p role="alert">{erreur}</p>}
      {!chargement && !erreur && alertes.length === 0 && <p>Aucune alerte.</p>}
      {alertes.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Horodatage</th>
              <th>Menace</th>
              <th>Source</th>
              <th>Gravité</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {alertes.map((alerte) => (
              <tr key={alerte.id}>
                <td>{new Date(alerte.horodatage_detection).toLocaleString()}</td>
                <td>{alerte.type_menace}</td>
                <td>{alerte.ip_source}</td>
                <td>{alerte.gravite}</td>
                <td>{alerte.statut_traitement}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}

export default AlertsPage;
