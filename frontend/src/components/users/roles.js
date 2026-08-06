// LIMITATION CONNUE (arbitrage validé avec le donneur d'ordre) : aucun
// endpoint /v1/roles n'existe côté backend (voir app/auth/router.py) pour
// lister les rôles disponibles avec leur identifiant. UtilisateurAdminOut
// n'expose que le *nom* du rôle, jamais son role_id, pourtant requis par
// POST /v1/utilisateurs et PUT /v1/utilisateurs/{id}.
//
// Cette liste est donc codée en dur, couplée à l'ordre de création dans
// backend/app/database/seed.py (ROLES_DE_REFERENCE) et à l'hypothèse d'un
// attribution d'ID auto-incrémenté 1/2/3 sur une base fraîchement
// initialisée. Fragile : si les rôles sont recréés dans un autre ordre, ou
// modifiés directement en base, ces ID seront faux. À remplacer dès qu'un
// endpoint de consultation des rôles existera côté API.
export const ROLES = [
  { id: 1, nom: "Administrateur" },
  { id: 2, nom: "Analyste sécurité" },
  { id: 3, nom: "Lecture seule" },
];

export function roleIdParNom(nom) {
  return ROLES.find((role) => role.nom === nom)?.id ?? ROLES[0].id;
}
