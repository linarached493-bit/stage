import { NavLink } from "react-router-dom";

// Seul le Tableau de bord est disponible à ce stade. Les autres pages
// (alertes, règles, utilisateurs, logs, configuration, statistiques) seront
// ajoutées ici une par une, sans changement de structure, au fur et à mesure
// des prochaines étapes du plan de développement.
const LIENS = [{ chemin: "/", libelle: "Tableau de bord" }];

function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Navigation principale">
      <ul>
        {LIENS.map((lien) => (
          <li key={lien.chemin}>
            <NavLink to={lien.chemin} end>
              {lien.libelle}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Sidebar;
