// Carte simple affichant une valeur numérique et son libellé : un seul
// composant réutilisé pour chacun des cinq indicateurs principaux (aucun
// graphique, conformément à la consigne de ce tour).
function IndicateurCarte({ libelle, valeur }) {
  return (
    <div className="indicateur-carte">
      <p className="indicateur-carte__valeur">{valeur}</p>
      <p className="indicateur-carte__libelle">{libelle}</p>
    </div>
  );
}

export default IndicateurCarte;
