// Badge générique (couleur selon `tone`), réutilisable pour toute valeur
// énumérée à mettre en évidence (gravité, statut, ...), pas seulement pour
// les alertes.

function Badge({ tone = "neutre", children }) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}

export default Badge;
