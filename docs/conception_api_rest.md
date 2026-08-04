# Conception de l'API REST — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 6 — Conception de l'API REST
**Documents de référence :** `docs/cahier_des_charges.md` (Livrable 1), `docs/specifications_techniques.md` (Livrable 2), `docs/conception_uml.md` (Livrable 3), `docs/architecture_logicielle.md` (Livrable 4), `docs/conception_base_de_donnees.md` (Livrable 5)
**Statut :** Conception d'API — aucune implémentation, aucune spécification OpenAPI/Swagger

---

## 1. Objectif du document

### 1.1 Rôle de l'API REST

Ce document définit la conception de l'API REST du système, qui constitue le point d'échange structuré unique entre l'Interface Web et l'ensemble des modules internes, conformément au module « API Backend » déjà décrit en section 4.7 de l'architecture logicielle. Il décrit les ressources exposées, les opérations disponibles sur chacune d'elles, les règles d'autorisation associées, ainsi que les principes généraux de sécurité et de gestion des erreurs.

Ce document reste à un niveau de **conception** : il ne constitue ni une spécification technique au format OpenAPI/Swagger, ni une implémentation FastAPI. Aucun exemple de requête ou de réponse au format JSON n'est fourni ; seules les descriptions fonctionnelles des échanges sont présentées.

### 1.2 Lien avec les autres livrables

- Le **cahier des charges** a défini les fonctionnalités (F1 à F10), les profils utilisateurs et leurs permissions, ainsi que les cas d'utilisation que l'API doit permettre de réaliser.
- Les **spécifications techniques** ont positionné l'API Backend comme unique point d'accès de l'Interface Web aux données et fonctionnalités du système.
- La **conception UML** a modélisé les cas d'utilisation et les diagrammes de séquence « Consultation des alertes » et « Authentification d'un utilisateur », que ce document traduit en ressources et en opérations concrètes.
- L'**architecture logicielle** a précisé les dépendances de l'API Backend envers l'Authentification, la Base de données, la Gestion des alertes, la Journalisation et la Configuration.
- La **conception de la base de données** a défini les entités Utilisateur, Rôle, Alerte, Log, Règle, Statistique, Configuration et Liste noire, dont ce document reprend la structure pour définir les ressources exposées par l'API.

Aucun document précédent n'est modifié par ce livrable.

---

## 2. Principes de conception

