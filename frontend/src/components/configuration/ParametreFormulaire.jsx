import { useState } from "react";

// Combine consultation et modification dans un même panneau (contrairement
// à AlerteDetail/UtilisateurDetail/RegleDetail, qui séparent une vue
// détail en lecture d'un formulaire de modification) : GET /v1/configuration
// renvoie déjà toute l'information nécessaire à l'édition, une vue détail
// séparée n'ajouterait rien.
function ParametreFormulaire({ nomParametre, valeursInitiales, enCours, erreur, onAnnuler, onSoumettre }) {
  const [valeur, setValeur] = useState(valeursInitiales.valeur);
  const [description, setDescription] = useState(valeursInitiales.description);

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    await onSoumettre({ valeur, description: description || null });
  }

  return (
    <section className="detail-panel" aria-label={`Modifier le paramètre ${nomParametre}`}>
      <header>
        <h2>{nomParametre}</h2>
        <button type="button" onClick={onAnnuler}>
          Fermer le panneau
        </button>
      </header>
      <form onSubmit={gererSoumission}>
        <div>
          <label htmlFor="parametre-valeur">Valeur</label>
          <input
            id="parametre-valeur"
            value={valeur}
            onChange={(evenement) => setValeur(evenement.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="parametre-description">Description</label>
          <input
            id="parametre-description"
            value={description}
            onChange={(evenement) => setDescription(evenement.target.value)}
          />
        </div>
        {erreur && <p role="alert">{erreur}</p>}
        <button type="submit" disabled={enCours}>
          Enregistrer le paramètre
        </button>
      </form>
    </section>
  );
}

export default ParametreFormulaire;
