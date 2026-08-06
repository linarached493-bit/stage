// Page Règles : création + liste + détail/traitement d'une règle
// sélectionnée. Même architecture que pages/AlertsPage.jsx et
// pages/UsersPage.jsx : toute la logique vit dans useRegles(), cette page
// assemble les composants présentationnels.

import { useState } from "react";
import { GRAVITES } from "../components/alerts/alertLabels";
import RegleDetail from "../components/rules/RegleDetail";
import RegleFormulaire from "../components/rules/RegleFormulaire";
import ReglesTable from "../components/rules/ReglesTable";
import { INDICATEURS } from "../components/rules/ruleLabels";
import { useRegles } from "../hooks/useRegles";

const VALEURS_INITIALES_CREATION = {
  nom: "",
  description: "",
  typeMenace: "",
  gravite: GRAVITES[0].valeur,
  indicateur: INDICATEURS[0].valeur,
  seuil: 1,
  fenetreSecondes: "",
  typeEvenement: "",
};

function RulesPage() {
  const [creationOuverte, setCreationOuverte] = useState(false);
  const {
    regles,
    chargementListe,
    erreurListe,
    regleSelectionneeId,
    regleDetail,
    chargementDetail,
    erreurDetail,
    actionEnCours,
    creationEnCours,
    erreurCreation,
    selectionnerRegle,
    fermerDetail,
    creer,
    modifier,
    changerStatut,
  } = useRegles();

  async function gererCreation(donnees) {
    const succes = await creer(donnees);
    if (succes) setCreationOuverte(false);
    return succes;
  }

  return (
    <section>
      <h1>Règles</h1>

      <button type="button" onClick={() => setCreationOuverte((valeur) => !valeur)}>
        {creationOuverte ? "Annuler" : "Créer une règle"}
      </button>

      {creationOuverte && (
        <RegleFormulaire
          idPrefix="creation"
          valeursInitiales={VALEURS_INITIALES_CREATION}
          libelleSoumission="Créer"
          enCours={creationEnCours}
          erreur={erreurCreation}
          onSoumettre={gererCreation}
        />
      )}

      {chargementListe && <p>Chargement des règles...</p>}
      {erreurListe && <p role="alert">{erreurListe}</p>}
      {!chargementListe && !erreurListe && (
        <ReglesTable
          regles={regles}
          regleSelectionneeId={regleSelectionneeId}
          onSelectionner={selectionnerRegle}
        />
      )}

      {regleSelectionneeId && chargementDetail && <p>Chargement du détail...</p>}
      {regleSelectionneeId && !chargementDetail && erreurDetail && !regleDetail && (
        <p role="alert">{erreurDetail}</p>
      )}
      {regleSelectionneeId && regleDetail && (
        <RegleDetail
          regle={regleDetail}
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

export default RulesPage;
