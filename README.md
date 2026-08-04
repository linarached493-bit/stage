# IDS — Centre Cinématographique Marocain (CCM)

Système de détection d'intrusion (IDS) réseau pédagogique, développé dans le cadre d'un stage d'observation de fin de première année de cycle d'ingénieur.

> **État du projet :** Phase 1 — Initialisation terminée. Aucune fonctionnalité métier n'est encore implémentée (voir [Statut d'avancement](#statut-davancement)).

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

Toute décision de code doit rester cohérente avec ces documents. En cas de doute sur un choix d'implémentation, ils font foi.

## Organisation du dépôt

```
ccm-ids/
├── docs/            Livrables de conception (voir tableau ci-dessus)
├── backend/         API et logique métier (Python / FastAPI)
├── frontend/        Interface Web (React / Vite)
├── docker-compose.yml
└── .env.example
```

### Backend

Le backend est organisé en un module par responsabilité, reprenant directement le découpage défini dans [l'architecture logicielle](docs/architecture_logicielle.md) (section 4) :

| Dossier (`backend/app/`) | Module de l'architecture logicielle |
|---|---|
| `capture/` | Capture réseau |
| `analysis/` | Analyse |
| `detection/` | Moteur de détection |
| `alerts/` | Gestion des alertes |
| `eventlog/` | Journalisation |
| `auth/` | Authentification |
| `api/` | API Backend |
| `configuration/` | Configuration |
| `database/` | Base de données (accès aux données) |
| `core/` | Éléments transverses de l'application (configuration technique, non un module métier) |

Chaque dossier est un module Python distinct ; aucun ne doit dépendre de l'implémentation interne d'un autre, seulement des données qu'il échange avec lui, conformément au principe de faible couplage retenu dans l'architecture logicielle.

### Frontend

L'interface web est organisée par fonctionnalité, reprenant les ressources définies dans la [conception de l'API REST](docs/conception_api_rest.md) (section 3) :

| Dossier (`frontend/src/features/`) | Ressource API correspondante |
|---|---|
| `auth/` | Authentification |
| `alerts/` | Alertes |
| `logs/` | Logs |
| `rules/` | Règles |
| `statistics/` | Statistiques |
| `users/` | Utilisateurs |
| `configuration/` | Configuration |
| `blacklist/` | Liste noire |

Le dossier `frontend/src/api/` accueillera le futur client HTTP centralisé, seul point d'échange avec le backend, conformément au principe d'accès unique déjà retenu dans les spécifications techniques.

## Statut d'avancement

Le développement suit strictement l'ordre des phases défini dans le [plan de développement](docs/plan_de_developpement.md) (section 3). Une seule phase est développée à la fois, avec validation avant de passer à la suivante.

- [x] **Phase 1 — Initialisation du projet** : structure de dépôt, environnements backend/frontend, configuration Docker, outillage qualité (formatage, linting), intégration continue de base.
- [ ] Phase 2 — Base de données
- [ ] Phase 3 — Backend (couche d'accès aux données)
- [ ] Phase 4 — Capture réseau
- [ ] Phase 5 — Moteur de détection
- [ ] Phase 6 — Authentification
- [ ] Phase 7 — API REST
- [ ] Phase 8 — Interface Web
- [ ] Phase 9 — Intégration
- [ ] Phase 10 — Tests
- [ ] Phase 11 — Documentation
- [ ] Phase 12 — Préparation de la démonstration

À ce stade, le backend expose une application FastAPI sans aucune route, et le frontend affiche un écran vide de démarrage : il ne s'agit que de l'échafaudage du projet.

## Environnement technique

Conforme aux choix technologiques validés (cahier des charges, section 8) : Python/FastAPI, PostgreSQL, React, Docker, Linux.

| Choix | Justification |
|---|---|
| Gestionnaire de paquets backend | `pip` avec `requirements.txt` / `requirements-dev.txt` : simple, standard, adapté au périmètre pédagogique du projet (cohérent avec le principe de simplicité retenu dans les exigences non fonctionnelles). |
| Formatage / lint backend | `black` (formatage) et `ruff` (lint), configurés dans `backend/pyproject.toml`. |
| Outil de build frontend | `Vite` : outil de développement léger adapté à une application React consommant une API REST, sans nécessiter de rendu serveur. |
| Formatage / lint frontend | `ESLint` et `Prettier`, configurés dans `frontend/`. |

Ces choix précisent, au niveau de l'outillage, les technologies déjà validées dans les livrables de conception ; ils n'introduisent aucune technologie non prévue par ces documents.

## Démarrage de l'environnement

```
cp .env.example .env
docker compose up --build
```

- Backend disponible sur `http://localhost:8000` (documentation interactive générée automatiquement sur `/docs`, sans route métier à ce stade).
- Frontend disponible sur `http://localhost:5173`.

Aucune table de base de données, aucun compte utilisateur et aucune règle de détection ne sont créés à ce stade : ces éléments seront introduits progressivement à partir de la Phase 2.
