import { useState } from "react";
import { ROLES } from "./roles";

// Réutilisé pour la création (avec mot de passe) et la modification (sans
// mot de passe, PUT /v1/utilisateurs/{id} ne l'accepte pas) : `idPrefix`
// évite toute collision d'identifiants DOM si les deux formulaires sont
// affichés simultanément sur la page.
function UtilisateurFormulaire({
  idPrefix,
  valeursInitiales = { nomUtilisateur: "", roleId: ROLES[0].id },
  demanderMotDePasse = false,
  libelleSoumission,
  enCours,
  erreur,
  onSoumettre,
}) {
  const [nomUtilisateur, setNomUtilisateur] = useState(valeursInitiales.nomUtilisateur);
  const [motDePasse, setMotDePasse] = useState("");
  const [roleId, setRoleId] = useState(valeursInitiales.roleId);

  async function gererSoumission(evenement) {
    evenement.preventDefault();
    const donnees = { nomUtilisateur, roleId: Number(roleId) };
    if (demanderMotDePasse) donnees.motDePasse = motDePasse;
    const succes = await onSoumettre(donnees);
    if (succes && demanderMotDePasse) setMotDePasse("");
  }

  return (
    <form onSubmit={gererSoumission}>
      <div>
        <label htmlFor={`${idPrefix}-nom-utilisateur`}>Nom d&apos;utilisateur</label>
        <input
          id={`${idPrefix}-nom-utilisateur`}
          value={nomUtilisateur}
          onChange={(evenement) => setNomUtilisateur(evenement.target.value)}
          required
        />
      </div>
      {demanderMotDePasse && (
        <div>
          <label htmlFor={`${idPrefix}-mot-de-passe`}>Mot de passe</label>
          <input
            id={`${idPrefix}-mot-de-passe`}
            type="password"
            value={motDePasse}
            onChange={(evenement) => setMotDePasse(evenement.target.value)}
            required
          />
        </div>
      )}
      <div>
        <label htmlFor={`${idPrefix}-role`}>Rôle</label>
        <select
          id={`${idPrefix}-role`}
          value={roleId}
          onChange={(evenement) => setRoleId(evenement.target.value)}
        >
          {ROLES.map((role) => (
            <option key={role.id} value={role.id}>
              {role.nom}
            </option>
          ))}
        </select>
      </div>
      {erreur && <p role="alert">{erreur}</p>}
      <button type="submit" disabled={enCours}>
        {libelleSoumission}
      </button>
    </form>
  );
}

export default UtilisateurFormulaire;
