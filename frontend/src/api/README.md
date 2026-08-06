# Client API

**Implémenté (partiel)** :
- `httpClient.js` — client HTTP bas niveau générique (URL de base, en-têtes JSON, gestion des erreurs) utilisé par tous les services de ressource.
- `authService.js` — `seConnecter()` (POST /v1/auth/login) et `consulterSession()` (GET /v1/auth/session).
- `alertsService.js` — `fetchAlertes()` (avec filtres gravité/statut), `fetchAlerteDetail()`, `acquitterAlerte()`, `fermerAlerte()`, `ajouterCommentaire()`.
- `usersService.js` — `fetchUtilisateurs()`, `fetchUtilisateurDetail()`, `creerUtilisateur()`, `modifierUtilisateur()`, `changerStatutUtilisateur()`.

Point d'accès unique vers l'API Backend, conformément au principe retenu dans `docs/specifications_techniques.md` (section 7). À compléter au fur et à mesure de l'ajout des autres ressources (logs, règles, statistiques, configuration, liste noire) : un service dédié par ressource, construit sur `httpClient.js`.
