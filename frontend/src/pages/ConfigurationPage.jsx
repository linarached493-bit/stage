// Page Configuration : trois sections indépendantes (paramètres génériques,
// ports interdits, liste noire), chacune alimentée par useConfiguration().
// Même architecture que les autres pages : toute la logique vit dans le
// hook, cette page assemble les composants présentationnels.

import ListeNoireFormulaire from "../components/configuration/ListeNoireFormulaire";
import ListeNoireTable from "../components/configuration/ListeNoireTable";
import ParametreFormulaire from "../components/configuration/ParametreFormulaire";
import ParametresTable from "../components/configuration/ParametresTable";
import PortsInterditsPanneau from "../components/configuration/PortsInterditsPanneau";
import { useConfiguration } from "../hooks/useConfiguration";

function ConfigurationPage() {
  const {
    parametres,
    chargementParametres,
    erreurParametres,
    parametreSelectionne,
    selectionnerParametre,
    fermerModificationParametre,
    modificationParametreEnCours,
    erreurModificationParametre,
    modifierParametre,

    portsInterdits,
    chargementPorts,
    erreurPorts,
    modificationPortsEnCours,
    erreurModificationPorts,
    modifierPortsInterdits,

    listeNoire,
    chargementListeNoire,
    erreurListeNoire,
    ajoutEnCours,
    erreurAjout,
    ajouterAdresseListeNoire,
    changementStatutEnCoursId,
    erreurChangementStatut,
    changerStatutAdresseListeNoire,
  } = useConfiguration();

  return (
    <section>
      <h1>Configuration</h1>

      <h2>Paramètres</h2>
      {chargementParametres && <p>Chargement des paramètres...</p>}
      {erreurParametres && <p role="alert">{erreurParametres}</p>}
      {!chargementParametres && !erreurParametres && (
        <ParametresTable
          parametres={parametres}
          parametreSelectionneNom={parametreSelectionne?.nom_parametre ?? null}
          onSelectionner={selectionnerParametre}
        />
      )}
      {parametreSelectionne && (
        <ParametreFormulaire
          nomParametre={parametreSelectionne.nom_parametre}
          valeursInitiales={{
            valeur: parametreSelectionne.valeur,
            description: parametreSelectionne.description || "",
          }}
          enCours={modificationParametreEnCours}
          erreur={erreurModificationParametre}
          onAnnuler={fermerModificationParametre}
          onSoumettre={(donnees) =>
            modifierParametre(parametreSelectionne.nom_parametre, donnees.valeur, donnees.description)
          }
        />
      )}

      <h2>Ports interdits</h2>
      {chargementPorts && <p>Chargement des ports interdits...</p>}
      {erreurPorts && <p role="alert">{erreurPorts}</p>}
      {!chargementPorts && !erreurPorts && (
        <PortsInterditsPanneau
          ports={portsInterdits}
          enCours={modificationPortsEnCours}
          erreur={erreurModificationPorts}
          onSoumettre={modifierPortsInterdits}
        />
      )}

      <h2>Liste noire</h2>
      <ListeNoireFormulaire
        enCours={ajoutEnCours}
        erreur={erreurAjout}
        onSoumettre={ajouterAdresseListeNoire}
      />
      {chargementListeNoire && <p>Chargement de la liste noire...</p>}
      {erreurListeNoire && <p role="alert">{erreurListeNoire}</p>}
      {!chargementListeNoire && !erreurListeNoire && (
        <ListeNoireTable
          entrees={listeNoire}
          changementStatutEnCoursId={changementStatutEnCoursId}
          onChangerStatut={changerStatutAdresseListeNoire}
        />
      )}
      {erreurChangementStatut && <p role="alert">{erreurChangementStatut}</p>}
    </section>
  );
}

export default ConfigurationPage;