| Principe | Application |
|---|---|
| **Architecture REST** | Chaque ressource du système (utilisateurs, alertes, logs, règles, statistiques, configuration, liste noire) est identifiée par une URI dédiée ; les opérations sur ces ressources s'appuient sur les méthodes HTTP standards (consultation, création, modification). |
| **Séparation frontend / backend** | L'Interface Web ne communique qu'avec l'API Backend, qui centralise l'accès à l'ensemble des modules internes, conformément au principe déjà établi en section 7 des spécifications techniques et en section 5 de la conception UML. |
| **Format JSON** | L'ensemble des échanges entre l'Interface Web et l'API Backend s'effectue selon une représentation structurée et normalisée des données, sans qu'un format d'exemple ne soit détaillé dans ce document. |
| **Stateless (absence d'état conservé côté serveur entre les requêtes)** | Chaque requête adressée à l'API doit contenir les informations nécessaires à son traitement (notamment la preuve d'authentification) ; l'API ne conserve pas d'état de conversation propre à un utilisateur entre deux requêtes successives. |
| **Cohérence des ressources** | Chaque ressource exposée correspond directement à une entité ou à un regroupement logique déjà défini dans la conception de la base de données ; le nommage des ressources reste cohérent et prévisible d'une ressource à l'autre. |
| **Versionnement de l'API** | L'API est conçue pour être identifiée par une version explicite, afin de permettre l'introduction future de nouvelles fonctionnalités ou de nouvelles ressources sans remettre en cause les usages existants (voir section 9). |

---

## 3. Ressources de l'API

| Ressource | Rôle |
|---|---|
| **Authentification** | Permet à un utilisateur de s'identifier, d'obtenir une session active, et de la clôturer ; constitue le point d'entrée obligatoire avant tout accès aux autres ressources. |
| **Utilisateurs** | Permet la gestion des comptes utilisateurs et de leur rôle associé, conformément au cas d'utilisation UC6 du cahier des charges. |
| **Alertes** | Permet la consultation des alertes générées par le système et la mise à jour de leur statut de traitement, conformément aux cas d'utilisation UC2 et UC8. |
| **Logs** | Permet la consultation de l'historique des événements réseau enregistrés, conformément au cas d'utilisation UC4. |
| **Règles** | Permet la consultation et la gestion des règles de détection, conformément au cas d'utilisation UC3. |
| **Statistiques** | Permet la consultation d'une synthèse agrégée de l'activité réseau et des alertes, conformément au cas d'utilisation UC5. |
| **Configuration** | Permet la consultation et la modification des paramètres généraux du système, correspondant au module Configuration de l'architecture logicielle. |
| **Liste noire** | Permet la consultation et la gestion des adresses IP considérées comme malveillantes, utilisées par la règle de détection correspondante. |

---

## 4. Catalogue des endpoints

### 4.1 Authentification

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| POST | `/v1/auth/login` | Authentifie un utilisateur à partir de ses identifiants et ouvre une session. | Aucun profil requis (accès préalable à toute authentification) | Nom d'utilisateur, mot de passe | Confirmation d'authentification avec informations de session, ou refus explicite |
| POST | `/v1/auth/logout` | Clôture la session active de l'utilisateur authentifié. | Tout utilisateur authentifié | Session active | Confirmation de clôture de session |
| GET | `/v1/auth/session` | Retourne les informations du profil actuellement connecté. | Tout utilisateur authentifié | Session active | Informations du profil connecté (rôle, statut) |

### 4.2 Utilisateurs

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/utilisateurs` | Liste les comptes utilisateurs existants. | Administrateur | Filtres optionnels (rôle, statut du compte) | Liste des comptes utilisateurs |
| GET | `/v1/utilisateurs/{id}` | Consulte le détail d'un compte utilisateur. | Administrateur | Identifiant de l'utilisateur | Détail du compte concerné |
| POST | `/v1/utilisateurs` | Crée un nouveau compte utilisateur. | Administrateur | Nom d'utilisateur, mot de passe, rôle associé | Confirmation de création du compte |
| PUT | `/v1/utilisateurs/{id}` | Modifie les informations d'un compte utilisateur (rôle notamment). | Administrateur | Identifiant, champs à modifier | Confirmation de mise à jour |
| PATCH | `/v1/utilisateurs/{id}/statut` | Active ou désactive un compte utilisateur. | Administrateur | Identifiant, nouveau statut | Confirmation du changement de statut |

### 4.3 Alertes

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/alertes` | Liste les alertes générées, avec possibilité de filtrage. | Administrateur, Analyste sécurité, Lecture seule | Filtres optionnels (période, type de menace, gravité, statut) | Liste des alertes correspondant aux critères |
| GET | `/v1/alertes/{id}` | Consulte le détail d'une alerte. | Administrateur, Analyste sécurité, Lecture seule | Identifiant de l'alerte | Détail complet de l'alerte |
| PATCH | `/v1/alertes/{id}/statut` | Met à jour le statut de traitement d'une alerte (qualification). | Administrateur, Analyste sécurité | Identifiant, nouveau statut | Confirmation de la mise à jour du statut |

### 4.4 Logs

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/logs` | Consulte l'historique des événements réseau enregistrés, avec filtrage. | Administrateur, Analyste sécurité | Filtres optionnels (période, adresse IP, type d'événement) | Liste des événements correspondant aux critères |
| GET | `/v1/logs/{id}` | Consulte le détail d'un événement journalisé. | Administrateur, Analyste sécurité | Identifiant de l'entrée de journal | Détail complet de l'événement |

### 4.5 Règles

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/regles` | Liste les règles de détection existantes. | Administrateur, Analyste sécurité | Filtres optionnels (statut, type de menace) | Liste des règles |
| GET | `/v1/regles/{id}` | Consulte le détail d'une règle. | Administrateur, Analyste sécurité | Identifiant de la règle | Détail complet de la règle |
| POST | `/v1/regles` | Crée une nouvelle règle de détection. | Administrateur, Analyste sécurité | Nom, type de menace, condition de déclenchement, gravité | Confirmation de création de la règle |
| PUT | `/v1/regles/{id}` | Modifie une règle existante. | Administrateur, Analyste sécurité | Identifiant, champs à modifier | Confirmation de mise à jour |
| PATCH | `/v1/regles/{id}/statut` | Active ou désactive une règle. | Administrateur, Analyste sécurité | Identifiant, nouveau statut | Confirmation du changement de statut |

### 4.6 Statistiques

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/statistiques` | Retourne une synthèse agrégée de l'activité réseau et des alertes sur une période donnée. | Administrateur, Analyste sécurité, Lecture seule | Période considérée (date de début, date de fin) | Synthèse statistique correspondant à la période demandée |

### 4.7 Configuration

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/configuration` | Liste l'ensemble des paramètres généraux du système. | Administrateur | Aucun, ou filtre par nom de paramètre | Liste des paramètres et de leurs valeurs actuelles |
| GET | `/v1/configuration/{nom}` | Consulte la valeur d'un paramètre précis. | Administrateur | Nom du paramètre | Valeur actuelle du paramètre |
| PUT | `/v1/configuration/{nom}` | Modifie la valeur d'un paramètre général. | Administrateur | Nom du paramètre, nouvelle valeur | Confirmation de mise à jour |

### 4.8 Liste noire

| Méthode | URI | Description | Profils autorisés | Paramètres principaux | Réponse attendue |
|---|---|---|---|---|---|
| GET | `/v1/liste-noire` | Liste les adresses IP considérées comme malveillantes. | Administrateur, Analyste sécurité | Filtre optionnel (statut) | Liste des entrées de la liste noire |
| POST | `/v1/liste-noire` | Ajoute une adresse IP à la liste noire. | Administrateur, Analyste sécurité | Adresse IP, motif ou source | Confirmation de création de l'entrée |
| PUT | `/v1/liste-noire/{id}` | Modifie une entrée existante de la liste noire. | Administrateur, Analyste sécurité | Identifiant, champs à modifier | Confirmation de mise à jour |
| PATCH | `/v1/liste-noire/{id}/statut` | Active ou désactive une entrée de la liste noire. | Administrateur, Analyste sécurité | Identifiant, nouveau statut | Confirmation du changement de statut |

---

## 5. Authentification et autorisation

### 5.1 Principe d'authentification

Chaque utilisateur doit s'identifier auprès de la ressource Authentification avant de pouvoir accéder à toute autre ressource de l'API. Une fois l'identité vérifiée, une preuve de session est délivrée à l'utilisateur et doit être transmise à chaque requête ultérieure, conformément au principe « stateless » retenu en section 2 : l'API vérifie cette preuve à chaque appel plutôt que de conserver un état de connexion.

### 5.2 Gestion des rôles

Chaque utilisateur est rattaché à un rôle unique (Administrateur, Analyste sécurité, Utilisateur en lecture seule), conformément à l'entité Rôle définie dans la conception de la base de données. Ce rôle détermine l'ensemble des ressources et des opérations accessibles à l'utilisateur.

### 5.3 Contrôle d'accès

Chaque endpoint du catalogue (section 4) précise les profils autorisés à l'invoquer. Ce contrôle est appliqué de façon centralisée par l'API Backend avant tout traitement de la requête, conformément au principe déjà établi en section 4.6 de l'architecture logicielle : aucune opération n'est exécutée avant que l'autorisation du profil n'ait été vérifiée.

### 5.4 Protection des routes

Toute route de l'API, à l'exception de l'authentification elle-même, est considérée comme protégée par défaut : une requête ne présentant pas de preuve de session valide est systématiquement refusée, sans qu'aucune donnée ne soit exposée. Une requête présentant une preuve de session valide mais un profil insuffisant pour l'opération demandée est également refusée, de façon distincte d'un refus pour absence d'authentification (voir section 6).

---

## 6. Codes de réponse

| Code | Signification générale | Utilisation dans le contexte du projet |
|---|---|---|
| **200 (OK)** | La requête a été traitée avec succès. | Retourné pour toute consultation réussie (alertes, logs, règles, statistiques, configuration, liste noire). |
| **201 (Créé)** | Une nouvelle ressource a été créée avec succès. | Retourné après la création d'un utilisateur, d'une règle ou d'une entrée de liste noire. |
| **204 (Sans contenu)** | La requête a été traitée avec succès sans contenu à retourner. | Peut être retourné après une déconnexion ou une mise à jour ne nécessitant pas de restitution de données. |
| **400 (Requête invalide)** | La requête est mal formée ou incomplète. | Retourné lorsqu'un champ obligatoire est manquant ou mal formaté (par exemple une adresse IP invalide). |
| **401 (Non authentifié)** | Aucune preuve de session valide n'a été fournie. | Retourné pour toute tentative d'accès sans authentification préalable. |
| **403 (Non autorisé)** | L'utilisateur est authentifié mais son profil ne permet pas l'action demandée. | Retourné, par exemple, lorsqu'un Analyste sécurité tente de gérer un compte utilisateur. |
| **404 (Introuvable)** | La ressource demandée n'existe pas. | Retourné lorsqu'un identifiant d'alerte, de règle ou d'utilisateur ne correspond à aucun enregistrement. |
| **409 (Conflit)** | La requête entre en conflit avec l'état actuel des données. | Retourné, par exemple, lors de la création d'un utilisateur ou d'une règle avec un nom déjà utilisé. |
| **422 (Entité non traitable)** | Les données fournies sont syntaxiquement correctes mais ne respectent pas les règles fonctionnelles attendues. | Retourné, par exemple, si une période statistique est fournie avec une date de fin antérieure à la date de début. |
| **500 (Erreur interne)** | Une erreur imprévue s'est produite côté serveur. | Retourné en cas de défaillance interne d'un module, conformément à la stratégie de gestion des erreurs de l'architecture logicielle. |
| **503 (Service indisponible)** | Le service ou une de ses dépendances n'est pas disponible. | Retourné notamment en cas d'indisponibilité de la Base de données. |

---

## 7. Gestion des erreurs

### 7.1 Erreurs fonctionnelles possibles

- Identifiants de connexion invalides ou compte désactivé.
- Absence ou invalidité de la preuve de session sur une route protégée.
- Profil insuffisant pour l'action demandée.
- Référence à une ressource inexistante (utilisateur, alerte, règle, entrée de liste noire).
- Tentative de création d'une ressource avec un nom ou une valeur déjà existante (violation d'unicité).
- Tentative de suppression ou de modification interdite par les règles d'intégrité définies dans la conception de la base de données (par exemple, suppression d'un rôle encore utilisé).
- Données fournies incomplètes, mal formées, ou incohérentes sur le plan fonctionnel (par exemple une période statistique invalide).
- Indisponibilité temporaire de la Base de données ou d'un autre module interne dont dépend l'API.

