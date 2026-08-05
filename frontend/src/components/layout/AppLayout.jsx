// Mise en page principale (barre latérale + barre supérieure) partagée par
// toutes les pages protégées. Nouvelle page = nouvelle <Route> enfant sous
// <AppLayout> dans App.jsx, sans modifier ce composant.

import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-layout__contenu">
        <Topbar />
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
