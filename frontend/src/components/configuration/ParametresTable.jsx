function ParametresTable({ parametres, parametreSelectionneNom, onSelectionner }) {
  if (parametres.length === 0) {
    return <p>Aucun paramètre défini.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Nom</th>
          <th>Valeur</th>
          <th>Description</th>
          <th>Dernière modification</th>
          <th aria-hidden="true"></th>
        </tr>
      </thead>
      <tbody>
        {parametres.map((parametre) => (
          <tr
            key={parametre.nom_parametre}
            aria-current={parametre.nom_parametre === parametreSelectionneNom || undefined}
          >
            <td>{parametre.nom_parametre}</td>
            <td>{parametre.valeur}</td>
            <td>{parametre.description || "—"}</td>
            <td>
              {parametre.date_derniere_modification
                ? new Date(parametre.date_derniere_modification).toLocaleString()
                : "—"}
            </td>
            <td>
              <button type="button" onClick={() => onSelectionner(parametre.nom_parametre)}>
                Modifier
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ParametresTable;
