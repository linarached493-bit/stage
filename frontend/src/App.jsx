import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import AlertsPage from "./pages/AlertsPage";
import ConfigurationPage from "./pages/ConfigurationPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import LogsPage from "./pages/LogsPage";
import RulesPage from "./pages/RulesPage";
import StatisticsPage from "./pages/StatisticsPage";
import UsersPage from "./pages/UsersPage";

// Toutes les pages prévues au plan de développement sont désormais
// raccordées. Nouvelle page = nouvelle <Route> sous <AppLayout> ci-dessous,
// plus un lien dans components/layout/Sidebar.jsx.
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
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/configuration" element={<ConfigurationPage />} />
              <Route path="/statistiques" element={<StatisticsPage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
