import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import AlertsPage from "./pages/AlertsPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RulesPage from "./pages/RulesPage";
import UsersPage from "./pages/UsersPage";

// Nouvelle page = nouvelle <Route> sous <AppLayout> ci-dessous, plus un lien
// dans components/layout/Sidebar.jsx. Logs/Configuration/Statistiques ne
// sont volontairement pas encore raccordées (hors périmètre de cette étape).
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/connexion" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/alertes" element={<AlertsPage />} />
              <Route path="/utilisateurs" element={<UsersPage />} />
              <Route path="/regles" element={<RulesPage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
