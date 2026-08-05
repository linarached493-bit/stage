// Logique métier de la page Alertes : chargement de la liste (avec
// filtres), consultation du détail d'une alerte sélectionnée, et actions de
// traitement (acquittement, fermeture, commentaire) avec rafraîchissement
// automatique de la liste et du détail après chaque action réussie.
//
// Séparé de pages/AlertsPage.jsx pour garder cette dernière purement dédiée
// à l'assemblage des composants, et réutilisable si une autre page a besoin
// un jour d'un comportement similaire (liste + détail + actions).

import { useCallback, useEffect, useState } from "react";
import {
  acquitterAlerte,
  ajouterCommentaire,
  fermerAlerte,
  fetchAlerteDetail,
  fetchAlertes,
} from "../api/alertsService";
import { useAuth } from "../context/AuthContext";

export function useAlertes() {
  const { jeton } = useAuth();

  const [filtres, setFiltres] = useState({ gravite: "", statut: "" });
  const [alertes, setAlertes] = useState([]);
  const [chargementListe, setChargementListe] = useState(true);
  const [erreurListe, setErreurListe] = useState(null);

  const [alerteSelectionneeId, setAlerteSelectionneeId] = useState(null);
  const [alerteDetail, setAlerteDetail] = useState(null);
  const [chargementDetail, setChargementDetail] = useState(false);
  const [erreurDetail, setErreurDetail] = useState(null);
  const [actionEnCours, setActionEnCours] = useState(false);

  const rechargerListe = useCallback(() => {
    setChargementListe(true);
    setErreurListe(null);
    return fetchAlertes(jeton, filtres)
      .then(setAlertes)
      .catch(() => setErreurListe("Impossible de récupérer les alertes."))
      .finally(() => setChargementListe(false));
  }, [jeton, filtres]);

  useEffect(() => {
    rechargerListe();
  }, [rechargerListe]);

  function selectionnerAlerte(id) {
    setAlerteSelectionneeId(id);
    setChargementDetail(true);
    setErreurDetail(null);
    fetchAlerteDetail(jeton, id)
      .then(setAlerteDetail)
      .catch(() => setErreurDetail("Impossible de récupérer le détail de l'alerte."))
      .finally(() => setChargementDetail(false));
  }

  function fermerDetail() {
    setAlerteSelectionneeId(null);
    setAlerteDetail(null);
    setErreurDetail(null);
  }

  // Retourne `true`/`false` (plutôt que de lever une exception) : les
  // formulaires appelants s'en servent pour décider de vider leur champ de
  // commentaire uniquement en cas de succès.
  async function executerAction(promesseAction) {
    setActionEnCours(true);
    setErreurDetail(null);
    try {
      const alerteMiseAJour = await promesseAction;
      setAlerteDetail(alerteMiseAJour);
      await rechargerListe();
      return true;
    } catch {
      setErreurDetail("L'action a échoué. Veuillez réessayer.");
      return false;
    } finally {
      setActionEnCours(false);
    }
  }

  function acquitter(commentaire) {
    return executerAction(acquitterAlerte(jeton, alerteSelectionneeId, commentaire));
  }

  function fermer(statutFinal, commentaire) {
    return executerAction(fermerAlerte(jeton, alerteSelectionneeId, statutFinal, commentaire));
  }

  function commenter(commentaire) {
    return executerAction(ajouterCommentaire(jeton, alerteSelectionneeId, commentaire));
  }

  return {
    filtres,
    setFiltres,
    alertes,
    chargementListe,
    erreurListe,
    alerteSelectionneeId,
    alerteDetail,
    chargementDetail,
    erreurDetail,
    actionEnCours,
    selectionnerAlerte,
    fermerDetail,
    acquitter,
    fermer,
    commenter,
  };
}