### 7.2 Stratégie générale de retour d'erreur

- Toute erreur retournée par l'API doit être accompagnée d'un code de réponse HTTP cohérent avec sa nature (voir section 6) et d'une description compréhensible de la cause du refus, sans exposer d'information technique sensible (aucune trace interne, aucune information sur la structure de la base de données).
- Les erreurs liées à l'authentification et à l'autorisation doivent être distinguées explicitement (absence d'authentification contre profil insuffisant), afin de permettre à l'Interface Web d'orienter correctement l'utilisateur.
- Les erreurs liées à l'indisponibilité d'un module interne (notamment la Base de données) doivent être signalées de façon explicite à l'utilisateur, conformément à la stratégie de gestion des erreurs déjà définie en section 8 de l'architecture logicielle, plutôt que de provoquer un comportement silencieux ou incohérent de l'interface.
- Toute erreur significative doit être journalisée au niveau du module technique de Journalisation, conformément à l'architecture déjà validée.

---

## 8. Règles de sécurité

| Bonne pratique | Application |
|---|---|
| **Validation des entrées** | Toute donnée reçue par l'API (identifiants, contenu d'une règle, adresse IP à ajouter à la liste noire, période statistique) doit être vérifiée avant tout traitement, afin de garantir sa conformité avec les contraintes fonctionnelles définies dans la conception de la base de données. |
| **Principe du moindre privilège** | Chaque endpoint n'est accessible qu'aux profils strictement nécessaires à son usage, conformément à la matrice de permissions du cahier des charges ; aucune route ne doit accorder plus de droits que ceux requis par le cas d'utilisation associé. |
| **Limitation des accès** | L'accès à une ressource concernant un utilisateur donné (par exemple ses informations de session) doit être limité à cet utilisateur et aux profils habilités à le gérer. |
| **Journalisation** | Toute action sensible réalisée via l'API (authentification, création ou modification d'une règle, d'un utilisateur, d'un paramètre de configuration ou d'une entrée de liste noire) doit être tracée dans le journal d'accès, conformément à la section 7 de l'architecture logicielle. |
| **Protection contre les abus** | Les tentatives répétées d'authentification échouée doivent pouvoir être limitées, afin de réduire l'exposition de l'API à une attaque par force brute, cohérente avec la menace « Brute Force » identifiée en section 7 du cahier des charges. |

