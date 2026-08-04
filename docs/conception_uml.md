# Conception UML — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 3 — Conception UML
**Documents de référence :** `docs/cahier_des_charges.md` (Livrable 1), `docs/specifications_techniques.md` (Livrable 2)
**Statut :** Conception — aucune implémentation

---

## 1. Objectif de la conception UML

### 1.1 Rôle de la modélisation UML

Ce document a pour objectif de représenter, à l'aide de diagrammes UML, la structure et le comportement du système déjà décrits textuellement dans les deux livrables précédents. La modélisation UML permet de :

- rendre visibles les acteurs du système et leurs interactions avec celui-ci ;
- structurer les classes métier et de service qui composeront le système ;
- illustrer le déroulement dans le temps des scénarios fonctionnels les plus importants ;
- représenter l'organisation des composants logiciels et leurs dépendances ;
- représenter le déploiement physique envisagé du système.

Il s'agit d'une étape de **conception**, intermédiaire entre la spécification (Livrable 2) et l'implémentation (livrables ultérieurs). Aucun code, aucune API ni aucun schéma de base de données ne sont produits à ce stade.

### 1.2 Lien avec les livrables précédents

- Les **acteurs** et les **cas d'utilisation** présentés en section 2 reprennent directement les profils utilisateurs (section 5) et les cas d'utilisation (section 6) du cahier des charges.
- Les **classes** présentées en section 3 découlent des entités métier (section 10 du cahier des charges) et des composants logiques (section 3 des spécifications techniques).
- Les **diagrammes de séquence** (section 4) illustrent le flux de données déjà décrit textuellement en section 4 des spécifications techniques.
- Le **diagramme de composants** (section 5) reprend l'architecture logique et les interactions déjà décrites en section 3 et 7 des spécifications techniques.
- Le **diagramme de déploiement** (section 6) s'appuie sur les contraintes techniques (Linux, PostgreSQL, Docker) déjà annoncées dans les deux livrables précédents.

Ce document ne remet en cause aucun des choix déjà validés ; il les organise sous une forme visuelle structurée.

---

## 2. Diagramme des cas d'utilisation

### 2.1 Acteurs du système

| Acteur | Nature | Origine |
|---|---|---|
| **Administrateur** | Acteur humain | Profil défini en section 5.1 du cahier des charges |
| **Analyste sécurité** | Acteur humain | Profil défini en section 5.2 du cahier des charges |
| **Utilisateur en lecture seule** | Acteur humain | Profil défini en section 5.3 du cahier des charges |
| **Réseau surveillé** | Acteur non humain (source de trafic) | Déclencheur du processus de détection (section 2.3 des spécifications techniques) |

### 2.2 Cas d'utilisation principaux

Les cas d'utilisation repris ci-dessous correspondent directement à ceux décrits en section 6 du cahier des charges :

- UC1 — Authentification
- UC2 — Visualiser les alertes
- UC3 — Configurer une règle de détection
- UC4 — Consulter les journaux
- UC5 — Consulter les statistiques
- UC6 — Gérer les utilisateurs
- UC7 — Détecter une menace et générer une alerte

### 2.3 Diagramme UML (ASCII)

```
   Administrateur                Analyste sécurité              Lecture seule
         │                              │                             │
         │                              │                             │
         ▼                              ▼                             ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                          Système IDS (CCM)                               │
 │                                                                           │
 │   ( UC1 : Authentification )                                             │
 │                                                                           │
 │   ( UC2 : Visualiser les alertes )                                       │
 │                                                                           │
 │   ( UC3 : Configurer une règle de détection )                            │
 │                                                                           │
 │   ( UC4 : Consulter les journaux )                                       │
 │                                                                           │
 │   ( UC5 : Consulter les statistiques )                                   │
 │                                                                           │
 │   ( UC6 : Gérer les utilisateurs )                                       │
 │                                                                           │
 │   ( UC7 : Détecter une menace et générer une alerte )                    │
 │                                                                           │
 └─────────────────────────────────────────────────────────────────────────┘
                                                                     ▲
                                                                     │
                                                            Réseau surveillé
```

