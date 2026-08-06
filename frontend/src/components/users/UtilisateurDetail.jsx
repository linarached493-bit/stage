import { useState } from "react";
import Badge from "../Badge";
import UtilisateurFormulaire from "./UtilisateurFormulaire";
import { roleIdParNom } from "./roles";
import { libelleStatutCompte, toneStatutCompte } from "./userLabels";

function UtilisateurDetail({
  utilisateur,
  enCours,
  erreur,
  onFermerPanneau,
  onModifier,
  onChangerStatut,
}) {
  const [modificationOuverte, setModificationOuverte] = useState(false);

  const estActif = utilisateur.statut_compte === "actif";

  async function gererModification(donnees) {
    const succes = await onModifier(donnees);
    if (succes) setModificationOuverte(false);
    return succes;
  }

  return (
    <section
      className="detail-panel"
      aria-label={`Détail de l'utilisateur ${utilisateur.id}`}
    >
      <header>
        <h2>{utilisateur.nom_utilisateur}</h2>
        <button type="button" onClick={onFermerPanneau}>
          Fermer le panneau
        </button>
      </header>

      <dl>
        <dt>Identifiant</dt>
        <dd>{utilisateur.id}</dd>
        <dt>Rôle</dt>
        <dd>{utilisateur.role}</dd>
        <dt>Statut</dt>
        <dd>
          <Badge tone={toneStatutCompte(utilisateur.statut_compte)}>
            {libelleStatutCompte(utilisateur.statut_compte)}
          </Badge>
        </dd>
        <dt>Date de création</dt>
        <dd>{new Date(utilisateur.date_creation).toLocaleString()}</dd>
        <dt>Dernière connexion</dt>
        <dd>
          {utilisateur.date_derniere_connexion
            ? new Date(utilisateur.date_derniere_connexion).toLocaleString()
            : "Jamais connecté"}
        </dd>
      </dl>

      {erreur && <p role="alert">{erreur}</p>}

      <div>
        <button type="button" disabled={enCours} onClick={() => onChangerStatut(estActif ? "desactive" : "actif")}>
          {estActif ? "Désactiver" : "Activer"}
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
        <UtilisateurFormulaire
          idPrefix="modification"
          valeursInitiales={{
            nomUtilisateur: utilisateur.nom_utilisateur,
            roleId: roleIdParNom(utilisateur.role),
          }}
          demanderMotDePasse={false}
          libelleSoumission="Enregistrer"
          enCours={enCours}
          erreur={null}
          onSoumettre={gererModification}
        />
      )}
    </section>
  );
}

export default UtilisateurDetail;
