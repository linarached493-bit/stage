# Spécifications fonctionnelles et techniques — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 2 — Spécifications fonctionnelles et techniques
**Document de référence :** `docs/cahier_des_charges.md` (Livrable 1, validé)
**Statut :** Spécification — aucune implémentation

---

## 1. Objectif du document

### 1.1 Rôle des spécifications techniques

Ce document a pour rôle de traduire les besoins exprimés dans le cahier des charges (Livrable 1) en une description structurée du fonctionnement attendu du système : ses composants, leurs responsabilités, les données qui circulent entre eux, les technologies retenues et les contraintes qui encadrent leur mise en œuvre. Il s'agit d'un document de **spécification**, et non de conception détaillée : il décrit *ce que fait chaque composant et comment il communique avec les autres*, sans définir *comment il est codé*.

### 1.2 Lien avec le cahier des charges

Le cahier des charges a défini le périmètre fonctionnel du projet (objectifs, profils utilisateurs, cas d'utilisation, menaces à détecter, contraintes générales). Ce document s'appuie directement sur ce périmètre et le décline en composants logiques cohérents avec :

- les dix fonctionnalités identifiées en section 3 du cahier des charges (F1 à F10) ;
- les neuf menaces à détecter listées en section 7 du cahier des charges ;
- les exigences non fonctionnelles définies en section 4 du cahier des charges ;
- les contraintes techniques générales déjà annoncées en section 8 du cahier des charges (Python, FastAPI, Scapy, PostgreSQL, React, Docker, Linux).

Aucune exigence nouvelle n'est introduite ici : ce document précise et organise ce qui a déjà été validé, sans en modifier le contenu.

### 1.3 Périmètre couvert

Ce document couvre :

- l'architecture logique du système (composants et responsabilités) ;
- le flux de données de bout en bout ;
- la justification des choix technologiques ;
- les contraintes techniques transverses ;
- les modes de communication entre modules ;
- la gestion générale des erreurs et des situations dégradées ;
- les hypothèses et les limites techniques retenues pour cette première version.

Ce document ne couvre pas : les diagrammes UML, la conception détaillée de la base de données, la définition des points d'accès (endpoints) de l'API, ni aucun élément de code. Ces éléments feront l'objet de livrables ultérieurs.

---

## 2. Vue d'ensemble du système

Le système est conçu comme un ensemble de composants logiques coopérant selon un enchaînement séquentiel, depuis l'observation du trafic réseau jusqu'à la restitution d'informations exploitables à un utilisateur.

De manière générale, le système :

1. **observe** le trafic circulant sur le réseau surveillé ;
2. **extrait** de ce trafic des informations exploitables ;
3. **évalue** ces informations au regard de règles de détection ;
4. **produit** des alertes lorsqu'une menace est identifiée ;
5. **conserve** un historique de tout ce qui a été observé ;
6. **expose** ces informations, de manière contrôlée, à des utilisateurs authentifiés via une interface web.

Le système repose sur neuf composants principaux, détaillés en section 3 : Capture réseau, Analyse du trafic, Moteur de détection, Gestion des alertes, Journalisation, Authentification, API Backend, Base de données, Interface Web. Ces composants sont conçus pour être indépendants dans leur logique interne, mais reliés entre eux par des échanges de données clairement définis (section 7), ce qui permet de faire évoluer chacun d'eux séparément sans remettre en cause l'ensemble du système.

Le système fonctionne selon un modèle d'**observation continue** : il ne s'active pas ponctuellement sur demande, mais surveille en permanence le trafic réseau, en parallèle de l'activité des utilisateurs qui consultent les résultats via l'interface web.

---

## 3. Architecture logique

### 3.1 Capture réseau

| Aspect | Détail |
|---|---|
| **Rôle** | Observer le trafic circulant sur l'interface réseau surveillée. |
| **Responsabilités** | Écouter le trafic en continu ; extraire, pour chaque paquet observé, les informations pertinentes (adresses IP source/destination, ports, protocole, taille, indicateurs de connexion) ; transmettre ces informations au composant d'analyse. |
| **Entrées** | Trafic brut circulant sur l'interface réseau surveillée. |
| **Sorties** | Informations structurées relatives à chaque paquet observé. |
| **Interactions** | Transmet ses données au composant **Analyse du trafic** ; peut signaler un état d'erreur au composant de **Journalisation** en cas de dysfonctionnement de la capture. |

### 3.2 Analyse du trafic

| Aspect | Détail |
|---|---|
| **Rôle** | Transformer les informations brutes issues de la capture en indicateurs exploitables. |
| **Responsabilités** | Regrouper et agréger les informations reçues (par exemple : nombre de connexions par source, fréquence d'apparition d'un port, volumétrie observée sur une période donnée) ; produire des indicateurs synthétiques utilisables par le moteur de détection. |
| **Entrées** | Informations structurées transmises par la Capture réseau. |
| **Sorties** | Indicateurs d'analyse (fréquences, volumétries, répartitions). |
| **Interactions** | Reçoit ses données de la **Capture réseau** ; transmet ses indicateurs au **Moteur de détection** ; transmet également les événements observés à la **Journalisation**, qu'ils soient ou non jugés suspects. |

### 3.3 Moteur de détection

| Aspect | Détail |
|---|---|
| **Rôle** | Évaluer les indicateurs d'analyse au regard des règles de détection configurées, afin d'identifier les menaces listées dans le cahier des charges. |
| **Responsabilités** | Appliquer l'ensemble des règles actives à chaque indicateur reçu ; déterminer si une correspondance justifie le déclenchement d'une alerte ; associer à chaque détection positive un type de menace et un niveau de gravité. |
| **Entrées** | Indicateurs d'analyse ; règles de détection actives (issues de la Base de données). |
| **Sorties** | Détections positives (menace identifiée, gravité associée). |
| **Interactions** | Reçoit ses données de l'**Analyse du trafic** ; consulte les règles stockées dans la **Base de données** (via l'API Backend) ; transmet ses détections positives à la **Gestion des alertes**. |