### 2.4 Matrice d'association acteurs / cas d'utilisation

| Cas d'utilisation | Administrateur | Analyste sécurité | Lecture seule | Réseau surveillé |
|---|:---:|:---:|:---:|:---:|
| UC1 — Authentification | ✔ | ✔ | ✔ | |
| UC2 — Visualiser les alertes | ✔ | ✔ | ✔ | |
| UC3 — Configurer une règle de détection | ✔ | ✔ | | |
| UC4 — Consulter les journaux | ✔ | ✔ | | |
| UC5 — Consulter les statistiques | ✔ | ✔ | ✔ | |
| UC6 — Gérer les utilisateurs | ✔ | | | |
| UC7 — Détecter une menace et générer une alerte | | | | ✔ |

### 2.5 Description brève de chaque cas d'utilisation

- **UC1 — Authentification** : un utilisateur s'identifie afin d'accéder au système avec les droits correspondant à son profil.
- **UC2 — Visualiser les alertes** : un utilisateur consulte la liste des alertes générées par le système.
- **UC3 — Configurer une règle de détection** : un utilisateur habilité crée, modifie ou désactive une règle utilisée par le moteur de détection.
- **UC4 — Consulter les journaux** : un utilisateur habilité recherche et consulte l'historique des événements enregistrés.
- **UC5 — Consulter les statistiques** : un utilisateur consulte une synthèse de l'activité réseau et des alertes.
- **UC6 — Gérer les utilisateurs** : l'administrateur crée, modifie ou supprime des comptes utilisateurs.
- **UC7 — Détecter une menace et générer une alerte** : le système, à partir du trafic observé sur le réseau surveillé, identifie une correspondance avec une règle de détection et génère automatiquement une alerte.

---

## 3. Diagramme de classes

### 3.1 Classes identifiées

Les classes suivantes reprennent les entités métier du cahier des charges (section 10) et les composants fonctionnels des spécifications techniques (section 3).

#### Utilisateur

- **Responsabilités** : représenter une personne disposant d'un accès au système et le profil qui détermine ses permissions.
- **Attributs principaux** : identifiant, nom d'utilisateur, mot de passe (haché), profil, statut du compte, date de dernière connexion.
- **Opérations principales** : s'authentifier, changer de profil, activer/désactiver le compte.

#### Alerte

- **Responsabilités** : représenter une détection positive et son cycle de traitement.
- **Attributs principaux** : identifiant, type de menace, adresse(s) IP concernée(s), port(s) concerné(s), gravité, horodatage, statut de traitement.
- **Opérations principales** : changer de statut, associer une règle d'origine.

#### Log (journal d'événement)

- **Responsabilités** : représenter un événement réseau observé, qu'il ait ou non donné lieu à une alerte.
- **Attributs principaux** : identifiant, horodatage, type d'événement, adresses et ports concernés, protocole.
- **Opérations principales** : enregistrer un événement, être consulté selon des critères de recherche.

#### Règle

- **Responsabilités** : représenter une condition de détection utilisée par le moteur de détection pour identifier un type de menace donné.
- **Attributs principaux** : identifiant, nom, description, type de menace associée, condition de déclenchement, gravité associée, statut (active/inactive).
- **Opérations principales** : activer, désactiver, modifier la condition de déclenchement.

#### Statistique

- **Responsabilités** : représenter une synthèse agrégée de l'activité réseau et des alertes sur une période donnée.
- **Attributs principaux** : période considérée, volumétrie observée, répartition des alertes par type et par gravité.
- **Opérations principales** : être calculée, être consultée sur une période donnée.

#### PacketCapture

