// Tableau générique clé/valeur pour une répartition ({clé: nombre}), telle
// que renvoyée par GET /v1/statistiques (alertes_par_gravite, par_statut,
// par_type_menace, utilisateurs_par_role) : un seul composant réutilisé
// pour les quatre répartitions plutôt que quatre tableaux similaires.
// `rendreCle` permet un rendu personnalisé de la clé (badge coloré pour
// gravité/statut) ; par défaut la clé est affichée telle quelle.
function RepartitionTable({ titre, repartition, libelleColonneCle, rendreCle }) {
  const entrees = Object.entries(repartition);

  return (
    <section>
      <h3>{titre}</h3>
      {entrees.length === 0 ? (
        <p>Aucune donnée.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>{libelleColonneCle}</th>
              <th>Nombre</th>
            </tr>
          </thead>
          <tbody>
            {entrees.map(([cle, nombre]) => (
              <tr key={cle}>
                <td>{rendreCle ? rendreCle(cle) : cle}</td>
                <td>{nombre}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export default RepartitionTable;
