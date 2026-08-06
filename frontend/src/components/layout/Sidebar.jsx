import { NavLink } from "react-router-dom";

// Seuls le Tableau de bord, les Alertes, les Utilisateurs et les Règles
// sont disponibles à ce stade. Les autres pages (logs, configuration,
// statistiques) seront ajoutées ici une par une, sans changement de
// structure, au fur et à mesure des prochaines étapes du plan de
// développement.
const LIENS = [
  { chemin: "/", libelle: "Tableau de bord" },
  { chemin: "/alertes", libelle: "Alertes" },
  { chemin: "/utilisateurs", libelle: "Utilisateurs" },
  { chemin: "/regles", libelle: "Règles" },
];

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