- **Responsabilités** : correspond au composant « Capture réseau » ; observe le trafic circulant sur l'interface surveillée et en extrait les informations pertinentes.
- **Attributs principaux** : interface surveillée, état de fonctionnement.
- **Opérations principales** : démarrer la capture, arrêter la capture, extraire les informations d'un paquet observé.

#### TrafficAnalyzer

- **Responsabilités** : correspond au composant « Analyse du trafic » ; transforme les informations brutes en indicateurs exploitables par le moteur de détection.
- **Attributs principaux** : fenêtre d'observation, indicateurs courants.
- **Opérations principales** : agréger les informations reçues, produire des indicateurs.

#### DetectionEngine

- **Responsabilités** : correspond au composant « Moteur de détection » ; évalue les indicateurs au regard des règles actives et identifie les menaces.
- **Attributs principaux** : ensemble des règles actives.
- **Opérations principales** : évaluer un indicateur, appliquer une règle, produire une détection positive.

#### AlertManager

- **Responsabilités** : correspond au composant « Gestion des alertes » ; structure les détections positives en alertes complètes et gère leur cycle de vie.
- **Attributs principaux** : liste des alertes en cours.
- **Opérations principales** : créer une alerte, mettre à jour son statut, transmettre l'alerte pour journalisation et persistance.

#### AuthService

- **Responsabilités** : correspond au composant « Authentification » ; vérifie les identifiants et contrôle les autorisations associées à un profil.
- **Attributs principaux** : session active.
- **Opérations principales** : authentifier un utilisateur, vérifier une autorisation, clôturer une session.

### 3.2 Diagramme UML des relations (ASCII)

```
┌───────────────────┐        capture         ┌───────────────────┐
│   PacketCapture     │───────────────────────►│   TrafficAnalyzer   │
└───────────────────┘                         └─────────┬─────────┘
                                                          │ indicateurs
                                                          ▼
┌───────────────────┐        consulte        ┌───────────────────┐
│       Règle         │◄────────────────────────│  DetectionEngine    │
└─────────┬─────────┘                         └─────────┬─────────┘
          │ 1                                            │ détection positive
          │                                                ▼
          │ configure                        ┌───────────────────┐
          │                                    │    AlertManager     │
          │                                    └─────────┬─────────┘
          │                                              │ crée
          │                                              ▼
┌─────────▼─────────┐        qualifie        ┌───────────────────┐        alimente        ┌───────────────────┐
│    Utilisateur       │───────────────────────►│       Alerte         │───────────────────────►│         Log           │
└─────────┬─────────┘                         └───────────────────┘                         └───────────────────┘
          │ authentifié par                                                                          ▲
          ▼                                                                                           │ enregistre
┌───────────────────┐                                                                                 │
│    AuthService       │─────────────────────────────────────────────────────────────────────────────┘
└───────────────────┘

┌───────────────────┐        agrège
│    Statistique       │◄──────────────────── (Alerte, Log)
└───────────────────┘
```

### 3.3 Lecture des relations principales

| Relation | Nature | Description |
|---|---|---|
| PacketCapture → TrafficAnalyzer | Dépendance | Le trafic capturé alimente l'analyse. |
| TrafficAnalyzer → DetectionEngine | Dépendance | Les indicateurs produits alimentent la détection. |
| DetectionEngine → Règle | Association | Le moteur de détection consulte les règles actives. |
| DetectionEngine → AlertManager | Dépendance | Une détection positive déclenche la création d'une alerte. |
| AlertManager → Alerte | Composition | Le gestionnaire d'alertes crée et gère les instances d'alerte. |
| Utilisateur → Règle | Association | Un utilisateur habilité configure les règles. |
| Utilisateur → Alerte | Association | Un utilisateur habilité qualifie le statut d'une alerte. |
| Utilisateur → AuthService | Dépendance | Un utilisateur est authentifié via ce service. |
| Alerte / Log → Statistique | Dépendance | Les statistiques sont calculées à partir des alertes et des journaux. |

---

## 4. Diagrammes de séquence

