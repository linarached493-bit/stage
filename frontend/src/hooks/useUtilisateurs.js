// Logique métier de la page Utilisateurs : chargement de la liste,
// consultation du détail d'un utilisateur sélectionné, création, et
// actions de traitement (modification, activation/désactivation) avec
// rafraîchissement automatique de la liste et du détail après chaque
// action réussie. Même architecture que hooks/useAlertes.js.
//
// N'accède au jeton que via useAuth() : aucune logique de session ou de
// stockage n'est dupliquée depuis context/AuthContext.jsx.

import { useCallback, useEffect, useState } from "react";
import {
  changerStatutUtilisateur,
  creerUtilisateur,
  fetchUtilisateurDetail,
  fetchUtilisateurs,
  modifierUtilisateur,
} from "../api/usersService";
import { useAuth } from "../context/AuthContext";

export function useUtilisateurs() {
  const { jeton } = useAuth();

  const [utilisateurs, setUtilisateurs] = useState([]);
  const [chargementListe, setChargementListe] = useState(true);
  const [erreurListe, setErreurListe] = useState(null);

  const [utilisateurSelectionneId, setUtilisateurSelectionneId] = useState(null);
  const [utilisateurDetail, setUtilisateurDetail] = useState(null);
  const [chargementDetail, setChargementDetail] = useState(false);
  const [erreurDetail, setErreurDetail] = useState(null);
  const [actionEnCours, setActionEnCours] = useState(false);

  const [creationEnCours, setCreationEnCours] = useState(false);
  const [erreurCreation, setErreurCreation] = useState(null);

  const rechargerListe = useCallback(() => {
    setChargementListe(true);
    setErreurListe(null);
    return fetchUtilisateurs(jeton)
      .then(setUtilisateurs)
      .catch(() => setErreurListe("Impossible de récupérer les utilisateurs."))
      .finally(() => setChargementListe(false));
  }, [jeton]);

  useEffect(() => {
    rechargerListe();
  }, [rechargerListe]);

  function selectionnerUtilisateur(id) {
    setUtilisateurSelectionneId(id);
    setChargementDetail(true);
    setErreurDetail(null);
    fetchUtilisateurDetail(jeton, id)
      .then(setUtilisateurDetail)
      .catch(() => setErreurDetail("Impossible de récupérer le détail de l'utilisateur."))
      .finally(() => setChargementDetail(false));
  }

  function fermerDetail() {
    setUtilisateurSelectionneId(null);
    setUtilisateurDetail(null);
    setErreurDetail(null);
  }

  // Retourne `true`/`false` (plutôt que de lever une exception) : les
  // formulaires appelants s'en servent pour décider de se refermer
  // uniquement en cas de succès.
  async function executerAction(promesseAction) {
    setActionEnCours(true);
    setErreurDetail(null);
    try {
      const utilisateurMisAJour = await promesseAction;
      setUtilisateurDetail(utilisateurMisAJour);
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
    return executerAction(modifierUtilisateur(jeton, utilisateurSelectionneId, donnees));
  }

  function changerStatut(statutCompte) {
    return executerAction(changerStatutUtilisateur(jeton, utilisateurSelectionneId, statutCompte));
  }

  async function creer(donnees) {
    setCreationEnCours(true);
    setErreurCreation(null);
    try {
      await creerUtilisateur(jeton, donnees);
      await rechargerListe();
      return true;
    } catch {
      setErreurCreation("Impossible de créer cet utilisateur. Vérifiez les informations saisies.");
      return false;
    } finally {
      setCreationEnCours(false);
    }
  }

  return {
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
  };
}
