# Plan de développement — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 7 — Plan de développement
**Documents de référence :** `docs/cahier_des_charges.md` (Livrable 1), `docs/specifications_techniques.md` (Livrable 2), `docs/conception_uml.md` (Livrable 3), `docs/architecture_logicielle.md` (Livrable 4), `docs/conception_base_de_donnees.md` (Livrable 5), `docs/conception_api_rest.md` (Livrable 6)
**Statut :** Planification — aucune implémentation

---

## 1. Objectif du document

### 1.1 Rôle du plan de développement

Ce document a pour objectif d'organiser, en phases et en tâches, la réalisation du système déjà conçu dans les six livrables précédents. Il définit une stratégie de développement, un découpage du travail, un ordre d'implémentation justifié, une stratégie de tests, une analyse des risques et une checklist de préparation, afin que le passage à l'implémentation (Livrable 8) puisse débuter sur des bases claires et validées.

Ce document reste un document de **planification** : il n'introduit aucun code, aucune structure de projet, ni aucun détail d'implémentation technique. Il organise dans le temps ce qui a déjà été spécifié et conçu.

### 1.2 Lien avec les livrables précédents

- Le **cahier des charges** fournit les fonctionnalités, les cas d'utilisation et les critères de réussite qui structurent le découpage en tâches.
- Les **spécifications techniques** et l'**architecture logicielle** définissent les modules dont la construction est planifiée dans ce document.
- La **conception UML** fournit les comportements attendus (séquences) qui guident la définition des tâches d'intégration.
- La **conception de la base de données** et la **conception de l'API REST** fournissent la structure de données et les ressources dont la réalisation est planifiée respectivement dans les phases « Base de données » et « API REST ».

Aucun document précédent n'est modifié par ce livrable.

---

## 2. Stratégie de développement