### 4.1 Capture d'un paquet réseau

**Description** : ce scénario illustre l'observation continue du trafic par le composant de capture et sa transmission vers l'analyse.

```
Réseau surveillé      PacketCapture        TrafficAnalyzer        Log
      │                     │                     │                │
      │── paquet brut ─────►│                     │                │
      │                     │── infos extraites ─►│                │
      │                     │                     │── événement ──►│
      │                     │                     │                │
```

### 4.2 Détection d'une menace

**Description** : ce scénario illustre l'évaluation des indicateurs d'analyse par le moteur de détection, à partir des règles actives.

```
TrafficAnalyzer       DetectionEngine            Règle           AlertManager
      │                      │                     │                   │
      │── indicateurs ──────►│                     │                   │
      │                      │── règles actives ──►│                   │
      │                      │◄── conditions ───────│                   │
      │                      │  (évaluation interne)                   │
      │                      │── détection positive ───────────────────►│
      │                      │                     │                   │
```

### 4.3 Génération d'une alerte

**Description** : ce scénario illustre la structuration d'une détection positive en alerte, puis son enregistrement.

```
DetectionEngine        AlertManager              Log             Base de données
      │                      │                     │                   │
      │── détection ────────►│                     │                   │
      │                      │── crée l'alerte ───►│                   │
      │                      │                     │── persiste ──────►│
      │                      │── persiste l'alerte ────────────────────►│
      │                      │                     │                   │
```

### 4.4 Consultation des alertes

**Description** : ce scénario illustre la consultation, par un utilisateur authentifié, de la liste des alertes via l'interface web et l'API.

```
Utilisateur      Interface Web      API Backend      AuthService      Base de données
    │                  │                  │                │                  │
    │── demande ──────►│                  │                │                  │
    │                  │── requête ──────►│                │                  │
    │                  │                  │── vérifie ────►│                  │
    │                  │                  │◄── autorisé ───│                  │
    │                  │                  │── lit alertes ─────────────────────►│
    │                  │                  │◄── résultats ───────────────────────│
    │                  │◄── réponse ──────│                │                  │
    │◄── affichage ────│                  │                │                  │
```

### 4.5 Authentification d'un utilisateur

**Description** : ce scénario illustre la vérification des identifiants d'un utilisateur et l'ouverture d'une session associée à son profil.

```
Utilisateur      Interface Web      API Backend      AuthService      Base de données
    │                  │                  │                │                  │
    │── identifiants ─►│                  │                │                  │
    │                  │── transmet ─────►│                │                  │
    │                  │                  │── vérifie ────►│                  │
    │                  │                  │                │── consulte ─────►│
    │                  │                  │                │◄── compte ───────│
    │                  │                  │◄── session ────│                  │
    │                  │◄── confirmation ─│                │                  │
    │◄── accès profil ─│                  │                │                  │
```

---

## 5. Diagramme de composants

### 5.1 Composants logiciels

Les composants présentés reprennent directement l'architecture logique décrite en section 3 des spécifications techniques : Capture réseau, Analyse du trafic, Moteur de détection, Gestion des alertes, Journalisation, Authentification, API Backend, Base de données, Interface Web.

### 5.2 Diagramme UML des dépendances (ASCII)

```
┌────────────────────┐
│   Interface Web      │
└──────────┬──────────┘
           │ dépend de
           ▼
┌────────────────────┐
│    API Backend        │
└───┬───────┬───────┬──┘
    │       │       │
    │dépend │dépend │dépend
    │de     │de     │de
    ▼       ▼       ▼
┌────────┐ ┌──────────────┐ ┌────────────────┐
│Authenti-│ │Gestion des    │ │ Base de          │
│fication │ │alertes        │ │ données           │
└────────┘ └──────┬───────┘ └────────▲────────┘
                   │ dépend de                 │
                   ▼                            │
           ┌────────────────┐                  │
           │  Journalisation  │──────────────────┘
           └────────▲────────┘
                     │ dépend de
           ┌────────┴────────┐
           │ Moteur de         │
           │ détection          │
           └────────▲────────┘
                     │ dépend de
           ┌────────┴────────┐
           │ Analyse du         │
           │ trafic             │
           └────────▲────────┘
                     │ dépend de
           ┌────────┴────────┐
           │ Capture réseau     │
           └────────────────┘
```

