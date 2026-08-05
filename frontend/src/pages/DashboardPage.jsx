// Tableau de bord : message de bienvenue et informations de l'utilisateur
// connecté uniquement (portée de cette étape). Les widgets (alertes
// récentes, statistiques, ...) seront ajoutés ici dans une étape ultérieure.

import { useAuth } from "../context/AuthContext";

function DashboardPage() {
  const { utilisateur } = useAuth();

  return (
    <section>
      <h1>Bienvenue, {utilisateur?.nom_utilisateur}</h1>
      <dl>
        <dt>Nom d&apos;utilisateur</dt>
        <dd>{utilisateur?.nom_utilisateur}</dd>
        <dt>Rôle</dt>
        <dd>{utilisateur?.role}</dd>
      </dl>
    </section>
  );
}

export default DashboardPage;
