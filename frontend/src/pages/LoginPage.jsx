import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function LoginPage() {
  const { connecter, estAuthentifie } = useAuth();
  const [nomUtilisateur, setNomUtilisateur] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState(null);
  const [enCours, setEnCours] = useState(false);

  // Déjà connecté (session restaurée depuis le stockage local) : inutile
  // de repasser par le formulaire.
  if (estAuthentifie) {
    return <Navigate to="/" replace />;
  }

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await connecter(nomUtilisateur, motDePasse);
      // Pas de navigation manuelle ici : `estAuthentifie` passe à `true`
      // et le garde ci-dessus déclenche la redirection au rendu suivant.
    } catch {
      setErreur("Identifiants invalides.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <main className="page-connexion">
      <h1>IDS — Connexion</h1>
      <form onSubmit={gererSoumission}>
        <div>
          <label htmlFor="nom-utilisateur">Nom d&apos;utilisateur</label>
          <input
            id="nom-utilisateur"
            value={nomUtilisateur}
            onChange={(evenement) => setNomUtilisateur(evenement.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="mot-de-passe">Mot de passe</label>
          <input
            id="mot-de-passe"
            type="password"
            value={motDePasse}
            onChange={(evenement) => setMotDePasse(evenement.target.value)}
            required
          />
        </div>
        {erreur && <p role="alert">{erreur}</p>}
        <button type="submit" disabled={enCours}>
          {enCours ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </main>
  );
}

export default LoginPage;
