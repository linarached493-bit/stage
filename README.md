# IDS — Centre Cinématographique Marocain (CCM)

Système de détection d'intrusion (IDS) réseau pédagogique, développé dans le cadre d'un stage d'observation de fin de première année de cycle d'ingénieur.

> **État du projet : terminé.** Les 9 menaces de détection, l'ensemble des ressources de l'API REST et les huit pages du frontend prévues au plan de développement sont implémentées. Voir [Fonctionnalités implémentées](#fonctionnalités-implémentées) et [Limitations connues](#limitations-connues) ci-dessous.

## Documentation de conception

L'ensemble de la démarche de conception est disponible dans [`docs/`](docs/), sous forme de huit livrables validés avant le démarrage du développement :

| # | Livrable | Fichier |
|---|---|---|
| 1 | Cahier des charges | [docs/cahier_des_charges.md](docs/cahier_des_charges.md) |
| 2 | Spécifications fonctionnelles et techniques | [docs/specifications_techniques.md](docs/specifications_techniques.md) |
| 3 | Conception UML | [docs/conception_uml.md](docs/conception_uml.md) |
| 4 | Architecture logicielle | [docs/architecture_logicielle.md](docs/architecture_logicielle.md) |
| 5 | Conception de la base de données | [docs/conception_base_de_donnees.md](docs/conception_base_de_donnees.md) |
| 6 | Conception de l'API REST | [docs/conception_api_rest.md](docs/conception_api_rest.md) |
| 7 | Plan de développement | [docs/plan_de_developpement.md](docs/plan_de_developpement.md) |
| 8 | Préparation de l'implémentation | [docs/preparation_implementation.md](docs/preparation_implementation.md) |

Ces documents constituent le dossier de conception original, validé avant le développement, et ne sont pas remaniés a posteriori : tout écart entre eux et l'implémentation finale est documenté dans le code (commentaires) et l'historique Git (messages de commit) au moment où il a été introduit, plutôt que rétroactivement dans les livrables eux-mêmes.

## Organisation du dépôt

```
ccm-ids/
├── docs/                Livrables de conception (voir tableau ci-dessus)
├── backend/             API et logique métier (Python / FastAPI)
├── frontend/            Interface Web (React / Vite)
├── .github/workflows/   Intégration continue (GitHub Actions)
├── docker-compose.yml
└── .env.example
```

### Backend

Le backend est organisé en un module par responsabilité, reprenant le découpage défini dans [l'architecture logicielle](docs/architecture_logicielle.md) (section 4) :

| Dossier (`backend/app/`) | Module de l'architecture logicielle |
|---|---|
| `capture/` | Capture réseau |
| `analysis/` | Analyse |
| `detection/` | Moteur de détection + ressource API Règles |
| `alerts/` | Gestion des alertes + ressource API Alertes |
| `eventlog/` | Journalisation + ressource API Logs |
| `auth/` | Authentification + ressource API Utilisateurs |
| `configuration/` | Configuration + ressources API Configuration et Liste noire |
| `statistics/` | Ressource API Statistiques |
| `database/` | Base de données (modèles, session, données de référence) |
| `core/` | Éléments transverses (configuration technique), non un module métier |

Le module architectural « API Backend » des livrables de conception n'existe pas sous la forme d'un dossier séparé : chaque ressource expose son propre routeur FastAPI (`router.py`) au sein de son module métier, et `backend/app/main.py` les assemble avec le middleware CORS — ce choix, plus proche de l'usage idiomatique de FastAPI, a été retenu au moment de l'implémentation de l'API REST (voir `docs/preparation_implementation.md`).

Chaque dossier est un module Python distinct ; aucun ne dépend de l'implémentation interne d'un autre, seulement des données qu'il échange avec lui.

### Frontend

L'interface web est organisée par couche technique plutôt que par ressource, chaque ressource API étant elle-même déclinée dans chacune de ces couches :

| Dossier (`frontend/src/`) | Rôle |
|---|---|
| `api/` | Client HTTP (`httpClient.js`) et un service par ressource (`alertsService.js`, `usersService.js`, `rulesService.js`, `logsService.js`, `configurationService.js`, `statisticsService.js`, `authService.js`) — seul point d'échange avec le backend. |
| `hooks/` | Toute la logique métier React (chargement, filtres, actions, gestion d'erreurs) d'une ressource, centralisée dans un hook dédié (`useAlertes`, `useUtilisateurs`, `useRegles`, `useLogs`, `useConfiguration`, `useStatistiques`). |
| `components/` | Composants React réutilisables et uniquement présentationnels, groupés par ressource (`components/alerts/`, `components/users/`, ...) plus des composants transverses (`Badge.jsx`, layout, `ProtectedRoute.jsx`). |
| `pages/` | Une page par ressource, assemblant un hook et ses composants. |
| `context/` | `AuthContext.jsx` — authentification JWT et persistance de session, seule source de vérité sur le jeton. |

Cette organisation (introduite à partir de l'écran de connexion, premier développement de la Phase 8) remplace l'organisation par ressource (`features/<ressource>/`) initialement envisagée dans le livrable 7 ; les deux poursuivent le même principe de séparation des responsabilités, seule la manière de les regrouper dans l'arborescence diffère.

## Fonctionnalités implémentées

**Backend** — testé par une suite de 262 tests automatisés (`pytest`, tous passants) :
- Authentification JWT et gestion des rôles (Administrateur / Analyste sécurité / Lecture seule) ;
- Les 9 menaces de détection du cahier des charges (Port Scan, IP blacklistée, Brute Force, SYN Flood, ICMP Flood, Tentatives répétées de connexion, Ports interdits, Activité réseau inhabituelle, Trafic anormal simple) ;
- Toutes les ressources de l'API REST : Authentification, Utilisateurs, Alertes, Règles, Logs, Configuration, Liste noire, Statistiques ;
- Capture réseau (Scapy) : transformation d'un paquet en événement, compatible sans modification avec le moteur de détection.

**Frontend** — huit pages, chacune avec chargement, gestion d'erreurs et tests écrits (voir [Tests](#tests) ci-dessous pour leur statut d'exécution) :
- Connexion, authentification JWT, persistance de session, layout principal (barre latérale + barre supérieure) ;
- Dashboard (informations de l'utilisateur connecté) ;
- Alertes (liste, filtres, détail, acquittement, fermeture, commentaire) ;
- Utilisateurs (liste, création, modification, activation/désactivation) ;
- Règles (liste, création, modification, activation/désactivation) ;
- Logs (liste, filtres, recherche, détail — consultation seule) ;
- Configuration (paramètres, ports interdits, liste noire — consultation et modification) ;
- Statistiques (indicateurs principaux et répartitions, rafraîchissement manuel).

## Limitations connues

- **`frontend/src/components/users/roles.js`** : la liste des rôles (nécessaire pour créer/modifier un utilisateur) est codée en dur, faute d'endpoint `/v1/roles` côté API ; couplée à l'ordre de création dans `backend/app/database/seed.py`.
- **`frontend/src/components/logs/logLabels.js`** : `LogOut` n'expose aucun champ `message` libre côté API ; la colonne « Message » est composée à partir des champs disponibles (type d'événement, protocole, IP destination, ports).
- La capture réseau (`backend/app/capture/sniffer.py:capturer`) n'est appelée par aucun processus au démarrage de l'application : elle est fonctionnelle et testée, mais pas branchée en continu.
- Le frontend ne restreint pas l'affichage selon le rôle de l'utilisateur connecté (seule l'authentification est vérifiée) ; un profil non autorisé sur une ressource obtiendrait une erreur du backend plutôt qu'une interface adaptée.
- Aucune pagination, côté API ou frontend, sur les listes (Alertes, Utilisateurs, Règles, Logs).
- Écarts d'accès volontaires par rapport au cahier des charges d'origine, documentés au fil des livrables : l'écriture sur les Règles est réservée à l'Administrateur seul, et le profil Lecture seule n'a pas accès à Logs, Configuration, Liste noire ni Statistiques.

## Environnement technique

Conforme aux choix technologiques validés (cahier des charges, section 8) : Python/FastAPI, PostgreSQL, React, Docker.

| Choix | Justification |
|---|---|
| Gestionnaire de paquets backend | `pip` avec `requirements.txt` / `requirements-dev.txt`. |
| Formatage / lint backend | `black` (formatage) et `ruff` (lint), configurés dans `backend/pyproject.toml`. |
| Outil de build frontend | `Vite`. |
| Formatage / lint / tests frontend | `ESLint`, `Prettier` et `Vitest` + `React Testing Library`, configurés dans `frontend/`. |

## Démarrage de l'environnement

```
cp .env.example .env
docker compose up --build
```

- Backend disponible sur `http://localhost:8000` (documentation interactive sur `/docs`).
- Frontend disponible sur `http://localhost:5173`.

Aucune donnée n'est pré-remplie hormis les trois rôles de référence (`backend/app/database/seed.py`) : le premier compte Administrateur doit être créé manuellement (script ou requête directe) avant de pouvoir se connecter.

## Tests

| Suite | Commande | Statut |
|---|---|---|
| Backend (`pytest`) | `cd backend && pytest` | **262 tests exécutés et passants** dans cet environnement de développement, ainsi que `black --check .` et `ruff check .`, tous deux sans erreur. |
| Frontend (`vitest`) | `cd frontend && npm install && npm test` | Tests écrits pour chaque page et composant, **jamais exécutés dans l'environnement de développement utilisé pour ce projet** : Node.js n'a pas pu y être installé (blocage sur une invite UAC non interactive lors de l'installation via `winget`, jamais résolu). Le code a été relu manuellement à chaque étape, sans remplacer une exécution réelle. |

La CI GitHub Actions (`.github/workflows/ci.yml`) exécute ces deux suites, ainsi que `eslint`/`prettier --check` côté frontend, à chaque push sur `main` — c'est là que la suite frontend sera réellement exécutée pour la première fois, sur les runners GitHub qui disposent de Node.js. Le workflow installe les dépendances frontend avec `npm install` plutôt que `npm ci`, faute de `package-lock.json` committé (jamais généré, pour la même raison) ; générer et committer un lockfile réel depuis une machine disposant de Node.js est une amélioration recommandée avant toute évolution future du frontend.