### 3.4 Gestion des alertes

| Aspect | Détail |
|---|---|
| **Rôle** | Centraliser les détections positives et en assurer le cycle de vie. |
| **Responsabilités** | Structurer chaque détection en une alerte complète (horodatage, type de menace, source, gravité, statut initial) ; transmettre l'alerte pour enregistrement ; permettre la mise à jour ultérieure du statut d'une alerte (traitée, en cours, faux positif). |
| **Entrées** | Détections positives transmises par le Moteur de détection ; demandes de mise à jour de statut provenant de l'API Backend. |
| **Sorties** | Alertes structurées, prêtes à être journalisées et consultées. |
| **Interactions** | Reçoit ses données du **Moteur de détection** ; transmet les alertes à la **Journalisation** et à la **Base de données** (via l'API Backend) ; met ses alertes à disposition de l'**API Backend** pour consultation par l'Interface Web. |

### 3.5 Journalisation

| Aspect | Détail |
|---|---|
| **Rôle** | Conserver durablement l'historique des événements observés et des alertes générées. |
| **Responsabilités** | Enregistrer chaque événement transmis par les autres composants, avec un horodatage précis ; garantir que l'enregistrement des événements ne soit pas perdu en cas d'incident sur un autre composant. |
| **Entrées** | Événements transmis par la Capture réseau, l'Analyse du trafic et la Gestion des alertes. |
| **Sorties** | Journal d'événements consultable. |
| **Interactions** | Reçoit ses données de plusieurs composants (Capture réseau, Analyse, Gestion des alertes) ; transmet les journaux à la **Base de données** ; met les journaux à disposition de l'**API Backend** pour consultation. |

### 3.6 Authentification

| Aspect | Détail |
|---|---|
| **Rôle** | Contrôler l'accès au système et garantir que chaque action est associée à un utilisateur identifié et à un profil autorisé. |
| **Responsabilités** | Vérifier les identifiants fournis par un utilisateur ; établir une session associée à un profil (Administrateur, Analyste sécurité, Lecture seule) ; vérifier, pour chaque action demandée, que le profil de l'utilisateur l'autorise. |
| **Entrées** | Identifiants fournis par l'utilisateur ; demandes d'action accompagnées d'une session active. |
| **Sorties** | Confirmation ou refus d'accès ; profil de l'utilisateur authentifié. |
| **Interactions** | Sollicité par l'**Interface Web** à chaque connexion ; consulté par l'**API Backend** avant l'exécution de toute action pour vérifier les permissions associées au profil. |

### 3.7 API Backend

| Aspect | Détail |
|---|---|
| **Rôle** | Constituer le point d'échange structuré entre l'Interface Web et l'ensemble des composants internes du système. |
| **Responsabilités** | Recevoir les demandes de l'Interface Web (consultation d'alertes, de journaux, de statistiques, gestion des règles et des utilisateurs) ; vérifier les autorisations via l'Authentification ; transmettre les demandes aux composants concernés (Base de données, Gestion des alertes, Journalisation) ; retourner les résultats à l'Interface Web. |
| **Entrées** | Requêtes émises par l'Interface Web. |
| **Sorties** | Réponses structurées (données d'alertes, de journaux, de statistiques, confirmations d'actions). |
| **Interactions** | Interagit avec l'**Interface Web** en frontal ; interagit avec l'**Authentification**, la **Base de données**, la **Gestion des alertes** et la **Journalisation** en interne. |

