# Client API

**Implémenté (partiel)** :
- `httpClient.js` — client HTTP bas niveau générique (URL de base, en-têtes JSON, gestion des erreurs) utilisé par tous les services de ressource.
- `authService.js` — `seConnecter()` (POST /v1/auth/login) et `consulterSession()` (GET /v1/auth/session).
- `alertsService.js` — `fetchAlertes()` (avec filtres gravité/statut), `fetchAlerteDetail()`, `acquitterAlerte()`, `fermerAlerte()`, `ajouterCommentaire()`.
- `usersService.js` — `fetchUtilisateurs()`, `fetchUtilisateurDetail()`, `creerUtilisateur()`, `modifierUtilisateur()`, `changerStatutUtilisateur()`.
- `rulesService.js` — `fetchRegles()`, `fetchRegleDetail()`, `creerRegle()`, `modifierRegle()`, `changerStatutRegle()`.
- `logsService.js` — `fetchLogs()` (avec filtres niveau/type d'événement/adresse IP/période/recherche), `fetchLogDetail()`. Consultation uniquement, aucune fonction d'écriture.
- `configurationService.js` — `fetchParametres()`, `modifierParametre()`, `fetchPortsInterdits()`, `modifierPortsInterdits()`, `fetchListeNoire()`, `ajouterAdresseListeNoire()`, `changerStatutListeNoire()`. Regroupe les ressources Configuration et Liste noire (deux routeurs backend distincts, un seul fichier ici comme côté backend).

Point d'accès unique vers l'API Backend, conformément au principe retenu dans `docs/specifications_techniques.md` (section 7). À compléter au fur et à mesure de l'ajout des autres ressources (statistiques) : un service dédié par ressource, construit sur `httpClient.js`.
