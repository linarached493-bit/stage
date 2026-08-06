import { useState } from "react";
import Badge from "../Badge";
import { libelleGravite, toneGravite } from "../alerts/alertLabels";
import RegleFormulaire from "./RegleFormulaire";
import { libelleStatutRegle, resumeCondition, toneStatutRegle } from "./ruleLabels";

function RegleDetail({ regle, enCours, erreur, onFermerPanneau, onModifier, onChangerStatut }) {
  const [modificationOuverte, setModificationOuverte] = useState(false);

  const estActive = regle.statut === "active";

  async function gererModification(donnees) {
    const succes = await onModifier(donnees);
    if (succes) setModificationOuverte(false);
    return succes;
  }

  return (
    <section className="detail-panel" aria-label={`Détail de la règle ${regle.id}`}>
      <header>
        <h2>{regle.nom}</h2>
        <button type="button" onClick={onFermerPanneau}>
          Fermer le panneau
        </button>
      </header>

      <dl>
        <dt>Menace</dt>
        <dd>{regle.type_menace}</dd>
        <dt>Description</dt>
        <dd>{regle.description || "—"}</dd>
        <dt>Gravité</dt>
        <dd>
          <Badge tone={toneGravite(regle.gravite)}>{libelleGravite(regle.gravite)}</Badge>
        </dd>
        <dt>Statut</dt>
        <dd>
          <Badge tone={toneStatutRegle(regle.statut)}>{libelleStatutRegle(regle.statut)}</Badge>
        </dd>
        <dt>Paramètres de déclenchement</dt>
        <dd>{resumeCondition(regle.condition_declenchement)}</dd>
        <dt>Auteur</dt>
        <dd>{regle.auteur}</dd>
        <dt>Date de création</dt>
        <dd>{new Date(regle.date_creation).toLocaleString()}</dd>
        <dt>Dernière modification</dt>
        <dd>
          {regle.date_derniere_modification
            ? new Date(regle.date_derniere_modification).toLocaleString()
            : "—"}
        </dd>
      </dl>

      {erreur && <p role="alert">{erreur}</p>}

      <div>
        <button
          type="button"
          disabled={enCours}
          onClick={() => onChangerStatut(estActive ? "inactive" : "active")}
        >
          {estActive ? "Désactiver" : "Activer"}
        </button>
        <button
          type="button"
          disabled={enCours}
          onClick={() => setModificationOuverte((valeur) => !valeur)}
        >
          {modificationOuverte ? "Annuler la modification" : "Modifier"}
        </button>
      </div>

      {modificationOuverte && (
        <RegleFormulaire
          idPrefix="modification"
          valeursInitiales={{
            nom: regle.nom,
            description: regle.description || "",
            typeMenace: regle.type_menace,
            gravite: regle.gravite,
            indicateur: regle.condition_declenchement.indicateur,
            seuil: regle.condition_declenchement.seuil,
            fenetreSecondes: regle.condition_declenchement.fenetre_secondes ?? "",
            typeEvenement: regle.condition_declenchement.type_evenement ?? "",
          }}
          libelleSoumission="Enregistrer"
          enCours={enCours}
          erreur={null}
          onSoumettre={gererModification}
        />
      )}
    </section>
  );
}

export default RegleDetail;
