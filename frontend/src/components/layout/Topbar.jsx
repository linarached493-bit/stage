import { useAuth } from "../../context/AuthContext";

function Topbar() {
  const { utilisateur, deconnecter } = useAuth();

  return (
    <header className="topbar">
      <span className="topbar__titre">IDS — Centre Cinématographique Marocain</span>
      <div className="topbar__utilisateur">
        <span>
          {utilisateur?.nom_utilisateur} ({utilisateur?.role})
        </span>
        <button type="button" onClick={deconnecter}>
          Se déconnecter
        </button>
      </div>
    </header>
  );
}

export default Topbar;
