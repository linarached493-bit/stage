import { useState } from "react";

function ListeNoireFormulaire({ enCours, erreur, onSoumettre }) {
  const [adresseIp, setAdresseIp] = useState("");
  const [motifSource, setMotifSource] = useState("");

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    const succes = await onSoumettre({ adresseIp, motifSource: motifSource || null });
    if (succes) {
      setAdresseIp("");
      setMotifSource("");
    }
  }

  return (
    <form onSubmit={gererSoumission}>
      <div>
        <label htmlFor="liste-noire-adresse-ip">Adresse IP</label>
        <input
          id="liste-noire-adresse-ip"
          value={adresseIp}
          onChange={(evenement) => setAdresseIp(evenement.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="liste-noire-motif">Motif (optionnel)</label>
        <input
          id="liste-noire-motif"
          value={motifSource}
          onChange={(evenement) => setMotifSource(evenement.target.value)}
        />
      </div>
      {erreur && <p role="alert">{erreur}</p>}
      <button type="submit" disabled={enCours}>
        Ajouter
      </button>
    </form>
  );
}

export default ListeNoireFormulaire;