| Élément de stratégie | Description | Justification |
|---|---|---|
| **Développement incrémental** | Le système est construit module par module, en commençant par les fondations (données, backend) avant les couches applicatives (détection, API, interface). | Permet de disposer à chaque étape d'un sous-ensemble fonctionnel vérifiable, plutôt que d'un système complet mais non testé avant la fin du projet ; cohérent avec le cadre d'un stage d'observation où la visibilité régulière sur l'avancement est importante. |
| **Validation progressive** | Chaque phase du plan (section 3) fait l'objet de critères de validation explicites (section 8) avant d'entamer la phase suivante lorsque celle-ci en dépend. | Réduit le risque de propager une erreur de conception ou d'implémentation d'un module vers les modules qui en dépendent. |
| **Intégration continue des modules** | Les modules développés séparément (Capture réseau, Détection, API, Interface Web) sont régulièrement assemblés et vérifiés ensemble plutôt qu'une seule fois en fin de projet. | Cohérent avec l'architecture modulaire déjà validée (Livrable 4), qui repose sur des échanges de données précis entre modules ; une intégration tardive rendrait plus difficile l'identification de l'origine d'un dysfonctionnement. |
| **Priorité aux fonctionnalités essentielles** | Les fonctionnalités critiques pour la démonstration du système (capture, détection des neuf menaces, génération d'alertes, authentification) sont développées avant les fonctionnalités de confort (statistiques avancées, gestion fine de la configuration). | Garantit qu'un système minimal mais fonctionnel existe le plus tôt possible, ce qui est essentiel dans un cadre de stage à durée limitée. |

---

## 3. Découpage en phases

### 3.1 Initialisation du projet

- **Objectif** : mettre en place les fondations techniques nécessaires avant tout développement fonctionnel.
- **Livrables attendus** : dépôt de code source organisé, environnement de développement conteneurisé conforme aux choix technologiques validés (Livrable 2), conventions de travail définies.
- **Dépendances** : aucune (phase de démarrage).

### 3.2 Base de données

- **Objectif** : mettre en œuvre la structure de données définie dans la conception de la base de données (Livrable 5).
- **Livrables attendus** : structure de données opérationnelle pour les huit entités (Utilisateur, Rôle, Alerte, Log, Règle, Statistique, Configuration, Liste noire), contraintes d'intégrité appliquées, données de référence initiales.
- **Dépendances** : Initialisation du projet.

### 3.3 Backend

- **Objectif** : mettre en place la structure applicative backend qui hébergera l'ensemble des modules métier et leur accès à la base de données.
- **Livrables attendus** : structure applicative backend opérationnelle, couche d'accès aux données fonctionnelle, gestion centralisée des erreurs internes.
- **Dépendances** : Base de données.

### 3.4 Capture réseau

- **Objectif** : implémenter l'observation du trafic réseau et sa transformation en indicateurs exploitables (module Capture réseau et module Analyse, tous deux couverts par cette phase).
- **Livrables attendus** : capture opérationnelle sur l'interface surveillée, extraction des informations pertinentes, production d'indicateurs d'analyse.
- **Dépendances** : Backend.

### 3.5 Moteur de détection

- **Objectif** : implémenter l'évaluation des indicateurs au regard des règles de détection, pour l'ensemble des neuf menaces définies dans le cahier des charges, ainsi que la Gestion des alertes et la Journalisation qui en découlent.
- **Livrables attendus** : moteur de détection opérationnel, couverture des neuf menaces, module de Gestion des alertes fonctionnel, module de Journalisation fonctionnel.
- **Dépendances** : Capture réseau, Base de données.

### 3.6 Authentification

- **Objectif** : implémenter la vérification des identifiants, la gestion des sessions et le contrôle d'accès basé sur les rôles.
- **Livrables attendus** : mécanisme d'authentification opérationnel, contrôle d'autorisation fonctionnel selon les trois profils utilisateurs.
- **Dépendances** : Base de données.

### 3.7 API REST

- **Objectif** : exposer les ressources définies dans la conception de l'API REST (Livrable 6), protégées par l'authentification et l'autorisation.
- **Livrables attendus** : ensemble des ressources (Authentification, Utilisateurs, Alertes, Logs, Règles, Statistiques, Configuration, Liste noire) opérationnelles.
- **Dépendances** : Backend, Authentification, Moteur de détection.

### 3.8 Interface Web

- **Objectif** : développer le tableau de bord permettant aux utilisateurs de consulter et de gérer le système selon leur profil.
- **Livrables attendus** : interface web opérationnelle couvrant l'ensemble des cas d'utilisation du cahier des charges, avec adaptation de l'affichage selon le profil connecté.
- **Dépendances** : API REST.

### 3.9 Intégration

- **Objectif** : assembler l'ensemble des modules développés séparément et vérifier leur fonctionnement conjoint de bout en bout.
- **Livrables attendus** : système intégré fonctionnant depuis la capture d'un paquet jusqu'à l'affichage d'une alerte dans l'interface web.
- **Dépendances** : toutes les phases précédentes.

### 3.10 Tests

- **Objectif** : valider la qualité et la fiabilité du système selon les différents niveaux de test décrits en section 6.
- **Livrables attendus** : suites de tests exécutées, rapport de résultats, anomalies identifiées et corrigées.
- **Dépendances** : Intégration.

### 3.11 Documentation

- **Objectif** : consolider la documentation technique et utilisateur nécessaire à l'exploitation et à la maintenance du système.
- **Livrables attendus** : guide d'utilisation par profil, documentation technique de déploiement, traçabilité entre les livrables et le système réalisé.
- **Dépendances** : Tests (peut débuter en parallèle dès que les modules concernés sont stabilisés).

### 3.12 Préparation de la démonstration

- **Objectif** : préparer une démonstration représentative du fonctionnement du système pour le CCM.
- **Livrables attendus** : scénario de démonstration, environnement de démonstration stable, support de présentation.
- **Dépendances** : Documentation, Tests.

---

## 4. Découpage en tâches

### 4.1 Initialisation du projet

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| INIT-1 | Mettre en place le dépôt de code source et les conventions de gestion de version. | Critique | — | Faible |
| INIT-2 | Préparer l'environnement de développement conteneurisé conforme aux choix technologiques validés. | Critique | INIT-1 | Moyenne |
| INIT-3 | Définir les conventions de nommage et d'organisation cohérentes avec les modules de l'architecture logicielle. | Haute | INIT-1 | Faible |
| INIT-4 | Mettre en place un environnement d'intégration continue de base. | Moyenne | INIT-2 | Moyenne |

### 4.2 Base de données

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| DB-1 | Mettre en place l'instance PostgreSQL dans l'environnement conteneurisé. | Critique | INIT-2 | Faible |
| DB-2 | Mettre en œuvre les entités Utilisateur et Rôle. | Critique | DB-1 | Moyenne |
| DB-3 | Mettre en œuvre les entités Règle et Liste noire. | Critique | DB-1 | Moyenne |
| DB-4 | Mettre en œuvre les entités Alerte et Log. | Critique | DB-3 | Moyenne |
| DB-5 | Mettre en œuvre les entités Statistique et Configuration. | Haute | DB-1 | Moyenne |
| DB-6 | Mettre en œuvre les règles d'intégrité (unicité, références, règles de suppression) définies dans le Livrable 5. | Critique | DB-2, DB-3, DB-4, DB-5 | Élevée |
| DB-7 | Initialiser les données de référence (rôles reconnus, paramètres de configuration par défaut). | Haute | DB-6 | Faible |

### 4.3 Backend

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| BE-1 | Mettre en place la structure applicative backend et sa connexion à la base de données. | Critique | DB-6 | Moyenne |
| BE-2 | Implémenter la couche d'accès aux données pour chaque entité. | Critique | BE-1 | Élevée |
| BE-3 | Mettre en place la gestion centralisée des erreurs internes, conformément à la stratégie de l'architecture logicielle. | Haute | BE-1 | Moyenne |

### 4.4 Capture réseau

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| CAP-1 | Mettre en place l'écoute du trafic sur l'interface réseau surveillée. | Critique | BE-1 | Élevée |
| CAP-2 | Implémenter l'extraction des informations pertinentes de chaque paquet observé. | Critique | CAP-1 | Moyenne |
| CAP-3 | Implémenter le signalement des erreurs de capture vers la Journalisation. | Haute | CAP-1 | Moyenne |
| CAP-4 | Implémenter le module d'Analyse (agrégation des informations en indicateurs). | Critique | CAP-2 | Élevée |

### 4.5 Moteur de détection

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| DET-1 | Implémenter le mécanisme générique d'évaluation d'une règle sur un indicateur. | Critique | CAP-4, DB-3 | Élevée |
| DET-2 | Implémenter les règles couvrant les menaces volumétriques (Port Scan, SYN Flood, ICMP Flood). | Critique | DET-1 | Élevée |
| DET-3 | Implémenter les règles couvrant les menaces liées aux connexions (Brute Force, tentatives répétées de connexion). | Critique | DET-1 | Moyenne |
| DET-4 | Implémenter les règles couvrant la liste noire et les ports interdits. | Critique | DET-1, DB-3 | Moyenne |
| DET-5 | Implémenter les règles couvrant l'activité inhabituelle et le trafic anormal simple. | Haute | DET-1 | Élevée |
| DET-6 | Implémenter la transmission des détections positives vers la Gestion des alertes. | Critique | DET-2, DET-3, DET-4, DET-5 | Moyenne |
| DET-7 | Implémenter le module de Gestion des alertes (création, cycle de vie, persistance). | Critique | DET-6, DB-4 | Élevée |
| DET-8 | Implémenter le module de Journalisation des événements et des alertes. | Critique | DET-7 | Moyenne |

### 4.6 Authentification

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| AUTH-1 | Implémenter la vérification des identifiants et la protection des mots de passe. | Critique | DB-2 | Moyenne |
| AUTH-2 | Implémenter l'émission et la vérification de la preuve de session. | Critique | AUTH-1 | Moyenne |
| AUTH-3 | Implémenter le contrôle d'autorisation basé sur le rôle de l'utilisateur. | Critique | AUTH-2 | Moyenne |
| AUTH-4 | Implémenter la limitation des tentatives d'authentification échouées. | Haute | AUTH-1 | Moyenne |

### 4.7 API REST

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| API-1 | Implémenter la ressource Authentification. | Critique | AUTH-3 | Moyenne |
| API-2 | Implémenter la ressource Utilisateurs. | Critique | API-1, DB-2 | Moyenne |
| API-3 | Implémenter la ressource Alertes. | Critique | API-1, DET-7 | Moyenne |
| API-4 | Implémenter la ressource Logs. | Haute | API-1, DET-8 | Faible |
| API-5 | Implémenter la ressource Règles. | Critique | API-1, DET-1 | Moyenne |
| API-6 | Implémenter la ressource Statistiques. | Haute | API-1, DB-5 | Moyenne |
| API-7 | Implémenter la ressource Configuration. | Moyenne | API-1, DB-5 | Faible |
| API-8 | Implémenter la ressource Liste noire. | Haute | API-1, DB-3 | Faible |
| API-9 | Implémenter la gestion homogène des erreurs et des codes de réponse sur l'ensemble des ressources. | Critique | API-2, API-3, API-4, API-5, API-6, API-7, API-8 | Moyenne |

### 4.8 Interface Web

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| WEB-1 | Mettre en place la structure applicative frontend. | Critique | INIT-2 | Faible |
| WEB-2 | Implémenter l'écran d'authentification et la gestion de session côté interface. | Critique | API-1 | Moyenne |
| WEB-3 | Implémenter le tableau de bord de consultation des alertes. | Critique | API-3 | Moyenne |
| WEB-4 | Implémenter la consultation des journaux. | Haute | API-4 | Faible |
| WEB-5 | Implémenter la gestion des règles de détection. | Critique | API-5 | Moyenne |
| WEB-6 | Implémenter le tableau de bord statistique. | Haute | API-6 | Moyenne |
| WEB-7 | Implémenter la gestion des utilisateurs. | Haute | API-2 | Faible |
| WEB-8 | Implémenter la gestion de la configuration et de la liste noire. | Moyenne | API-7, API-8 | Faible |
| WEB-9 | Adapter l'affichage et les actions disponibles selon le profil connecté. | Critique | WEB-2, WEB-3, WEB-4, WEB-5, WEB-6, WEB-7, WEB-8 | Moyenne |

### 4.9 Intégration

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| INT-1 | Intégrer la chaîne complète Capture → Analyse → Détection → Alertes → Journalisation. | Critique | DET-8, CAP-4 | Élevée |
| INT-2 | Intégrer l'API Backend avec l'ensemble des modules internes. | Critique | API-9 | Moyenne |
| INT-3 | Intégrer l'Interface Web avec l'API Backend dans l'environnement conteneurisé complet. | Critique | WEB-9, INT-2 | Moyenne |
| INT-4 | Vérifier le fonctionnement de bout en bout pour chacune des neuf menaces. | Critique | INT-1, INT-3 | Élevée |

### 4.10 Tests

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| TEST-1 | Réaliser les tests unitaires des modules Détection, Gestion des alertes et Authentification. | Critique | INT-1 | Moyenne |
| TEST-2 | Réaliser les tests d'intégration entre les modules internes et l'API Backend. | Critique | INT-2 | Moyenne |
| TEST-3 | Réaliser les tests fonctionnels couvrant l'ensemble des cas d'utilisation du cahier des charges. | Critique | INT-3 | Élevée |
| TEST-4 | Réaliser les tests de validation confirmant la détection effective des neuf menaces. | Critique | INT-4 | Élevée |
| TEST-5 | Corriger les anomalies identifiées lors des tests précédents. | Critique | TEST-1, TEST-2, TEST-3, TEST-4 | Moyenne |

### 4.11 Documentation

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| DOC-1 | Rédiger un guide d'utilisation par profil (Administrateur, Analyste sécurité, Lecture seule). | Haute | TEST-3 | Faible |
| DOC-2 | Rédiger une documentation technique de déploiement et d'exploitation. | Haute | TEST-2 | Moyenne |
| DOC-3 | Consolider la traçabilité entre les sept livrables et le système effectivement réalisé. | Moyenne | TEST-5 | Faible |

### 4.12 Préparation de la démonstration

| ID | Description | Priorité | Dépendances | Complexité |
|---|---|---|---|---|
| DEMO-1 | Définir un scénario de démonstration couvrant plusieurs menaces représentatives. | Haute | TEST-4 | Faible |
| DEMO-2 | Préparer un jeu de données ou un trafic de démonstration reproductible. | Haute | DEMO-1 | Moyenne |
| DEMO-3 | Vérifier la stabilité de l'environnement de démonstration complet. | Critique | INT-3, DEMO-2 | Moyenne |
| DEMO-4 | Préparer le support de présentation synthétisant la démarche et les résultats. | Moyenne | DOC-3 | Faible |

---

## 5. Ordre d'implémentation recommandé

L'ordre recommandé suit la chaîne de dépendances déjà établie dans l'architecture logicielle (section 3.10 du Livrable 4) et dans le découpage en phases ci-dessus :

1. **Initialisation du projet** — fondation indispensable à toute activité de développement.
2. **Base de données** — les modules applicatifs dépendent tous, directement ou indirectement, de la persistance des données.
3. **Backend** — nécessaire pour exposer la base de données aux modules métier.
4. **Authentification** et **Capture réseau** peuvent être menées **en parallèle** à partir de cette étape, car elles ne dépendent l'une de l'autre pour aucune donnée ni aucun comportement : l'Authentification ne dépend que des entités Utilisateur et Rôle, tandis que la Capture réseau ne dépend que du Backend. Ce parallélisme permet d'optimiser le temps disponible dans le cadre d'un stage à durée limitée.
5. **Moteur de détection** — ne peut être développé qu'une fois la Capture réseau (source des indicateurs) et la Base de données (règles) disponibles.
6. **API REST** — nécessite que l'Authentification, le Moteur de détection (pour les ressources Alertes et Règles) et le Backend soient opérationnels, puisqu'elle expose leurs données et fonctionnalités.
7. **Interface Web** — ne peut être développée de façon pertinente qu'une fois l'API REST disponible, celle-ci constituant son unique point d'accès.
8. **Intégration** — regroupe l'ensemble des modules développés séparément ; elle ne peut logiquement intervenir qu'après leur développement individuel.
9. **Tests** — s'appuient sur un système intégré pour être pleinement représentatifs, notamment pour les tests fonctionnels et de validation.
10. **Documentation** — peut débuter dès la stabilisation des premiers modules (par exemple la documentation technique du Backend), mais sa consolidation finale dépend des résultats des tests.
11. **Préparation de la démonstration** — dernière étape, qui suppose un système testé et documenté.

Cet ordre privilégie une construction **de bas en haut** (données → logique métier → exposition → interface), cohérente avec le principe de développement incrémental retenu en section 2, et limite le risque de devoir remettre en cause un module déjà achevé du fait d'une dépendance non anticipée.

---

## 6. Stratégie de tests

| Niveau de test | Objectif |
|---|---|
| **Tests unitaires** | Vérifier isolément le comportement d'un module ou d'une fonction précise (par exemple l'évaluation d'une règle de détection unique), indépendamment des autres modules, afin de détecter les erreurs de logique au plus tôt et avec un retour rapide. |
| **Tests d'intégration** | Vérifier que les échanges de données entre deux ou plusieurs modules respectent les flux définis dans l'architecture logicielle (par exemple, que la Détection reçoit correctement les indicateurs produits par l'Analyse, ou que l'API Backend interagit correctement avec la Base de données). |
| **Tests fonctionnels** | Vérifier que chaque cas d'utilisation défini dans le cahier des charges (UC1 à UC8) est correctement réalisé du point de vue de l'utilisateur, indépendamment de l'implémentation interne des modules sollicités. |
| **Tests de validation** | Vérifier, sur le système complet, que les critères de réussite définis en section 12 du cahier des charges sont atteints, en particulier la détection effective de chacune des neuf menaces identifiées ; ce niveau conditionne la préparation de la démonstration. |

Aucun cas de test précis n'est détaillé dans ce document ; cette stratégie définit uniquement les objectifs propres à chaque niveau, la définition des cas de test relevant de la phase de Tests elle-même.

---

## 7. Gestion des risques

### 7.1 Tableau de synthèse

| Risque | Catégorie | Impact | Probabilité | Mesure de mitigation |
|---|---|---|---|---|
| Difficulté d'accès bas niveau à l'interface réseau (droits, compatibilité de la capture) | Technique | Élevé | Moyenne | Prioriser et tester la Capture réseau tôt dans le plan (phase 3.4) ; s'appuyer sur l'environnement conteneurisé maîtrisé défini en Initialisation. |
| Faux positifs ou faux négatifs dans les règles de détection | Technique | Élevé | Élevée | Prévoir des tests de validation dédiés (TEST-4) et un calibrage progressif des seuils, conformément aux hypothèses déjà posées dans les spécifications techniques. |
| Couplage imprévu entre modules fragilisant la modularité | Technique | Moyen | Faible | Respecter strictement la séparation des responsabilités définie dans l'architecture logicielle validée (Livrable 4). |
| Durée limitée propre à un stage d'observation | Organisationnel | Élevé | Élevée | Prioriser strictement les fonctionnalités essentielles (section 2) ; suivre l'ordre d'implémentation recommandé (section 5). |
| Disponibilité limitée des interlocuteurs du CCM pour valider les points encore ouverts | Organisationnel | Moyen | Moyenne | Consolider l'ensemble des décisions à valider en un point unique avant le Livrable 8 (voir section 10.3). |
| Interruption ou indisponibilité imprévue du porteur du projet | Organisationnel | Élevé | Faible | Maintenir une documentation à jour tout au long du projet plutôt qu'en fin de parcours (phase Documentation menée en continu). |
| Volumétrie de trafic réel supérieure aux hypothèses retenues | Données | Moyen | Moyenne | S'appuyer sur les hypothèses de fonctionnement déjà validées (Livrable 2, section 9) et prévoir une vérification de charge simple lors de la phase Tests. |
| Données de test non représentatives de l'activité réelle du CCM | Données | Moyen | Élevée | Préparer un jeu de données de démonstration réaliste (DEMO-2) ; solliciter un échantillon représentatif auprès du CCM si possible. |
| Accès restreint ou indisponible à un segment réseau réel à surveiller | Réseau | Élevé | Moyenne | Valider dès l'Initialisation les droits d'accès nécessaires ; prévoir un environnement de test réseau isolé si l'accès au réseau réel n'est pas possible. |
| Absence de trafic malveillant réel pour valider la détection | Réseau | Moyen | Élevée | Générer, dans un environnement contrôlé, un trafic simulant les neuf menaces définies dans le cahier des charges (cohérent avec DEMO-2 et TEST-4). |

---

## 8. Critères de validation

| Phase | Critère de validation permettant de la considérer comme terminée |
|---|---|
| Initialisation du projet | L'environnement de développement est opérationnel et reproductible ; les conventions de travail sont formalisées. |
| Base de données | Les huit entités sont opérationnelles, les contraintes d'intégrité définies dans le Livrable 5 sont vérifiées, les données de référence sont disponibles. |
| Backend | La structure applicative backend permet un accès fiable à l'ensemble des entités persistées. |
| Capture réseau | Le trafic est capturé et transformé en indicateurs exploitables de façon continue et sans interruption majeure. |
| Moteur de détection | Chacune des neuf menaces définies dans le cahier des charges est détectée par au moins une règle fonctionnelle, et les alertes correspondantes sont correctement générées et journalisées. |
| Authentification | Les trois profils utilisateurs peuvent s'authentifier et se voient appliquer les autorisations correspondant à la matrice de permissions du cahier des charges. |
| API REST | L'ensemble des ressources du catalogue d'endpoints (Livrable 6) est opérationnel et correctement protégé. |
| Interface Web | L'ensemble des cas d'utilisation du cahier des charges est réalisable depuis l'interface, avec un affichage conforme au profil connecté. |
| Intégration | Le système fonctionne de bout en bout, de la capture d'un paquet jusqu'à l'affichage d'une alerte, sans intervention manuelle sur les modules internes. |
| Tests | L'ensemble des niveaux de test (unitaires, intégration, fonctionnels, validation) a été exécuté, et les anomalies critiques identifiées ont été corrigées. |
| Documentation | La documentation utilisateur et technique est disponible et cohérente avec le système effectivement réalisé. |
| Préparation de la démonstration | Un scénario de démonstration reproductible fonctionne de façon stable dans l'environnement prévu à cet effet. |

---

## 9. Checklist avant implémentation

Avant d'écrire la première ligne de code (Livrable 8), les éléments suivants doivent être vérifiés :

- [ ] Les six livrables précédents (cahier des charges, spécifications techniques, conception UML, architecture logicielle, conception de la base de données, conception de l'API REST) sont formellement validés.
- [ ] Les questions ouvertes consolidées en section 10.3 de ce document ont été soumises au CCM et ont reçu une réponse, ou une hypothèse de travail explicite a été retenue à défaut de réponse.
- [ ] Les droits d'accès nécessaires à la Capture réseau (accès à l'interface réseau surveillée) sont confirmés, ou un environnement de test réseau isolé est mis à disposition.
- [ ] L'environnement de développement conteneurisé (Docker, Linux) est opérationnel et accessible à toute personne impliquée dans le projet.
- [ ] Le dépôt de code source et les conventions de gestion de version sont en place.
- [ ] L'instance PostgreSQL cible est accessible depuis l'environnement de développement.
- [ ] Les profils utilisateurs de test (Administrateur, Analyste sécurité, Lecture seule) sont définis pour les besoins de validation.
- [ ] Un jeu de données ou de trafic de test représentatif des neuf menaces à détecter est préparé ou planifié.
- [ ] Les priorités de développement (fonctionnalités essentielles contre fonctionnalités de confort) sont partagées et acceptées par l'ensemble des parties prenantes du projet.
- [ ] Le calendrier global du stage est confronté à l'ordre d'implémentation recommandé (section 5), afin de vérifier sa faisabilité dans le temps imparti.

---

## 10. Vérification de cohérence

### 10.1 Cohérence avec les livrables précédents

| Livrable | Vérification |
|---|---|
| Cahier des charges | Les phases et tâches couvrent l'ensemble des fonctionnalités F1 à F10, des cas d'utilisation UC1 à UC8 et des neuf menaces à détecter. |
| Spécifications techniques | L'ordre d'implémentation respecte les dépendances entre les neuf composants logiques déjà décrits (section 3 du Livrable 2). |
| Conception UML | Les tâches d'intégration (INT-1 à INT-4) correspondent directement aux diagrammes de séquence définis dans le Livrable 3. |
| Architecture logicielle | Le découpage en modules (Capture, Analyse, Détection, Alertes, Journalisation, Authentification, API, Interface Web, Configuration) est repris à l'identique dans les phases et les tâches. |
| Conception de la base de données | La phase « Base de données » couvre l'ensemble des huit entités et des règles d'intégrité définies dans le Livrable 5. |
| Conception de l'API REST | La phase « API REST » couvre l'ensemble des huit ressources et leur catalogue d'endpoints défini dans le Livrable 6. |

### 10.2 Points de vigilance identifiés

- Le module **Configuration**, introduit dans l'architecture logicielle (Livrable 4) et repris dans la base de données (Livrable 5) et l'API REST (Livrable 6), est intégré dans ce plan à travers les tâches DB-5, API-7 et WEB-8 ; sa priorité a été fixée à un niveau modéré (Moyenne), cohérent avec son caractère non bloquant pour la détection des menaces.
- La tâche DET-1 (mécanisme générique d'évaluation d'une règle) constitue un point de passage critique du plan : tout retard sur cette tâche affecte directement l'ensemble des tâches DET-2 à DET-8 ainsi que la ressource API Règles ; une attention particulière doit lui être portée.

### 10.3 Décisions à prendre avant de démarrer le Livrable 8 (Implémentation)

Ce plan consolide les questions déjà signalées comme ouvertes dans les livrables précédents et qui doivent être tranchées avant le démarrage de l'implémentation :

1. **Périmètre réseau exact et point de capture** (cahier des charges, questions 1 et 2) : quel segment réseau du CCM sera effectivement surveillé, et par quel moyen technique le trafic sera-t-il rendu accessible à la Capture réseau.
2. **Environnement d'hébergement définitif** (cahier des charges, question 4 ; architecture logicielle, section 6.2) : machine unique ou séparation entre le nœud applicatif et la Base de données.
3. **Politique de conservation des données** (cahier des charges, question 6 ; conception de la base de données, section 7) : durées de rétention des alertes, journaux, statistiques et configurations.
4. **Source et modalités de gestion de la liste noire** (cahier des charges, question 7) : origine du renseignement sur les menaces alimentant cette liste.
5. **Politique de ports autorisés/interdits** (cahier des charges, question 8) : liste de référence à utiliser pour la règle correspondante.
6. **Statut de persistance des statistiques** (spécifications techniques, question 4 ; conception UML, section 8.3 ; conception de la base de données, section 10.5) : calcul à la demande ou stockage persistant.
7. **Granularité de la classe/entité Règle par type de menace** (conception UML, section 8.3) : paramétrage générique ou distinction structurelle par type de menace.
8. **Accès du profil Lecture seule aux journaux** (conception de l'API REST, section 10.4) : incohérence relevée entre le cahier des charges (accès « Limité ») et la conception UML (aucun accès), à trancher explicitement.
9. **Permissions précises sur les ressources Configuration et Liste noire** (conception de l'API REST, section 10.4) : confirmation des profils habilités à les gérer.
10. **Seuils de protection contre les abus d'authentification** (conception de l'API REST, section 8) : nombre de tentatives et durée de restriction en cas d'échecs répétés.

Il est recommandé de regrouper ces dix points en une seule session de validation avec les interlocuteurs du CCM avant le démarrage du Livrable 8, conformément à la mesure de mitigation du risque organisationnel identifié en section 7.

---

*Fin du document — Livrable 7.*