### 5.3 Lecture du diagramme

Ce diagramme met en évidence que :

- l'**Interface Web** ne dépend que de l'**API Backend**, conformément au principe d'accès unique décrit en section 7 des spécifications techniques ;
- l'**API Backend** dépend de l'**Authentification**, de la **Gestion des alertes** et de la **Base de données** pour répondre aux demandes de l'interface ;
- la chaîne **Capture réseau → Analyse du trafic → Moteur de détection → Gestion des alertes → Journalisation** correspond au flux de traitement du trafic décrit en section 4 des spécifications techniques ;
- la **Base de données** constitue le point de convergence de la persistance pour la Gestion des alertes, la Journalisation et l'API Backend.

---

## 6. Diagramme de déploiement

### 6.1 Architecture logique de déploiement

```
┌───────────────────────────────────────────────────────────────┐
│                     Machine Linux (Serveur)                    │
│                                                                 │
│   ┌───────────────────────────────┐   ┌──────────────────────┐ │
│   │        Nœud « IDS Backend »      │   │   Nœud « Base de       │ │
│   │                                 │   │   données »            │ │
│   │  - Capture réseau               │   │                        │ │
│   │  - Analyse du trafic            │──►│  - PostgreSQL           │ │
│   │  - Moteur de détection          │   │                        │ │
│   │  - Gestion des alertes          │   │                        │ │
│   │  - Journalisation               │   │                        │ │
│   │  - Authentification             │   │                        │ │
│   │  - API Backend                  │   │                        │ │
│   └───────────────┬─────────────────┘   └──────────────────────┘ │
│                    │ HTTP / HTTPS                                 │
└────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │   Nœud « Interface Web »     │
        │        (React)               │
        └──────────────┬────────────┘
                        │ HTTP / HTTPS
                        ▼
        ┌───────────────────────────┐
        │        Utilisateurs           │
        │ (Administrateur, Analyste,    │
        │      Lecture seule)           │
        └───────────────────────────┘
```

### 6.2 Remarques sur le déploiement

- L'ensemble des composants internes (Capture, Analyse, Détection, Alertes, Journalisation, Authentification, API) est regroupé sur une même machine Linux, conformément aux hypothèses de fonctionnement énoncées en section 9 des spécifications techniques (déploiement unique, sans redondance).
- La Base de données est représentée comme un nœud distinct, ce qui n'exclut pas un hébergement sur la même machine physique ; ce point relève d'une décision technique restant à confirmer (voir section 8).
- L'Interface Web est accessible aux utilisateurs via le réseau, exclusivement au travers de l'API Backend, conformément au principe d'accès unique déjà établi.

---

## 7. Relations entre les diagrammes

Les diagrammes présentés dans ce document ne sont pas indépendants : ils décrivent le même système sous des angles complémentaires.

- Le **diagramme des cas d'utilisation** (section 2) définit *ce que les acteurs peuvent faire* avec le système ; il constitue le point de départ de la conception.
- Le **diagramme de classes** (section 3) traduit ces cas d'utilisation en éléments structurels : chaque cas d'utilisation mobilise une ou plusieurs classes (par exemple, UC7 « Détecter une menace » mobilise PacketCapture, TrafficAnalyzer, DetectionEngine et AlertManager).
- Les **diagrammes de séquence** (section 4) montrent *comment* les classes identifiées collaborent dans le temps pour réaliser un cas d'utilisation donné ; ils rendent concret le comportement dynamique du diagramme de classes.
- Le **diagramme de composants** (section 5) regroupe les classes en unités logicielles cohérentes, correspondant à l'architecture déjà définie dans les spécifications techniques, et met en évidence leurs dépendances.
- Le **diagramme de déploiement** (section 6) positionne ces composants sur une infrastructure physique, en cohérence avec les contraintes techniques (Linux, PostgreSQL) déjà validées.