---

## 9. Évolutivité

- **Versionnement explicite** : chaque ressource est exposée sous un préfixe de version (`/v1`), ce qui permet d'introduire une future version de l'API (`/v2`) sans interrompre les usages existants.
- **Ajout de champs non contraignant** : l'ajout d'une nouvelle information optionnelle à une ressource existante (par exemple un nouvel attribut sur une alerte) ne doit pas remettre en cause les usages déjà établis d'une ressource, dans la mesure où ces informations restent facultatives.
- **Ajout de nouvelles ressources** : de nouvelles ressources (par exemple liées à la géolocalisation des adresses IP, évoquée en section 14 du cahier des charges) peuvent être introduites sans modifier les ressources existantes.
- **Dépréciation progressive** : toute évolution rendant obsolète un endpoint existant doit prévoir une période de coexistence entre l'ancien et le nouveau comportement, plutôt qu'un remplacement immédiat.

---

## 10. Vérification de cohérence

### 10.1 Cohérence avec le cahier des charges

| Élément du cahier des charges | Vérification |
|---|---|
| Fonctionnalités F1 à F10 | Toutes couvertes par au moins une ressource de l'API (ex. F9 « gérer les règles » → ressource Règles ; F10 « afficher des statistiques » → ressource Statistiques). |
| Cas d'utilisation UC1 à UC8 | Chacun trouve une correspondance directe avec un ou plusieurs endpoints (UC1 → `/v1/auth/login`, UC8 → `PATCH /v1/alertes/{id}/statut`). |
| Matrice de permissions (section 5.4) | Reprise fidèlement dans la colonne « profils autorisés » du catalogue des endpoints, à l'exception d'un point signalé en section 10.4. |

