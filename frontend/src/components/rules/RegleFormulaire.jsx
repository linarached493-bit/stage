import { useState } from "react";
import { GRAVITES } from "../alerts/alertLabels";
import { INDICATEURS } from "./ruleLabels";

// Réutilisé pour la création et la modification d'une règle. `idPrefix`
// évite toute collision d'identifiants DOM si les deux formulaires sont
// affichés simultanément sur la page (même motif que
// components/users/UtilisateurFormulaire.jsx).
function RegleFormulaire({ idPrefix, valeursInitiales, libelleSoumission, enCours, erreur, onSoumettre }) {
  const [nom, setNom] = useState(valeursInitiales.nom);
  const [description, setDescription] = useState(valeursInitiales.description);
  const [typeMenace, setTypeMenace] = useState(valeursInitiales.typeMenace);
  const [gravite, setGravite] = useState(valeursInitiales.gravite);
  const [indicateur, setIndicateur] = useState(valeursInitiales.indicateur);
  const [seuil, setSeuil] = useState(valeursInitiales.seuil);
  const [fenetreSecondes, setFenetreSecondes] = useState(valeursInitiales.fenetreSecondes);
  const [typeEvenement, setTypeEvenement] = useState(valeursInitiales.typeEvenement);

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    const conditionDeclenchement = { indicateur, seuil: Number(seuil) };
    if (fenetreSecondes !== "") {
      conditionDeclenchement.fenetre_secondes = Number(fenetreSecondes);
    }
    if (typeEvenement !== "") {
      conditionDeclenchement.type_evenement = typeEvenement;
    }

    await onSoumettre({
      nom,
      description: description || null,
      typeMenace,
      gravite,
      conditionDeclenchement,
    });
  }

  return (
    <form onSubmit={gererSoumission}>
      <div>
        <label htmlFor={`${idPrefix}-nom`}>Nom</label>
        <input
          id={`${idPrefix}-nom`}
          value={nom}
          onChange={(evenement) => setNom(evenement.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor={`${idPrefix}-description`}>Description</label>
        <textarea
          id={`${idPrefix}-description`}
          value={description}
          onChange={(evenement) => setDescription(evenement.target.value)}
        />
      </div>
      <div>
        <label htmlFor={`${idPrefix}-menace`}>Menace</label>
        <input
          id={`${idPrefix}-menace`}
          value={typeMenace}
          onChange={(evenement) => setTypeMenace(evenement.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor={`${idPrefix}-gravite`}>Gravité</label>
        <select
          id={`${idPrefix}-gravite`}
          value={gravite}
          onChange={(evenement) => setGravite(evenement.target.value)}
        >
          {GRAVITES.map((g) => (
            <option key={g.valeur} value={g.valeur}>
              {g.libelle}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor={`${idPrefix}-indicateur`}>Indicateur</label>
        <select
          id={`${idPrefix}-indicateur`}
          value={indicateur}
          onChange={(evenement) => setIndicateur(evenement.target.value)}
        >
          {INDICATEURS.map((i) => (
            <option key={i.valeur} value={i.valeur}>
              {i.libelle}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor={`${idPrefix}-seuil`}>Seuil</label>
        <input
          id={`${idPrefix}-seuil`}
          type="number"
          min="1"
          value={seuil}
          onChange={(evenement) => setSeuil(evenement.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor={`${idPrefix}-fenetre`}>Fenêtre (secondes)</label>
        <input
          id={`${idPrefix}-fenetre`}
          type="number"
          min="1"
          value={fenetreSecondes}
          onChange={(evenement) => setFenetreSecondes(evenement.target.value)}
        />
      </div>
      <div>
        <label htmlFor={`${idPrefix}-type-evenement`}>Type d&apos;événement</label>
        <input
          id={`${idPrefix}-type-evenement`}
          value={typeEvenement}
          onChange={(evenement) => setTypeEvenement(evenement.target.value)}
        />
      </div>
      {erreur && <p role="alert">{erreur}</p>}
      <button type="submit" disabled={enCours}>
        {libelleSoumission}
      </button>
    </form>
  );
}

export default RegleFormulaire;
