// Contexte d'authentification : détient le jeton JWT et le profil de
// l'utilisateur connecté, expose connecter()/deconnecter() et gère seul la
// persistance de session. Aucun autre composant ne doit lire/écrire le
// stockage du jeton directement (voir useAuth() ci-dessous).

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { consulterSession, seConnecter } from "../api/authService";

const CLE_STOCKAGE_JETON = "ccm_ids_jeton";

// Choix de persistance : le backend renvoie le jeton dans le corps JSON
// (pas de cookie httpOnly, hors périmètre de cette étape puisqu'aucune
// modification backend n'est autorisée). Le stocker dans localStorage est
// donc le compromis retenu pour survivre à un rafraîchissement de page ;
// un cookie httpOnly côté serveur resterait la solution la plus robuste
// contre le XSS si le backend évolue un jour dans ce sens.
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [jeton, setJeton] = useState(() => localStorage.getItem(CLE_STOCKAGE_JETON));
  const [utilisateur, setUtilisateur] = useState(null);
  const [verificationSessionEnCours, setVerificationSessionEnCours] = useState(Boolean(jeton));

  // Au chargement (ou si le jeton change), valide le jeton persisté auprès
  // du backend et récupère le profil correspondant. Un jeton invalide ou
  // expiré est silencieusement effacé : l'utilisateur retombe sur l'écran
  // de connexion, sans message d'erreur intrusif.
  useEffect(() => {
    if (!jeton) {
      setVerificationSessionEnCours(false);
      return;
    }
    let annule = false;
    consulterSession(jeton)
      .then((profil) => {
        if (!annule) setUtilisateur(profil);
      })
      .catch(() => {
        if (annule) return;
        localStorage.removeItem(CLE_STOCKAGE_JETON);
        setJeton(null);
        setUtilisateur(null);
      })
      .finally(() => {
        if (!annule) setVerificationSessionEnCours(false);
      });
    return () => {
      annule = true;
    };
  }, [jeton]);

  const connecter = useCallback(async (nomUtilisateur, motDePasse) => {
    const { access_token: nouveauJeton } = await seConnecter(nomUtilisateur, motDePasse);
    const profil = await consulterSession(nouveauJeton);
    localStorage.setItem(CLE_STOCKAGE_JETON, nouveauJeton);
    setJeton(nouveauJeton);
    setUtilisateur(profil);
  }, []);

  const deconnecter = useCallback(() => {
    localStorage.removeItem(CLE_STOCKAGE_JETON);
    setJeton(null);
    setUtilisateur(null);
  }, []);

  const valeur = useMemo(
    () => ({
      jeton,
      utilisateur,
      estAuthentifie: Boolean(jeton && utilisateur),
      verificationSessionEnCours,
      connecter,
      deconnecter,
    }),
    [jeton, utilisateur, verificationSessionEnCours, connecter, deconnecter],
  );

  return <AuthContext.Provider value={valeur}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexte = useContext(AuthContext);
  if (contexte === null) {
    throw new Error("useAuth doit être utilisé à l'intérieur d'un AuthProvider.");
  }
  return contexte;
}