Ainsi, la lecture de ce document doit se faire de façon progressive : des cas d'utilisation (le besoin), vers les classes (la structure), vers les séquences (le comportement), vers les composants (l'organisation logicielle), puis vers le déploiement (l'infrastructure).

---

## 8. Vérification de cohérence

### 8.1 Cohérence avec le cahier des charges

| Élément du cahier des charges | Vérification |
|---|---|
| Profils utilisateurs (section 5) | Repris à l'identique comme acteurs du diagramme de cas d'utilisation (section 2.1) et comme attribut « profil » de la classe Utilisateur. |
| Cas d'utilisation (section 6) | Repris à l'identique (UC1 à UC7) dans le diagramme de cas d'utilisation et dans les diagrammes de séquence correspondants. |
| Fonctionnalités F1 à F10 (section 3) | Chacune trouve une correspondance dans au moins une classe ou un composant (ex. F1 → PacketCapture, F5 → AlertManager, F9 → Règle). |
| Menaces à détecter (section 7) | Représentées de manière générique par la classe Règle et le comportement du DetectionEngine ; aucune règle spécifique à une menace n'est modélisée individuellement à ce stade, ce qui est cohérent avec le principe de généricité du moteur de détection. |
| Limites du projet (section 13) | Respectées : aucun mécanisme de blocage automatique n'apparaît dans les diagrammes ; aucune inspection du trafic chiffré n'est représentée. |

### 8.2 Cohérence avec les spécifications techniques

| Élément des spécifications techniques | Vérification |
|---|---|
| Neuf composants logiques (section 3) | Tous représentés dans le diagramme de composants (section 5) et dans le diagramme de déploiement (section 6). |
| Flux de données de bout en bout (section 4) | Retrouvé dans les diagrammes de séquence « Capture d'un paquet réseau », « Détection d'une menace » et « Génération d'une alerte ». |
| Principe d'accès unique via l'API Backend (section 7) | Respecté : l'Interface Web ne communique qu'avec l'API Backend dans le diagramme de composants et dans les diagrammes de séquence « Consultation des alertes » et « Authentification ». |
| Gestion des erreurs (section 8) | Non représentée explicitement dans les diagrammes de séquence, qui décrivent le scénario nominal ; ce point est signalé en section 8.3 ci-dessous comme point à clarifier. |
| Hypothèse de déploiement unique (section 9) | Respectée dans le diagramme de déploiement (section 6), avec une réserve sur la localisation exacte de la Base de données. |

### 8.3 Points à clarifier

- Les diagrammes de séquence présentés décrivent le **scénario nominal** de chaque cas d'utilisation ; les scénarios d'erreur (perte de paquets, base de données indisponible, utilisateur non authentifié), déjà décrits textuellement en section 8 des spécifications techniques, n'ont pas fait l'objet de diagrammes de séquence dédiés à ce stade.
- La localisation exacte de la Base de données (même machine que l'IDS ou machine distincte) reste une question ouverte, déjà identifiée en section 11 des spécifications techniques (question 8).
- Le diagramme de classes représente la classe Règle de manière générique ; la question de savoir si chaque type de menace (section 7 du cahier des charges) nécessite une sous-classe dédiée ou reste gérée par un simple paramétrage de la classe Règle reste à trancher lors de la conception détaillée.
- La classe Statistique est représentée comme dépendante des classes Alerte et Log ; le mode de calcul (calcul continu ou calcul à la demande), déjà identifié comme question ouverte en section 11 des spécifications techniques (question 4), n'est pas tranché ici.

---

*Fin du document — Livrable 3.*
