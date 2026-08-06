import { NavLink } from "react-router-dom";

// Seule la page Statistiques n'est pas encore disponible. Elle sera
// ajoutée ici de la même manière, sans changement de structure, à la
// prochaine étape du plan de développement.
const LIENS = [
  { chemin: "/", libelle: "Tableau de bord" },
  { chemin: "/alertes", libelle: "Alertes" },
  { chemin: "/utilisateurs", libelle: "Utilisateurs" },
  { chemin: "/regles", libelle: "Règles" },
  { chemin: "/logs", libelle: "Logs" },
  { chemin: "/configuration", libelle: "Configuration" },
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
