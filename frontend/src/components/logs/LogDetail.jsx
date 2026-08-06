import Badge from "../Badge";
import { libelleNiveau, resumeMessage, toneNiveau } from "./logLabels";

// Aucune action ici (contrairement à AlerteDetail/UtilisateurDetail/
// RegleDetail) : les logs sont uniquement consultables, conformément à la
// contrainte explicite de ce tour et à app/eventlog/service.py, qui
// n'expose aucune fonction d'écriture.
function LogDetail({ log, onFermerPanneau }) {
  return (
    <section className="detail-panel" aria-label={`Détail du log ${log.id}`}>
      <header>
        <h2>Log #{log.id}</h2>
        <button type="button" onClick={onFermerPanneau}>
          Fermer le panneau
        </button>
      </header>

      <dl>
        <dt>Date</dt>
        <dd>{new Date(log.horodatage).toLocaleString()}</dd>
        <dt>Niveau</dt>
        <dd>
          <Badge tone={toneNiveau(log.niveau)}>{libelleNiveau(log.niveau)}</Badge>
        </dd>
        <dt>Type d&apos;événement</dt>
        <dd>{log.type_evenement}</dd>
        <dt>IP source</dt>
        <dd>{log.ip_source}</dd>
        <dt>IP destination</dt>
        <dd>{log.ip_destination ?? "—"}</dd>
        <dt>Ports</dt>
        <dd>{log.ports ?? "—"}</dd>
        <dt>Protocole</dt>
        <dd>{log.protocole ?? "—"}</dd>
        <dt>Message</dt>
        <dd>{resumeMessage(log)}</dd>
        <dt>Alerte associée</dt>
        <dd>{log.alerte_id != null ? `#${log.alerte_id}` : "Aucune"}</dd>
      </dl>
    </section>
  );
}

export default LogDetail;
