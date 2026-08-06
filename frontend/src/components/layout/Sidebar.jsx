import { NavLink } from "react-router-dom";

// Toutes les pages prévues au plan de développement sont désormais
// disponibles.
const LIENS = [
  { chemin: "/", libelle: "Tableau de bord" },
  { chemin: "/alertes", libelle: "Alertes" },
  { chemin: "/utilisateurs", libelle: "Utilisateurs" },
  { chemin: "/regles", libelle: "Règles" },
  { chemin: "/logs", libelle: "Logs" },
  { chemin: "/configuration", libelle: "Configuration" },
  { chemin: "/statistiques", libelle: "Statistiques" },
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
