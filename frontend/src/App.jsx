import { useState } from "react";
import AlertsPage from "./features/alerts/AlertsPage.jsx";
import LoginPage from "./features/auth/LoginPage.jsx";

// Deux écrans seulement : un routeur dédié serait prématuré (voir
// react-router-dom, déjà déclaré en dépendance pour les phases suivantes).
function App() {
  const [jeton, setJeton] = useState(null);

  if (!jeton) {
    return <LoginPage onConnecte={setJeton} />;
  }
  return <AlertsPage jeton={jeton} onDeconnexion={() => setJeton(null)} />;
}

export default App;