### 3.8 Base de données

| Aspect | Détail |
|---|---|
| **Rôle** | Assurer la conservation persistante de l'ensemble des informations manipulées par le système. |
| **Responsabilités** | Stocker les utilisateurs, les alertes, les journaux, les règles de détection et les statistiques ; restituer ces informations à la demande des autres composants. |
| **Entrées** | Données transmises par la Gestion des alertes, la Journalisation et l'API Backend. |
| **Sorties** | Données stockées, restituées sur demande. |
| **Interactions** | Sollicitée principalement par l'**API Backend**, ainsi que par la **Gestion des alertes** et la **Journalisation** pour l'enregistrement des données. |

### 3.9 Interface Web

| Aspect | Détail |
|---|---|
| **Rôle** | Offrir aux utilisateurs un point d'accès visuel au système, adapté à leur profil. |
| **Responsabilités** | Présenter les alertes, les journaux et les statistiques ; permettre la gestion des règles de détection et des utilisateurs selon le profil connecté ; solliciter l'authentification avant tout accès. |
| **Entrées** | Actions de l'utilisateur (connexion, consultation, création/modification de règles ou d'utilisateurs). |
| **Sorties** | Affichage des données reçues de l'API Backend. |
| **Interactions** | Communique exclusivement avec l'**API Backend**, qui lui-même sollicite l'**Authentification** et les autres composants internes. |

### 3.10 Synthèse des interactions

| Composant | Reçoit de | Transmet à |
|---|---|---|
| Capture réseau | Trafic réseau brut | Analyse du trafic, Journalisation (erreurs) |
| Analyse du trafic | Capture réseau | Moteur de détection, Journalisation |
| Moteur de détection | Analyse du trafic, Base de données (règles) | Gestion des alertes |
| Gestion des alertes | Moteur de détection, API Backend | Journalisation, Base de données |
| Journalisation | Capture réseau, Analyse, Gestion des alertes | Base de données |
| Authentification | Interface Web, API Backend | Interface Web, API Backend |
| API Backend | Interface Web | Authentification, Base de données, Gestion des alertes, Journalisation |
| Base de données | API Backend, Gestion des alertes, Journalisation | API Backend |
| Interface Web | Utilisateur | API Backend |

---

## 4. Flux de données

### 4.1 Parcours complet d'un paquet réseau

Le parcours d'une donnée, depuis sa capture jusqu'à son affichage, suit les étapes suivantes :

