import { NIVEAUX, TYPES_EVENEMENT } from "./logLabels";

// Un seul callback `onChangerFiltre(cle, valeur)` plutôt qu'un callback par
// champ (comme components/alerts/AlertesFiltres.jsx) : avec six filtres ici
// contre deux pour les Alertes, ça évite une explosion de props.
function LogsFiltres({ filtres, onChangerFiltre }) {
  return (
    <div className="filtres">
      <div>
        <label htmlFor="filtre-niveau">Niveau</label>
        <select
          id="filtre-niveau"
          value={filtres.niveau}
          onChange={(evenement) => onChangerFiltre("niveau", evenement.target.value)}
        >
          <option value="">Tous</option>
          {NIVEAUX.map((n) => (
            <option key={n.valeur} value={n.valeur}>
              {n.libelle}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="filtre-type-evenement">Type d&apos;événement</label>
        <select
          id="filtre-type-evenement"
          value={filtres.typeEvenement}
          onChange={(evenement) => onChangerFiltre("typeEvenement", evenement.target.value)}
        >
          <option value="">Tous</option>
          {TYPES_EVENEMENT.map((t) => (
            <option key={t.valeur} value={t.valeur}>
              {t.libelle}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="filtre-adresse-ip">Adresse IP</label>
        <input
          id="filtre-adresse-ip"
          value={filtres.adresseIp}
          onChange={(evenement) => onChangerFiltre("adresseIp", evenement.target.value)}
        />
      </div>
      <div>
        <label htmlFor="filtre-date-debut">Depuis</label>
        <input
          id="filtre-date-debut"
          type="datetime-local"
          value={filtres.dateDebut}
          onChange={(evenement) => onChangerFiltre("dateDebut", evenement.target.value)}
        />
      </div>
      <div>
        <label htmlFor="filtre-date-fin">Jusqu&apos;à</label>
        <input
          id="filtre-date-fin"
          type="datetime-local"
          value={filtres.dateFin}
          onChange={(evenement) => onChangerFiltre("dateFin", evenement.target.value)}
        />
      </div>
      <div>
        <label htmlFor="filtre-recherche">Recherche</label>
        <input
          id="filtre-recherche"
          value={filtres.recherche}
          onChange={(evenement) => onChangerFiltre("recherche", evenement.target.value)}
          placeholder="Type, protocole, IP..."
        />
      </div>
    </div>
  );
}

export default LogsFiltres;
