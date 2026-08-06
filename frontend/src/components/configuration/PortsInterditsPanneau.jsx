import { useState } from "react";

function analyserPorts(texte) {
  return texte
    .split(",")
    .map((valeur) => valeur.trim())
    .filter((valeur) => valeur !== "")
    .map(Number);
}

// Consultation et modification réunies dans un même formulaire toujours
// visible (pas de bascule affichage/édition) : les ports interdits forment
// une seule valeur (une liste), pas une collection d'éléments distincts à
// sélectionner comme les paramètres génériques ou la liste noire.
function PortsInterditsPanneau({ ports, enCours, erreur, onSoumettre }) {
  const [portsTexte, setPortsTexte] = useState(ports.join(", "));

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    await onSoumettre(analyserPorts(portsTexte));
  }

  return (
    <form onSubmit={gererSoumission}>
      <div>
        <label htmlFor="ports-interdits">Ports interdits (séparés par des virgules)</label>
        <input
          id="ports-interdits"
          value={portsTexte}
          onChange={(evenement) => setPortsTexte(evenement.target.value)}
        />
      </div>
      {erreur && <p role="alert">{erreur}</p>}
      <button type="submit" disabled={enCours}>
        Enregistrer les ports interdits
      </button>
    </form>
  );
}

export default PortsInterditsPanneau;
