import { GRAVITES, STATUTS } from "./alertLabels";

function AlertesFiltres({ gravite, statut, onChangerGravite, onChangerStatut }) {
  return (
    <div className="filtres">
      <div>
        <label htmlFor="filtre-gravite">Gravité</label>
        <select
          id="filtre-gravite"
          value={gravite}
          onChange={(evenement) => onChangerGravite(evenement.target.value)}
        >
          <option value="">Toutes</option>
          {GRAVITES.map((g) => (
            <option key={g.valeur} value={g.valeur}>
              {g.libelle}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="filtre-statut">Statut</label>
        <select
          id="filtre-statut"
          value={statut}
          onChange={(evenement) => onChangerStatut(evenement.target.value)}
        >
          <option value="">Tous</option>
          {STATUTS.map((s) => (
            <option key={s.valeur} value={s.valeur}>
              {s.libelle}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export default AlertesFiltres;
