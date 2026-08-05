// Page Alertes : liste filtrable + détail/traitement d'une alerte
// sélectionnée. Toute la logique (chargement, filtres, actions) vit dans
// useAlertes() ; cette page ne fait qu'assembler les composants.

import AlerteDetail from "../components/alerts/AlerteDetail";
import AlertesFiltres from "../components/alerts/AlertesFiltres";
import AlertesTable from "../components/alerts/AlertesTable";
import { useAlertes } from "../hooks/useAlertes";

function AlertsPage() {
  const {
    filtres,
    setFiltres,
    alertes,
    chargementListe,
    erreurListe,
    alerteSelectionneeId,
    alerteDetail,
    chargementDetail,
    erreurDetail,
    actionEnCours,
    selectionnerAlerte,
    fermerDetail,
    acquitter,
    fermer,
    commenter,
  } = useAlertes();

  return (
    <section>
      <h1>Alertes</h1>

      <AlertesFiltres
        gravite={filtres.gravite}
        statut={filtres.statut}
        onChangerGravite={(gravite) => setFiltres((precedent) => ({ ...precedent, gravite }))}
        onChangerStatut={(statut) => setFiltres((precedent) => ({ ...precedent, statut }))}
      />

      {chargementListe && <p>Chargement des alertes...</p>}
      {erreurListe && <p role="alert">{erreurListe}</p>}
      {!chargementListe && !erreurListe && (
        <AlertesTable
          alertes={alertes}
          alerteSelectionneeId={alerteSelectionneeId}
          onSelectionner={selectionnerAlerte}
        />
      )}

      {alerteSelectionneeId && chargementDetail && <p>Chargement du détail...</p>}
      {alerteSelectionneeId && !chargementDetail && erreurDetail && !alerteDetail && (
        <p role="alert">{erreurDetail}</p>
      )}
      {alerteSelectionneeId && alerteDetail && (
        <AlerteDetail
          alerte={alerteDetail}
          enCours={actionEnCours}
          erreur={erreurDetail}
          onFermerPanneau={fermerDetail}
          onAcquitter={acquitter}
          onFermer={fermer}
          onCommenter={commenter}
        />
      )}
    </section>
  );
}

export default AlertsPage;
