// Page Utilisateurs : création + liste filtrable + détail/traitement d'un
// utilisateur sélectionné. Même architecture que pages/AlertsPage.jsx :
// toute la logique vit dans useUtilisateurs(), cette page assemble les
// composants présentationnels.

import { useState } from "react";
import UtilisateurDetail from "../components/users/UtilisateurDetail";
import UtilisateurFormulaire from "../components/users/UtilisateurFormulaire";
import UtilisateursTable from "../components/users/UtilisateursTable";
import { ROLES } from "../components/users/roles";
import { useUtilisateurs } from "../hooks/useUtilisateurs";

function UsersPage() {
  const [creationOuverte, setCreationOuverte] = useState(false);
  const {
    utilisateurs,
    chargementListe,
    erreurListe,
    utilisateurSelectionneId,
    utilisateurDetail,
    chargementDetail,
    erreurDetail,
    actionEnCours,
    creationEnCours,
    erreurCreation,
    selectionnerUtilisateur,
    fermerDetail,
    creer,
    modifier,
    changerStatut,
  } = useUtilisateurs();

  async function gererCreation(donnees) {
    const succes = await creer(donnees);
    if (succes) setCreationOuverte(false);
    return succes;
  }

  return (
    <section>
      <h1>Utilisateurs</h1>

      <button type="button" onClick={() => setCreationOuverte((valeur) => !valeur)}>
        {creationOuverte ? "Annuler" : "Créer un utilisateur"}
      </button>

      {creationOuverte && (
        <UtilisateurFormulaire
          idPrefix="creation"
          valeursInitiales={{ nomUtilisateur: "", roleId: ROLES[0].id }}
          demanderMotDePasse
          libelleSoumission="Créer"
          enCours={creationEnCours}
          erreur={erreurCreation}
          onSoumettre={gererCreation}
        />
      )}

      {chargementListe && <p>Chargement des utilisateurs...</p>}
      {erreurListe && <p role="alert">{erreurListe}</p>}
      {!chargementListe && !erreurListe && (
        <UtilisateursTable
          utilisateurs={utilisateurs}
          utilisateurSelectionneId={utilisateurSelectionneId}
          onSelectionner={selectionnerUtilisateur}
        />
      )}

      {utilisateurSelectionneId && chargementDetail && <p>Chargement du détail...</p>}
      {utilisateurSelectionneId && !chargementDetail && erreurDetail && !utilisateurDetail && (
        <p role="alert">{erreurDetail}</p>
      )}
      {utilisateurSelectionneId && utilisateurDetail && (
        <UtilisateurDetail
          utilisateur={utilisateurDetail}
          enCours={actionEnCours}
          erreur={erreurDetail}
          onFermerPanneau={fermerDetail}
          onModifier={modifier}
          onChangerStatut={changerStatut}
        />
      )}
    </section>
  );
}

export default UsersPage;