1. **Capture** : un paquet circulant sur le réseau surveillé est intercepté par le composant de Capture réseau, qui en extrait les informations pertinentes.
2. **Analyse** : ces informations sont transmises au composant d'Analyse du trafic, qui les intègre à des indicateurs (fréquence, volumétrie, répartition).
3. **Détection** : les indicateurs sont évalués par le Moteur de détection au regard des règles actives.
4. **Décision** : si une correspondance est identifiée, une détection positive est produite ; sinon, l'événement est simplement journalisé sans déclenchement d'alerte.
5. **Génération de l'alerte** : en cas de détection positive, la Gestion des alertes structure une alerte complète (type, gravité, horodatage, statut).
6. **Journalisation** : l'événement (avec ou sans alerte associée) est enregistré de manière durable.
7. **Persistance** : les données (événement, alerte) sont stockées dans la Base de données.
8. **Mise à disposition** : l'API Backend rend ces données accessibles, sous réserve d'authentification et d'autorisation.
9. **Consultation** : l'Interface Web récupère les données via l'API Backend et les présente à l'utilisateur authentifié, selon son profil.

### 4.2 Diagramme ASCII du flux de données

```
 Trafic réseau
     │
     ▼
┌───────────────────┐
│  Capture réseau    │
└─────────┬─────────┘
          │ paquet structuré
          ▼
┌───────────────────┐
│  Analyse du trafic │
└─────────┬─────────┘
          │ indicateurs
          ▼
┌───────────────────┐        ┌────────────────────┐
│ Moteur de détection │◄─────│  Règles (Base de     │
└─────────┬─────────┘        │  données)            │
          │                   └────────────────────┘
          │ détection positive
          ▼
┌───────────────────┐
│ Gestion des alertes │
└────┬──────────┬────┘
     │          │
     │          │ tout événement
     ▼          ▼
┌─────────┐ ┌────────────────┐
│ Base de  │◄│ Journalisation  │
│ données  │ └────────────────┘
└────┬────┘
     │
     ▼
┌───────────────────┐
│    API Backend      │
└─────────┬─────────┘
          │ données autorisées
          ▼
┌───────────────────┐        ┌────────────────────┐
│  Interface Web      │◄─────►│  Authentification    │
└─────────┬─────────┘        └────────────────────┘
          │
          ▼
   Utilisateur (Admin,
   Analyste, Lecture seule)
```

---

## 5. Choix technologiques

| Technologie | Rôle | Justification | Avantages | Limites |
|---|---|---|---|---|
| **Python** | Langage principal de développement du backend et des composants d'analyse. | Langage largement utilisé en cybersécurité et en traitement de données réseau ; bonne lisibilité, adapté à un contexte pédagogique. | Écosystème riche, syntaxe claire, nombreuses bibliothèques disponibles pour le réseau et le web. | Performances brutes inférieures à des langages compilés pour certains traitements intensifs. |
| **FastAPI** | Framework utilisé pour exposer les fonctionnalités du système via une API. | Framework moderne, conçu pour construire des API structurées de façon claire et documentée. | Rapidité de mise en œuvre, documentation d'API générée automatiquement. | Nécessite une bonne organisation du code à mesure que le nombre de fonctionnalités augmente. |
| **Scapy** | Bibliothèque utilisée pour la capture et l'interprétation des paquets réseau. | Bibliothèque de référence en Python pour la manipulation de paquets réseau, adaptée à un usage pédagogique et réaliste. | Grande flexibilité dans l'interprétation des paquets, large couverture des protocoles courants. | Performances limitées face à des volumes de trafic très élevés, comparée à des outils de capture bas niveau dédiés. |
| **PostgreSQL** | Système de gestion de base de données utilisé pour la persistance des informations. | Système de base de données relationnelle robuste et largement éprouvé, adapté à des données structurées comme celles manipulées ici. | Fiabilité, robustesse, richesse fonctionnelle. | Nécessite une administration appropriée pour rester performant à mesure que le volume de données croît. |
| **React** | Bibliothèque utilisée pour la construction de l'Interface Web. | Bibliothèque répandue pour la construction d'interfaces interactives, adaptée à un tableau de bord de consultation. | Grande communauté, forte modularité de l'interface. | Nécessite une organisation du code front-end rigoureuse pour rester maintenable. |
| **Docker** | Outil de conteneurisation utilisé pour packager les différents composants du système. | Facilite le déploiement reproductible d'un système composé de plusieurs modules (capture, API, base de données, interface). | Portabilité, cohérence entre environnements de développement et d'exécution. | Ajoute une couche d'abstraction supplémentaire à prendre en compte lors du déploiement. |
| **Linux** | Système d'exploitation cible pour le déploiement du système. | Environnement de référence pour la capture réseau bas niveau et le déploiement de services de sécurité. | Bonne maîtrise des mécanismes réseau, large adoption dans les environnements serveur. | Nécessite des privilèges particuliers pour l'accès aux interfaces réseau en mode d'écoute. |

