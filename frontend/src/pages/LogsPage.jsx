// Page Logs : liste filtrable (mise à jour automatique à chaque filtre) +
// détail d'un log sélectionné, en lecture seule. Même architecture que
// pages/AlertsPage.jsx, sans formulaire de création ni action de
// traitement (les logs ne sont pas modifiables).

import LogDetail from "../components/logs/LogDetail";
import LogsFiltres from "../components/logs/LogsFiltres";
import LogsTable from "../components/logs/LogsTable";
import { useLogs } from "../hooks/useLogs";

function LogsPage() {
  const {
    filtres,
    setFiltres,
    logs,
    chargementListe,
    erreurListe,
    logSelectionneId,
    logDetail,
    chargementDetail,
    erreurDetail,
    selectionnerLog,
    fermerDetail,
  } = useLogs();

  function gererChangementFiltre(cle, valeur) {
    setFiltres((precedent) => ({ ...precedent, [cle]: valeur }));
  }

  return (
    <section>
      <h1>Logs</h1>

      <LogsFiltres filtres={filtres} onChangerFiltre={gererChangementFiltre} />

      {chargementListe && <p>Chargement des logs...</p>}
      {erreurListe && <p role="alert">{erreurListe}</p>}
      {!chargementListe && !erreurListe && (
        <LogsTable logs={logs} logSelectionneId={logSelectionneId} onSelectionner={selectionnerLog} />
      )}

      {logSelectionneId && chargementDetail && <p>Chargement du détail...</p>}
      {logSelectionneId && !chargementDetail && erreurDetail && !logDetail && (
        <p role="alert">{erreurDetail}</p>
      )}
      {logSelectionneId && logDetail && <LogDetail log={logDetail} onFermerPanneau={fermerDetail} />}
    </section>
  );
}

export default LogsPage;
