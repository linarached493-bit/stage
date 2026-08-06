// Logique métier de la page Statistiques : chargement des statistiques et
// rafraîchissement manuel. Le hook le plus simple de tous (avec
// hooks/useLogs.js) : une seule ressource, en lecture seule, sans filtre
// ni sélection. N'accède au jeton que via useAuth(), aucune logique de
// session dupliquée depuis context/AuthContext.jsx.

import { useCallback, useEffect, useState } from "react";
import { fetchStatistiques } from "../api/statisticsService";
import { useAuth } from "../context/AuthContext";

export function useStatistiques() {
  const { jeton } = useAuth();

  const [statistiques, setStatistiques] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);

  const recharger = useCallback(() => {
    setChargement(true);
    setErreur(null);
    return fetchStatistiques(jeton)
      .then(setStatistiques)
      .catch(() => setErreur("Impossible de récupérer les statistiques."))
      .finally(() => setChargement(false));
  }, [jeton]);

  useEffect(() => {
    recharger();
  }, [recharger]);

  return { statistiques, chargement, erreur, recharger };
}
