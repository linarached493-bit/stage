// Garde de route : redirige vers /connexion si aucune session valide n'est
// active. À composer avec react-router-dom via un <Route element={...}>
// englobant (voir App.jsx).

import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute() {
  const { estAuthentifie, verificationSessionEnCours } = useAuth();

  if (verificationSessionEnCours) {
    return <p>Chargement...</p>;
  }
  if (!estAuthentifie) {
    return <Navigate to="/connexion" replace />;
  }
  return <Outlet />;
}

export default ProtectedRoute;
