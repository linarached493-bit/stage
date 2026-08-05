import { useState } from "react";
import Badge from "../Badge";
import { libelleGravite, libelleStatut, toneGravite, toneStatut } from "./alertLabels";

// Statuts terminaux acceptés par POST .../fermer (voir
// app/alerts/service.py:STATUTS_FERMETURE_VALIDES) : dupliqués ici en
// constante plutôt qu'importés, le frontend n'ayant pas accès au code Python.
const ALERTE_FERMEE = new Set(["traitee", "faux_positif"]);
const STATUTS_FERMETURE = [
  { valeur: "traitee", libelle: "Traitée" },
  { valeur: "faux_positif", libelle: "Faux positif" },
];

function AlerteDetail({
  alerte,
  enCours,
  erreur,
  onFermerPanneau,
  onAcquitter,
  onFermer,
  onCommenter,
}) {
  const [commentaireAcquittement, setCommentaireAcquittement] = useState("");
  const [statutFermeture, setStatutFermeture] = useState(STATUTS_FERMETURE[0].valeur);
  const [commentaireFermeture, setCommentaireFermeture] = useState("");
  const [nouveauCommentaire, setNouveauCommentaire] = useState("");

  // Reflète les règles de transition du backend (app/alerts/service.py) :
  // évite d'afficher une action que l'API refuserait de toute façon.
  const peutAcquitter = alerte.statut_traitement === "nouvelle";
  const peutFermer = !ALERTE_FERMEE.has(alerte.statut_traitement);

  async function gererAcquittement(evenement) {
    evenement.preventDefault();
    const succes = await onAcquitter(commentaireAcquittement || undefined);
    if (succes) setCommentaireAcquittement("");
  }

  async function gererFermeture(evenement) {
    evenement.preventDefault();
    const succes = await onFermer(statutFermeture, commentaireFermeture || undefined);
    if (succes) setCommentaireFermeture("");
  }

  async function gererCommentaire(evenement) {
    evenement.preventDefault();
    const succes = await onCommenter(nouveauCommentaire);
    if (succes) setNouveauCommentaire("");
  }

  return (
    <section className="alerte-detail" aria-label={`Détail de l'alerte ${alerte.id}`}>
      <header>
        <h2>Alerte #{alerte.id}</h2>
        <button type="button" onClick={onFermerPanneau}>
          Fermer le panneau
        </button>
      </header>

      <dl>
        <dt>Menace</dt>
        <dd>{alerte.type_menace}</dd>
        <dt>Règle</dt>
        <dd>{alerte.regle}</dd>
        <dt>Gravité</dt>
        <dd>
          <Badge tone={toneGravite(alerte.gravite)}>{libelleGravite(alerte.gravite)}</Badge>
        </dd>
        <dt>Statut</dt>
        <dd>
          <Badge tone={toneStatut(alerte.statut_traitement)}>
            {libelleStatut(alerte.statut_traitement)}
          </Badge>
        </dd>
        <dt>IP source</dt>
        <dd>{alerte.ip_source}</dd>
        <dt>IP destination</dt>
        <dd>{alerte.ip_destination ?? "—"}</dd>
        <dt>Date de création</dt>
        <dd>{new Date(alerte.horodatage_detection).toLocaleString()}</dd>
      </dl>

      {erreur && <p role="alert">{erreur}</p>}

      <h3>Historique</h3>
      {alerte.historique.length === 0 ? (
        <p>Aucun événement enregistré.</p>
      ) : (
        <ul>
          {alerte.historique.map((entree, index) => (
            <li key={index}>
              {new Date(entree.horodatage).toLocaleString()} — {libelleStatut(entree.statut)} par{" "}
              {entree.utilisateur}
              {entree.commentaire && <> : {entree.commentaire}</>}
            </li>
          ))}
        </ul>
      )}

      {peutAcquitter && (
        <form onSubmit={gererAcquittement}>
          <h3>Acquitter</h3>
          <label htmlFor="commentaire-acquittement">Commentaire (optionnel)</label>
          <textarea
            id="commentaire-acquittement"
            value={commentaireAcquittement}
            onChange={(evenement) => setCommentaireAcquittement(evenement.target.value)}
          />
          <button type="submit" disabled={enCours}>
            Acquitter
          </button>
        </form>
      )}

      {peutFermer && (
        <form onSubmit={gererFermeture}>
          <h3>Fermer</h3>
          <label htmlFor="statut-fermeture">Statut final</label>
          <select
            id="statut-fermeture"
            value={statutFermeture}
            onChange={(evenement) => setStatutFermeture(evenement.target.value)}
          >
            {STATUTS_FERMETURE.map((s) => (
              <option key={s.valeur} value={s.valeur}>
                {s.libelle}
              </option>
            ))}
          </select>
          <label htmlFor="commentaire-fermeture">Commentaire (optionnel)</label>
          <textarea
            id="commentaire-fermeture"
            value={commentaireFermeture}
            onChange={(evenement) => setCommentaireFermeture(evenement.target.value)}
          />
          <button type="submit" disabled={enCours}>
            Fermer
          </button>
        </form>
      )}

      <form onSubmit={gererCommentaire}>
        <h3>Ajouter un commentaire</h3>
        <label htmlFor="nouveau-commentaire">Commentaire</label>
        <textarea
          id="nouveau-commentaire"
          value={nouveauCommentaire}
          onChange={(evenement) => setNouveauCommentaire(evenement.target.value)}
          required
        />
        <button type="submit" disabled={enCours || !nouveauCommentaire.trim()}>
          Commenter
        </button>
      </form>
    </section>
  );
}

export default AlerteDetail;
