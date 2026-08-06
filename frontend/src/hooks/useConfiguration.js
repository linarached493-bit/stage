// Logique métier de la page Configuration : trois sous-ressources
// indépendantes (paramètres génériques, ports interdits, liste noire),
// chacune avec son propre chargement/erreur, mais un seul hook — comme un
// seul service API et une seule page les regroupent déjà côté backend et
// côté conception. N'accède au jeton que via useAuth() : aucune logique de
// session dupliquée depuis context/AuthContext.jsx.
//
// Particularité par rapport à useAlertes/useUtilisateurs/useRegles : la
// sélection d'un paramètre à modifier ne déclenche aucun appel réseau
// supplémentaire (GET /v1/configuration renvoie déjà toutes les données
// nécessaires à son édition) et la fermeture du panneau après une
// modification réussie est gérée ici, pas dans la page, puisque c'est le
// hook qui possède déjà l'état de sélection.

import { useCallback, useEffect, useState } from "react";
import {
  ajouterAdresseListeNoire as ajouterAdresseListeNoireApi,
  changerStatutListeNoire,
  fetchListeNoire,
  fetchParametres,
  fetchPortsInterdits,
  modifierParametre as modifierParametreApi,
  modifierPortsInterdits as modifierPortsInterditsApi,
} from "../api/configurationService";
import { useAuth } from "../context/AuthContext";

export function useConfiguration() {
  const { jeton } = useAuth();

  // --- Paramètres génériques ---------------------------------------------
  const [parametres, setParametres] = useState([]);
  const [chargementParametres, setChargementParametres] = useState(true);
  const [erreurParametres, setErreurParametres] = useState(null);
  const [parametreSelectionneNom, setParametreSelectionneNom] = useState(null);
  const [modificationParametreEnCours, setModificationParametreEnCours] = useState(false);
  const [erreurModificationParametre, setErreurModificationParametre] = useState(null);

  const rechargerParametres = useCallback(() => {
    setChargementParametres(true);
    setErreurParametres(null);
    return fetchParametres(jeton)
      .then(setParametres)
      .catch(() => setErreurParametres("Impossible de récupérer les paramètres."))
      .finally(() => setChargementParametres(false));
  }, [jeton]);

  useEffect(() => {
    rechargerParametres();
  }, [rechargerParametres]);

  const parametreSelectionne =
    parametres.find((p) => p.nom_parametre === parametreSelectionneNom) ?? null;

  function selectionnerParametre(nom) {
    setParametreSelectionneNom(nom);
    setErreurModificationParametre(null);
  }

  function fermerModificationParametre() {
    setParametreSelectionneNom(null);
    setErreurModificationParametre(null);
  }

  async function modifierParametre(nom, valeur, description) {
    setModificationParametreEnCours(true);
    setErreurModificationParametre(null);
    try {
      await modifierParametreApi(jeton, nom, valeur, description);
      await rechargerParametres();
      setParametreSelectionneNom(null);
      return true;
    } catch {
      setErreurModificationParametre("Impossible de modifier ce paramètre.");
      return false;
    } finally {
      setModificationParametreEnCours(false);
    }
  }

  // --- Ports interdits ------------------------------------------------------
  const [portsInterdits, setPortsInterdits] = useState([]);
  const [chargementPorts, setChargementPorts] = useState(true);
  const [erreurPorts, setErreurPorts] = useState(null);
  const [modificationPortsEnCours, setModificationPortsEnCours] = useState(false);
  const [erreurModificationPorts, setErreurModificationPorts] = useState(null);

  const rechargerPorts = useCallback(() => {
    setChargementPorts(true);
    setErreurPorts(null);
    return fetchPortsInterdits(jeton)
      .then((donnees) => setPortsInterdits(donnees.ports))
      .catch(() => setErreurPorts("Impossible de récupérer les ports interdits."))
      .finally(() => setChargementPorts(false));
  }, [jeton]);

  useEffect(() => {
    rechargerPorts();
  }, [rechargerPorts]);

  async function modifierPortsInterdits(ports) {
    setModificationPortsEnCours(true);
    setErreurModificationPorts(null);
    try {
      const donnees = await modifierPortsInterditsApi(jeton, ports);
      setPortsInterdits(donnees.ports);
      return true;
    } catch {
      setErreurModificationPorts("Impossible de modifier les ports interdits.");
      return false;
    } finally {
      setModificationPortsEnCours(false);
    }
  }

  // --- Liste noire ---------------------------------------------------------
  const [listeNoire, setListeNoire] = useState([]);
  const [chargementListeNoire, setChargementListeNoire] = useState(true);
  const [erreurListeNoire, setErreurListeNoire] = useState(null);
  const [ajoutEnCours, setAjoutEnCours] = useState(false);
  const [erreurAjout, setErreurAjout] = useState(null);
  const [changementStatutEnCoursId, setChangementStatutEnCoursId] = useState(null);
  const [erreurChangementStatut, setErreurChangementStatut] = useState(null);

  const rechargerListeNoire = useCallback(() => {
    setChargementListeNoire(true);
    setErreurListeNoire(null);
    return fetchListeNoire(jeton)
      .then(setListeNoire)
      .catch(() => setErreurListeNoire("Impossible de récupérer la liste noire."))
      .finally(() => setChargementListeNoire(false));
  }, [jeton]);

  useEffect(() => {
    rechargerListeNoire();
  }, [rechargerListeNoire]);

  async function ajouterAdresseListeNoire(donnees) {
    setAjoutEnCours(true);
    setErreurAjout(null);
    try {
      await ajouterAdresseListeNoireApi(jeton, donnees.adresseIp, donnees.motifSource);
      await rechargerListeNoire();
      return true;
    } catch {
      setErreurAjout("Impossible d'ajouter cette adresse. Vérifiez qu'elle n'est pas déjà listée.");
      return false;
    } finally {
      setAjoutEnCours(false);
    }
  }

  async function changerStatutAdresseListeNoire(entreeId, statut) {
    setChangementStatutEnCoursId(entreeId);
    setErreurChangementStatut(null);
    try {
      await changerStatutListeNoire(jeton, entreeId, statut);
      await rechargerListeNoire();
      return true;
    } catch {
      setErreurChangementStatut("Impossible de modifier le statut de cette adresse.");
      return false;
    } finally {
      setChangementStatutEnCoursId(null);
    }
  }

  return {
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
  };
}