---

## 6. Contraintes techniques

| Contrainte | Détail |
|---|---|
| **Performances** | Le traitement du trafic capturé (analyse et détection) doit s'effectuer avec un délai réduit, afin que les alertes générées restent pertinentes et exploitables rapidement après l'événement observé. |
| **Sécurité** | L'accès au système doit systématiquement passer par le composant d'Authentification ; aucune fonctionnalité sensible (gestion des règles, gestion des utilisateurs) ne doit être accessible sans vérification préalable du profil de l'utilisateur. |
| **Modularité** | Chaque composant décrit en section 3 doit pouvoir évoluer indépendamment des autres, dès lors que les données échangées entre eux (section 7) restent cohérentes. |
| **Évolutivité** | L'ajout d'une nouvelle règle de détection ou d'un nouveau type de menace ne doit pas nécessiter de modification des autres composants que le Moteur de détection et, le cas échéant, la Base de données. |
| **Maintenabilité** | La séparation claire des responsabilités entre composants (capture, analyse, détection, alertes, journalisation, accès) doit permettre à une équipe restreinte de comprendre et de faire évoluer le système sans vision exhaustive de l'ensemble. |
| **Portabilité** | Le système, une fois conteneurisé, doit pouvoir être déployé sur différents environnements Linux sans adaptation majeure. |

---

## 7. Communication entre les modules

Les échanges entre les composants du système suivent des principes cohérents avec l'architecture décrite en section 3 :

