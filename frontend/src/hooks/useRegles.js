// Logique métier de la page Règles : chargement de la liste, consultation
// du détail d'une règle sélectionnée, création, et actions de traitement
// (modification, activation/désactivation) avec rafraîchissement
// automatique de la liste et du détail après chaque action réussie. Même
// architecture que hooks/useAlertes.js et hooks/useUtilisateurs.js.
//
// N'accède au jeton que via useAuth() : aucune logique de session ou de
// stockage n'est dupliquée depuis context/AuthContext.jsx.

import { useCallback, useEffect, useState } from "react";
import {
  changerStatutRegle,
  creerRegle,
  fetchRegleDetail,
  fetchRegles,
  modifierRegle,
} from "../api/rulesService";
import { useAuth } from "../context/AuthContext";

export function useRegles() {
  const { jeton } = useAuth();

  const [regles, setRegles] = useState([]);
  const [chargementListe, setChargementListe] = useState(true);
  const [erreurListe, setErreurListe] = useState(null);

  const [regleSelectionneeId, setRegleSelectionneeId] = useState(null);
  const [regleDetail, setRegleDetail] = useState(null);
  const [chargementDetail, setChargementDetail] = useState(false);
  const [erreurDetail, setErreurDetail] = useState(null);
  const [actionEnCours, setActionEnCours] = useState(false);

  const [creationEnCours, setCreationEnCours] = useState(false);
  const [erreurCreation, setErreurCreation] = useState(null);

  const rechargerListe = useCallback(() => {
    setChargementListe(true);
    setErreurListe(null);
    return fetchRegles(jeton)
      .then(setRegles)
      .catch(() => setErreurListe("Impossible de récupérer les règles."))
      .finally(() => setChargementListe(false));
  }, [jeton]);

  useEffect(() => {
    rechargerListe();
  }, [rechargerListe]);

  function selectionnerRegle(id) {
    setRegleSelectionneeId(id);
    setChargementDetail(true);
    setErreurDetail(null);
    fetchRegleDetail(jeton, id)
      .then(setRegleDetail)
      .catch(() => setErreurDetail("Impossible de récupérer le détail de la règle."))
      .finally(() => setChargementDetail(false));
  }

  function fermerDetail() {
    setRegleSelectionneeId(null);
    setRegleDetail(null);
    setErreurDetail(null);
  }

  // Retourne `true`/`false` (plutôt que de lever une exception) : les
  // formulaires appelants s'en servent pour décider de se refermer
  // uniquement en cas de succès.
  async function executerAction(promesseAction) {
    setActionEnCours(true);
    setErreurDetail(null);
    try {
      const regleMiseAJour = await promesseAction;
      setRegleDetail(regleMiseAJour);
      await rechargerListe();
      return true;
    } catch {
      setErreurDetail("L'action a échoué. Veuillez réessayer.");
      return false;
    } finally {
      setActionEnCours(false);
    }
  }

  function modifier(donnees) {
    return executerAction(modifierRegle(jeton, regleSelectionneeId, donnees));
  }

  function changerStatut(statut) {
    return executerAction(changerStatutRegle(jeton, regleSelectionneeId, statut));
  }

  async function creer(donnees) {
    setCreationEnCours(true);
    setErreurCreation(null);
    try {
      await creerRegle(jeton, donnees);
      await rechargerListe();
      return true;
    } catch {
      setErreurCreation("Impossible de créer cette règle. Vérifiez les informations saisies.");
      return false;
    } finally {
      setCreationEnCours(false);
    }
  }

  return {
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
  };
}
