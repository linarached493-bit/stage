import { useState } from "react";
import { login } from "../../api/client";

function LoginPage({ onConnecte }) {
  const [nomUtilisateur, setNomUtilisateur] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState(null);
  const [enCours, setEnCours] = useState(false);

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      const jeton = await login(nomUtilisateur, motDePasse);
      onConnecte(jeton);
    } catch {
      setErreur("Identifiants invalides.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <main>
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