### 10.2 Cohérence avec les spécifications techniques et l'architecture logicielle

| Élément | Vérification |
|---|---|
| Point d'accès unique de l'Interface Web | Respecté : toutes les opérations de l'Interface Web transitent exclusivement par les ressources de cette API. |
| Dépendances de l'API Backend (Authentification, Base de données, Gestion des alertes, Journalisation, Configuration) | Toutes reflétées dans les ressources exposées (Authentification, Utilisateurs, Alertes, Configuration, Liste noire). |
| Stratégie de gestion des erreurs | Reprise et déclinée en codes de réponse HTTP concrets (section 6 et 7 de ce document), cohérente avec la section 8 de l'architecture logicielle. |

### 10.3 Cohérence avec la conception UML et la conception de la base de données

| Élément | Vérification |
|---|---|
| Diagrammes de séquence « Authentification » et « Consultation des alertes » | Traduits fidèlement par les endpoints des ressources Authentification et Alertes. |
| Entités Utilisateur, Rôle, Alerte, Log, Règle, Statistique, Configuration, Liste noire | Chacune correspond directement à une ressource de l'API ; les champs mentionnés dans les paramètres des endpoints reprennent le dictionnaire de données du Livrable 5. |
| Règles d'intégrité (suppression déconseillée au profit d'une désactivation) | Respectées : aucun endpoint de suppression définitive n'est proposé pour les Règles ou les entrées de Liste noire ; seule une opération de changement de statut (activation/désactivation) est prévue. |

### 10.4 Points restant à valider avant le développement

- **Accès des utilisateurs en lecture seule aux journaux** : le cahier des charges (section 5.4) qualifie cet accès de « Limité », tandis que la conception UML (section 2.4) ne l'accorde pas du tout. Ce document retient, par prudence, l'absence d'accès du profil Lecture seule à la ressource Logs, conformément à la conception UML ; ce point doit être explicitement tranché avec le CCM avant le développement.
- **Permissions sur les ressources Configuration et Liste noire** : ces ressources n'étaient pas identifiées individuellement dans la matrice de permissions du cahier des charges. Ce document attribue la gestion de la Configuration générale au seul profil Administrateur (par analogie avec la responsabilité de configuration décrite en section 5.1 du cahier des charges) et la gestion de la Liste noire aux profils Administrateur et Analyste sécurité (par analogie avec la gestion des règles de détection) ; ces choix restent à confirmer avec le CCM.
- **Persistance ou calcul à la demande des statistiques** : conformément à la question déjà signalée dans les Livrables 2, 3 et 5, l'endpoint `GET /v1/statistiques` est conçu de manière compatible avec les deux hypothèses (statistiques précalculées ou calculées à la demande) ; le choix définitif reste à trancher avant l'implémentation.
- **Limitation des tentatives d'authentification** : le principe de protection contre les abus est posé en section 8, mais les seuils précis (nombre de tentatives, durée de blocage) ne sont pas définis dans ce document et devront être précisés lors de la conception détaillée.

---

*Fin du document — Livrable 6.*
