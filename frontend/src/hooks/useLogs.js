// Logique métier de la page Logs : chargement de la liste (avec filtres),
// rechargement automatique à chaque changement de filtre, et consultation
// du détail d'un log sélectionné. Contrairement à hooks/useAlertes.js,
// hooks/useUtilisateurs.js et hooks/useRegles.js, aucune action de
// traitement n'existe ici : les logs sont uniquement consultables
// (app/eventlog/service.py n'expose aucune fonction d'écriture).
//
// N'accède au jeton que via useAuth() : aucune logique de session ou de
// stockage n'est dupliquée depuis context/AuthContext.jsx.

import { useCallback, useEffect, useState } from "react";
import { fetchLogDetail, fetchLogs } from "../api/logsService";
import { useAuth } from "../context/AuthContext";

const FILTRES_INITIAUX = {
  niveau: "",
  typeEvenement: "",
  adresseIp: "",
  dateDebut: "",
  dateFin: "",
  recherche: "",
};

export function useLogs() {
  const { jeton } = useAuth();

  const [filtres, setFiltres] = useState(FILTRES_INITIAUX);
  const [logs, setLogs] = useState([]);
  const [chargementListe, setChargementListe] = useState(true);
  const [erreurListe, setErreurListe] = useState(null);

  const [logSelectionneId, setLogSelectionneId] = useState(null);
  const [logDetail, setLogDetail] = useState(null);
  const [chargementDetail, setChargementDetail] = useState(false);
  const [erreurDetail, setErreurDetail] = useState(null);

  const rechargerListe = useCallback(() => {
    setChargementListe(true);
    setErreurListe(null);
    return fetchLogs(jeton, filtres)
      .then(setLogs)
      .catch(() => setErreurListe("Impossible de récupérer les logs."))
      .finally(() => setChargementListe(false));
  }, [jeton, filtres]);

  useEffect(() => {
    rechargerListe();
  }, [rechargerListe]);

  function selectionnerLog(id) {
    setLogSelectionneId(id);
    setChargementDetail(true);
    setErreurDetail(null);
    fetchLogDetail(jeton, id)
      .then(setLogDetail)
      .catch(() => setErreurDetail("Impossible de récupérer le détail du log."))
      .finally(() => setChargementDetail(false));
  }

  function fermerDetail() {
    setLogSelectionneId(null);
    setLogDetail(null);
    setErreurDetail(null);
  }

  return {
    filtres,
    setFiltres,
    logs,
    chargementListe,
    erreurListe,
    logSelectionneId,
    logDetail,
    chargementDetail,
    erreurDetail,
    selectionnerLog,
    fermerDetail,
  };
}
