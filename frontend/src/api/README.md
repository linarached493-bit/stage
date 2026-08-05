# Client API

**Implémenté (partiel)** :
- `httpClient.js` — client HTTP bas niveau générique (URL de base, en-têtes JSON, gestion des erreurs) utilisé par tous les services de ressource.
- `authService.js` — `seConnecter()` (POST /v1/auth/login) et `consulterSession()` (GET /v1/auth/session).
- `client.js` — conservé tel quel pour `fetchAlertes()`, utilisé par `features/alerts/AlertsPage.jsx` (page non encore raccordée au routage).

Point d'accès unique vers l'API Backend, conformément au principe retenu dans `docs/specifications_techniques.md` (section 7). À compléter au fur et à mesure de l'ajout des autres ressources (logs, règles, statistiques, configuration, liste noire, utilisateurs) : un service dédié par ressource, construit sur `httpClient.js`.