- **Capture réseau → Analyse du trafic** : transmission continue d'informations structurées relatives à chaque paquet observé (adresses, ports, protocole, taille, indicateurs de connexion).
- **Analyse du trafic → Moteur de détection** : transmission d'indicateurs agrégés (fréquences, volumétries, répartitions) construits à partir des données brutes.
- **Analyse du trafic → Journalisation** : transmission de l'ensemble des événements observés, indépendamment de leur caractère suspect ou non.
- **Base de données → Moteur de détection** (via l'API Backend) : mise à disposition des règles de détection actives.
- **Moteur de détection → Gestion des alertes** : transmission des détections positives (type de menace, gravité).
- **Gestion des alertes → Journalisation** et **Gestion des alertes → Base de données** : transmission des alertes générées, pour conservation durable.
- **API Backend ↔ Authentification** : vérification systématique des droits associés à une session avant l'exécution de toute action demandée.
- **API Backend ↔ Base de données** : lecture et écriture des données persistantes (utilisateurs, alertes, journaux, règles, statistiques).
- **Interface Web ↔ API Backend** : point d'échange unique entre l'utilisateur et le système ; l'Interface Web ne communique avec aucun autre composant directement.

Cette organisation garantit que l'Interface Web ne dispose d'aucun accès direct aux composants internes (Capture, Analyse, Détection, Base de données) : tout passe par l'API Backend, qui centralise le contrôle des accès.

---

## 8. Gestion des erreurs

| Situation | Réaction attendue du système |
|---|---|
| **Perte de paquets** | Le système doit considérer la perte de paquets comme un phénomène possible et ne pas interrompre son fonctionnement global pour autant ; l'analyse se poursuit sur la base des paquets effectivement capturés, sans tenter de reconstituer les paquets manquants. |
| **Erreur de capture** | En cas d'incapacité du composant de Capture réseau à accéder à l'interface surveillée (droits insuffisants, interface indisponible), le système doit journaliser l'incident et signaler un état dégradé, sans provoquer l'arrêt des autres composants (consultation des données déjà enregistrées toujours possible). |
| **Indisponibilité de la base de données** | Les composants dépendants (API Backend, Gestion des alertes, Journalisation) doivent détecter cette indisponibilité et la signaler explicitement à l'utilisateur ou dans les journaux techniques, plutôt que d'échouer silencieusement ; les nouvelles données ne pouvant être persistées doivent être traitées de façon à limiter leur perte autant que raisonnablement possible. |
| **Erreur interne** (défaillance imprévue d'un composant) | Le composant concerné doit signaler l'erreur de manière explicite (journal technique), sans provoquer la défaillance en cascade des autres composants ; le système doit rester utilisable pour les fonctions non affectées par l'erreur. |
| **Utilisateur non authentifié** | Toute tentative d'accès à une fonctionnalité sans authentification valide doit être refusée par l'API Backend, avec un message clair invitant l'utilisateur à s'authentifier ; aucune donnée sensible ne doit être exposée avant vérification de l'identité et du profil de l'utilisateur. |

---

## 9. Hypothèses de fonctionnement

- Le système surveille un segment de réseau représentatif, accessible techniquement au composant de Capture réseau (conformément au périmètre défini dans le cahier des charges).
- Le volume de trafic observé reste compatible avec les capacités de traitement d'un système pédagogique, sans exigence de très haute performance.
- Les règles de détection sont définies et ajustées par des utilisateurs habilités (Administrateur, Analyste sécurité), et non générées automatiquement.
- Le système fonctionne sur un déploiement unique (une seule instance), sans répartition de charge ni redondance.
- Les utilisateurs du système disposent d'un accès réseau fiable à l'Interface Web pour la consultation des données.
- La liste des ports interdits et la liste noire d'adresses IP sont considérées comme des données de configuration fournies et tenues à jour par les utilisateurs habilités.

---

## 10. Limites techniques

- L'architecture proposée ne prévoit pas de mécanisme de haute disponibilité : une défaillance du composant de Capture réseau interrompt la surveillance jusqu'à son rétablissement.
- L'analyse du trafic repose sur des indicateurs et des règles définis à l'avance ; elle ne permet pas d'identifier des menaces ne correspondant à aucune règle existante.
- Le système ne procède à aucune inspection du contenu chiffré : seules les métadonnées de trafic sont exploitées, conformément aux limites déjà posées dans le cahier des charges.
- La communication entre l'Interface Web et l'API Backend constitue un point de passage unique ; toute indisponibilité de l'API Backend rend l'ensemble de l'interface inutilisable, même si la capture et la détection continuent de fonctionner en arrière-plan.
- Le système ne prévoit pas de mécanisme de blocage automatique du trafic malveillant, conformément au périmètre défini dans le cahier des charges.

---

## 11. Questions ouvertes

Les points suivants restent à valider avant d'entamer la conception détaillée (diagrammes UML, modélisation de la base de données, spécification de l'API) :

1. **Emplacement précis de la Capture réseau** : sur quelle machine ou quel point du réseau le composant de capture sera-t-il physiquement exécuté ?
2. **Mode d'exécution de l'Analyse et de la Détection** : ces composants doivent-ils fonctionner en flux continu ou par traitement périodique par lots ?
3. **Granularité des règles de détection** : les règles seront-elles génériques (un seuil global) ou paramétrables finement par type de menace et par utilisateur habilité ?
4. **Fréquence de mise à jour des statistiques** : les statistiques doivent-elles être calculées en continu ou recalculées à la demande de consultation ?
5. **Gestion de la montée en charge** : quel volume de trafic maximal le système doit-il être capable d'absorber sans dégradation notable ?
6. **Politique de purge des données** : au bout de combien de temps les journaux et alertes anciens peuvent-ils être archivés ou supprimés ?
7. **Mode de communication interne** : les composants internes (Capture, Analyse, Détection, Alertes, Journalisation) doivent-ils communiquer de façon synchrone ou asynchrone ?
8. **Environnement de déploiement définitif** : le système sera-t-il déployé sur un poste unique ou réparti sur plusieurs machines dès cette première version ?
9. **Gestion des sessions utilisateurs** : quelle doit être la durée de validité d'une session avant nécessité de ré-authentification ?
10. **Format d'échange interne** : les données échangées entre composants suivront-elles un format unique et standardisé, à définir dans les livrables suivants ?

---

*Fin du document — Livrable 2.*
