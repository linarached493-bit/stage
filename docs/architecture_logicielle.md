# Architecture logicielle — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 4 — Architecture logicielle
**Documents de référence :** `docs/cahier_des_charges.md` (Livrable 1), `docs/specifications_techniques.md` (Livrable 2), `docs/conception_uml.md` (Livrable 3)
**Statut :** Architecture — aucune implémentation

---

## 1. Objectif du document

### 1.1 Rôle de l'architecture logicielle

Ce document a pour objectif de consolider, sous la forme d'une architecture logicielle cohérente, l'ensemble des éléments déjà définis dans les trois livrables précédents. Il précise l'organisation interne du système en modules, les responsabilités précises de chacun, les données qu'ils manipulent, les événements qu'ils échangent, ainsi que les principes transverses (sécurité, configuration, journalisation, gestion des erreurs) qui encadrent leur fonctionnement conjoint.

Il ne s'agit pas d'un document de conception détaillée au sens du code : aucune API REST n'est définie, aucun schéma de base de données n'est conçu, et aucune structure de projet n'est proposée. Ce document reste au niveau de l'organisation logicielle, dans la continuité directe de la conception UML.

### 1.2 Lien avec les livrables précédents

- Le **cahier des charges** a défini les besoins fonctionnels et non fonctionnels, les profils utilisateurs, les menaces à détecter et les contraintes générales du projet.
- Les **spécifications techniques** ont décrit les neuf composants logiques du système, le flux de données de bout en bout, les choix technologiques et les contraintes techniques transverses.
- La **conception UML** a représenté ces composants sous forme de classes, de cas d'utilisation, de séquences, de composants et de déploiement.
- Ce document reprend cette même organisation en modules, en l'enrichissant d'un module supplémentaire — la **Configuration** — nécessaire pour gérer de façon cohérente les paramètres, règles, listes noires et seuils déjà mentionnés dans les livrables précédents mais jamais regroupés sous une responsabilité dédiée.

Aucun élément déjà validé n'est remis en cause ; ce document ajoute le niveau de détail architectural nécessaire à la préparation des livrables suivants (conception détaillée, implémentation).

---

## 2. Principes d'architecture

L'architecture du système repose sur les principes suivants, retenus pour répondre aux exigences non fonctionnelles définies en section 4 du cahier des charges :

| Principe | Application dans le système |
|---|---|
| **Modularité** | Le système est découpé en modules aux frontières claires (Capture, Analyse, Détection, Alertes, Journalisation, Authentification, API Backend, Interface Web, Base de données, Configuration), chacun correspondant à une responsabilité unique. |
| **Séparation des responsabilités** | Chaque module traite un aspect précis du système (observation, analyse, décision, restitution, persistance, accès) ; aucun module ne cumule des responsabilités relevant de plusieurs domaines. |
| **Faible couplage** | Les modules communiquent par des échanges de données explicites (événements, requêtes) plutôt que par des dépendances directes à leur fonctionnement interne ; l'Interface Web, par exemple, ne dépend que de l'API Backend. |
| **Forte cohésion** | Chaque module regroupe des responsabilités homogènes : le module de Détection ne s'occupe que de l'évaluation des règles, sans se préoccuper de la façon dont les alertes sont ensuite stockées ou affichées. |
| **Extensibilité** | L'ajout d'une nouvelle règle, d'un nouveau type de menace ou d'un nouveau canal de notification doit pouvoir se faire en modifiant un nombre limité de modules (typiquement Détection et Configuration), sans toucher au reste du système. |
| **Maintenabilité** | La séparation claire des responsabilités permet à une équipe restreinte de comprendre, corriger et faire évoluer un module sans devoir maîtriser l'ensemble du système. |
| **Simplicité** | L'architecture évite toute complexité non justifiée par les besoins exprimés dans le cahier des charges (pas de répartition de charge, pas de haute disponibilité, pas de mécanismes distribués complexes), conformément au périmètre pédagogique du projet. |

---

## 3. Vue d'ensemble de l'architecture

### 3.1 Modules du système

Le système est composé des dix modules suivants :

1. Capture réseau
2. Analyse
3. Détection
4. Gestion des alertes
5. Journalisation
6. Authentification
7. API Backend
8. Interface Web
9. Base de données
10. Configuration

### 3.2 Schéma global des interactions (ASCII)

```
                         ┌───────────────────────┐
                         │   Réseau surveillé       │
                         └───────────┬───────────┘
                                     │ trafic brut
                                     ▼
                         ┌───────────────────────┐
                         │     Capture réseau       │
                         └───────────┬───────────┘
                                     │ paquets structurés
                                     ▼
                         ┌───────────────────────┐
                         │        Analyse           │
                         └───────────┬───────────┘
                                     │ indicateurs
                                     ▼
        ┌────────────────┐  ┌───────────────────────┐
        │  Configuration    │─►│       Détection          │
        │ (règles, seuils,  │  └───────────┬───────────┘
        │ listes noires)    │              │ détection positive
        └────────────────┘              ▼
                                 ┌───────────────────────┐
                                 │  Gestion des alertes     │
                                 └─────┬───────────┬─────┘
                                       │           │
                          alertes      │           │ tout événement
                                       ▼           ▼
                          ┌────────────────┐ ┌───────────────────┐
                          │ Base de données  │◄│  Journalisation     │
                          └────────┬───────┘ └───────────────────┘
                                   │
                                   ▼
                          ┌───────────────────────┐
                          │      API Backend          │◄──────────┐
                          └───────────┬───────────┘             │
                                      │                            │ vérifie
                                      ▼                            │
                          ┌───────────────────────┐    ┌───────────────────────┐
                          │     Interface Web         │◄──►│   Authentification      │
                          └───────────┬───────────┘    └───────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │       Utilisateurs         │
                          │ (Admin, Analyste,          │
                          │  Lecture seule)             │
                          └───────────────────────┘
```

---

## 4. Description détaillée des modules

### 4.1 Capture réseau

| Aspect | Détail |
|---|---|
| **Mission** | Observer en continu le trafic circulant sur l'interface réseau surveillée. |
| **Responsabilités** | Écouter le trafic ; extraire les informations pertinentes de chaque paquet (adresses, ports, protocole, taille, indicateurs de connexion). |
| **Dépendances** | Aucune dépendance envers les autres modules ; dépend uniquement de l'accès à l'interface réseau surveillée. |
| **Données manipulées** | Paquets réseau bruts et leurs métadonnées extraites. |
| **Événements reçus** | Trafic circulant sur le réseau surveillé. |
| **Événements émis** | Paquet structuré (vers Analyse) ; signalement d'erreur de capture (vers Journalisation). |

### 4.2 Analyse

| Aspect | Détail |
|---|---|
| **Mission** | Transformer les informations brutes issues de la capture en indicateurs exploitables par la détection. |
| **Responsabilités** | Agréger les informations reçues sur une fenêtre d'observation ; produire des indicateurs (fréquences, volumétries, répartitions). |
| **Dépendances** | Dépend des données transmises par la Capture réseau. |
| **Données manipulées** | Paquets structurés en entrée ; indicateurs agrégés en sortie. |
| **Événements reçus** | Paquet structuré (de Capture réseau). |
| **Événements émis** | Indicateur d'analyse (vers Détection) ; événement observé (vers Journalisation). |

### 4.3 Détection

| Aspect | Détail |
|---|---|
| **Mission** | Évaluer les indicateurs d'analyse au regard des règles de détection actives, afin d'identifier les menaces définies dans le cahier des charges. |
| **Responsabilités** | Appliquer les règles actives à chaque indicateur reçu ; déterminer si une correspondance justifie une alerte ; associer un type de menace et une gravité à chaque détection positive. |
| **Dépendances** | Dépend des indicateurs transmis par l'Analyse ; dépend des règles, seuils et listes noires fournis par la Configuration. |
| **Données manipulées** | Indicateurs d'analyse ; règles de détection ; détections positives produites. |
| **Événements reçus** | Indicateur d'analyse (d'Analyse) ; règles actives (de Configuration). |
| **Événements émis** | Détection positive (vers Gestion des alertes). |

### 4.4 Gestion des alertes

| Aspect | Détail |
|---|---|
| **Mission** | Centraliser les détections positives et assurer le suivi de leur cycle de vie. |
| **Responsabilités** | Structurer chaque détection en alerte complète (horodatage, type, gravité, statut) ; permettre la mise à jour du statut d'une alerte (traitée, en cours, faux positif). |
| **Dépendances** | Dépend des détections positives transmises par la Détection ; dépend de la Base de données pour la persistance ; dépend de l'API Backend pour les demandes de mise à jour de statut. |
| **Données manipulées** | Alertes (création, mise à jour de statut). |
| **Événements reçus** | Détection positive (de Détection) ; demande de mise à jour de statut (de l'API Backend). |
| **Événements émis** | Alerte structurée (vers Journalisation et Base de données). |

### 4.5 Journalisation

| Aspect | Détail |
|---|---|
| **Mission** | Conserver durablement l'historique des événements observés et des alertes générées. |
| **Responsabilités** | Enregistrer chaque événement transmis, avec horodatage précis ; garantir que l'enregistrement ne soit pas perdu en cas d'incident sur un autre module. |
| **Dépendances** | Dépend des événements transmis par la Capture réseau, l'Analyse et la Gestion des alertes ; dépend de la Base de données pour la persistance. |
| **Données manipulées** | Journaux d'événements. |
| **Événements reçus** | Événement observé (de Capture réseau, Analyse) ; alerte structurée (de Gestion des alertes). |
| **Événements émis** | Journal persisté (vers Base de données). |

### 4.6 Authentification

| Aspect | Détail |
|---|---|
| **Mission** | Contrôler l'accès au système et garantir que chaque action est associée à un profil autorisé. |
| **Responsabilités** | Vérifier les identifiants fournis ; établir une session associée à un profil ; vérifier, pour chaque action demandée, que le profil de l'utilisateur l'autorise. |
| **Dépendances** | Dépend de la Base de données pour la vérification des comptes ; sollicité par l'API Backend. |
| **Données manipulées** | Identifiants, sessions, profils utilisateurs. |
| **Événements reçus** | Demande d'authentification (de l'API Backend) ; demande de vérification d'autorisation (de l'API Backend). |
| **Événements émis** | Confirmation ou refus d'accès (vers API Backend). |

### 4.7 API Backend

| Aspect | Détail |
|---|---|
| **Mission** | Constituer le point d'échange structuré unique entre l'Interface Web et l'ensemble des modules internes. |
| **Responsabilités** | Recevoir les demandes de l'Interface Web ; vérifier les autorisations via l'Authentification ; transmettre les demandes aux modules concernés ; retourner les résultats. |
| **Dépendances** | Dépend de l'Authentification, de la Base de données, de la Gestion des alertes, de la Journalisation et de la Configuration. |
| **Données manipulées** | Requêtes et réponses structurées relatives aux alertes, journaux, statistiques, règles et utilisateurs. |
| **Événements reçus** | Requête (de l'Interface Web). |
| **Événements émis** | Réponse structurée (vers Interface Web) ; demandes internes vers les modules concernés. |

### 4.8 Interface Web

| Aspect | Détail |
|---|---|
| **Mission** | Offrir aux utilisateurs un point d'accès visuel au système, adapté à leur profil. |
| **Responsabilités** | Présenter les alertes, journaux et statistiques ; permettre la gestion des règles et des utilisateurs selon le profil connecté ; solliciter l'authentification avant tout accès. |
| **Dépendances** | Dépend exclusivement de l'API Backend. |
| **Données manipulées** | Données affichées, actions initiées par l'utilisateur. |
| **Événements reçus** | Réponse de l'API Backend. |
| **Événements émis** | Requête vers l'API Backend (connexion, consultation, action de gestion). |

### 4.9 Base de données

| Aspect | Détail |
|---|---|
| **Mission** | Assurer la conservation persistante de l'ensemble des informations manipulées par le système. |
| **Responsabilités** | Stocker les utilisateurs, alertes, journaux, règles et statistiques ; restituer ces informations à la demande des autres modules. |
| **Dépendances** | Sollicitée par l'API Backend, la Gestion des alertes, la Journalisation et la Configuration. |
| **Données manipulées** | Ensemble des données persistantes du système. |
| **Événements reçus** | Demandes de lecture et d'écriture (des modules dépendants). |
| **Événements émis** | Données restituées (vers les modules demandeurs). |

### 4.10 Configuration

| Aspect | Détail |
|---|---|
| **Mission** | Centraliser et mettre à disposition l'ensemble des paramètres nécessaires au fonctionnement du système : règles de détection, seuils, listes noires, paramètres généraux. |
| **Responsabilités** | Conserver les paramètres de configuration ; les rendre disponibles à la Détection et aux autres modules qui en dépendent ; permettre leur mise à jour par les utilisateurs habilités via l'API Backend. |
| **Dépendances** | Dépend de la Base de données pour la persistance des paramètres ; sollicitée par la Détection et par l'API Backend. |
| **Données manipulées** | Règles de détection, seuils, listes noires, paramètres généraux du système. |
| **Événements reçus** | Demande de mise à jour de paramètres (de l'API Backend). |
| **Événements émis** | Paramètres actifs (vers Détection) ; confirmation de mise à jour (vers API Backend). |

---

## 5. Flux de communication

### 5.1 Description des communications

Les communications entre modules suivent deux grandes catégories de flux, cohérentes avec le flux de données déjà décrit en section 4 des spécifications techniques :

- **Flux de traitement du trafic** (continu, sans intervention utilisateur) : Capture réseau → Analyse → Détection → Gestion des alertes → Journalisation → Base de données. Ce flux est alimenté par la Configuration, qui fournit à tout moment les règles, seuils et listes noires actifs à la Détection.
- **Flux de consultation et de gestion** (déclenché par un utilisateur) : Interface Web → API Backend → (Authentification, Base de données, Gestion des alertes, Configuration) → API Backend → Interface Web. Ce flux est systématiquement soumis à une vérification d'autorisation par l'Authentification avant tout accès aux données ou toute action de gestion.

### 5.2 Diagramme ASCII des échanges

```
   ┌─────────────────┐   ┌─────────────┐   ┌─────────────┐   ┌────────────────────┐   ┌────────────────┐
   │  Capture réseau   │──►│   Analyse     │──►│  Détection    │──►│ Gestion des alertes  │──►│ Journalisation   │
   └─────────────────┘   └─────────────┘   └──────▲──────┘   └──────────┬─────────┘   └────────┬───────┘
                                                    │                     │                         │
                                            paramètres actifs     alertes persistées        journaux persistés
                                                    │                     │                         │
                                            ┌───────┴───────┐            ▼                         ▼
                                            │  Configuration   │   ┌─────────────────────────────────────┐
                                            └───────▲───────┘   │           Base de données                │
                                                    │            └───────────────▲─────────────────────────┘
                                        mise à jour │                            │
                                                    │                            │ lecture / écriture
                                            ┌───────┴────────────────────────────┴───────┐
                                            │                 API Backend                    │◄──────┐
                                            └───────────────────────┬───────────────────────┘        │
                                                                     │                                  │ vérifie
                                                                     ▼                                  │
                                            ┌───────────────────────────────────┐            ┌───────────────────┐
                                            │           Interface Web              │◄──────────►│   Authentification    │
                                            └───────────────────┬───────────────┘            └───────────────────┘
                                                                 │
                                                                 ▼
                                            ┌───────────────────────────────────┐
                                            │              Utilisateurs             │
                                            └───────────────────────────────────┘
```

---

## 6. Gestion de la configuration

Le module Configuration centralise l'ensemble des éléments paramétrables du système, afin d'éviter que ces informations ne soient dispersées entre les différents modules :

| Élément de configuration | Rôle |
|---|---|
| **Paramètres généraux** | Réglages globaux du système, tels que l'interface réseau surveillée ou la fenêtre d'observation utilisée par l'Analyse. |
| **Règles de détection** | Conditions permettant d'identifier chacune des menaces définies dans le cahier des charges (section 7) ; chaque règle associe un type de menace à une condition de déclenchement et à un niveau de gravité. |
| **Listes noires** | Ensemble des adresses IP considérées comme malveillantes, utilisées par la règle de détection relative à la communication avec une IP blacklistée. |
| **Seuils de détection** | Valeurs numériques de référence (par exemple, nombre de ports distincts sollicités, fréquence de connexions) utilisées par les règles pour distinguer un comportement normal d'un comportement suspect. |
| **Fichiers de configuration** | Représentation persistante de l'ensemble des éléments ci-dessus, permettant leur chargement au démarrage du système et leur mise à jour en cours de fonctionnement, sans nécessiter de redémarrage des autres modules. |

La gestion de la configuration doit respecter les principes suivants :

- toute modification d'un paramètre, d'une règle, d'une liste noire ou d'un seuil doit transiter par l'API Backend et être soumise au contrôle d'autorisation de l'Authentification, conformément à la matrice de permissions du cahier des charges ;
- le module Détection doit toujours utiliser la version active et à jour des paramètres de configuration, sans nécessiter de redémarrage du système lors d'une mise à jour ;
- la configuration doit être persistée dans la Base de données, afin de survivre à un redémarrage du système.

Aucune modalité d'implémentation (format de fichier, mécanisme de rechargement) n'est définie à ce stade ; ces éléments relèvent des livrables ultérieurs.

---

## 7. Gestion des journaux

Le système distingue plusieurs types de journaux, correspondant à des besoins différents :

| Type de journal | Rôle |
|---|---|
| **Journal d'événements réseau** | Enregistre chaque événement observé par la Capture réseau et l'Analyse, qu'il ait ou non donné lieu à une alerte ; constitue la base d'investigation en cas d'incident (correspond à l'entité Log du cahier des charges et de la conception UML). |
| **Journal d'alertes** | Enregistre chaque alerte générée par la Gestion des alertes, avec son évolution de statut dans le temps ; permet de retracer le traitement complet d'une menace détectée. |
| **Journal technique** | Enregistre les événements internes au fonctionnement du système lui-même (erreurs de capture, indisponibilité de la Base de données, erreurs internes), conformément à la stratégie de gestion des erreurs décrite en section 8 des spécifications techniques. |
| **Journal d'accès** | Enregistre les actions des utilisateurs authentifiés (connexions, actions de gestion sur les règles ou les utilisateurs), afin d'assurer la traçabilité des interventions humaines sur le système. |

Ces journaux partagent une exigence commune : ils doivent tous être horodatés de manière précise et rester consultables par les utilisateurs habilités via l'API Backend, conformément au cas d'utilisation UC4 défini dans le cahier des charges et la conception UML.

---

## 8. Gestion des erreurs

La stratégie générale de gestion des erreurs entre modules repose sur les principes suivants, dans la continuité de la section 8 des spécifications techniques :

- **Isolation des défaillances** : la défaillance d'un module ne doit pas provoquer l'arrêt en cascade des autres modules. Par exemple, une indisponibilité de la Base de données doit être détectée par les modules qui en dépendent (Gestion des alertes, Journalisation, API Backend), sans interrompre la Capture réseau ou l'Analyse.
- **Signalement explicite** : chaque module doit signaler explicitement toute erreur rencontrée, via le Journal technique, plutôt que d'échouer silencieusement.
- **Dégradation progressive** : en cas d'indisponibilité d'un module non critique pour la surveillance (par exemple l'Interface Web), le flux de traitement du trafic (Capture, Analyse, Détection, Alertes, Journalisation) doit continuer à fonctionner de manière autonome.
- **Refus explicite pour les accès non autorisés** : toute demande provenant d'un utilisateur non authentifié ou non autorisé doit être refusée par l'API Backend de façon explicite, sans exposer de donnée sensible.
- **Traçabilité des erreurs** : toute erreur significative (erreur de capture, indisponibilité de la Base de données, erreur interne) doit être journalisée avec un horodatage, afin de permettre une analyse a posteriori.

Cette stratégie ne définit aucun mécanisme technique précis (ex. : temporisation, nombre de tentatives) ; ces éléments relèvent de la conception détaillée et de l'implémentation.

---

## 9. Architecture de sécurité

| Mécanisme | Description générale |
|---|---|
| **Authentification** | Tout accès au système passe par une vérification préalable de l'identité de l'utilisateur, assurée par le module Authentification ; aucune fonctionnalité n'est accessible sans authentification valide. |
| **Autorisation** | Chaque action demandée est vérifiée au regard du profil de l'utilisateur (Administrateur, Analyste sécurité, Lecture seule), conformément à la matrice de permissions définie dans le cahier des charges ; cette vérification est centralisée au niveau de l'API Backend. |
| **Protection des données** | Les données sensibles (notamment les mots de passe) ne doivent jamais être manipulées ou stockées en clair ; les échanges entre l'Interface Web et l'API Backend doivent être protégés contre l'interception. |
| **Journalisation de sécurité** | Toute action d'authentification, de gestion des règles ou de gestion des utilisateurs doit être tracée dans le Journal d'accès, afin de permettre une revue a posteriori des actions sensibles. |
| **Principe du moindre privilège** | Chaque profil utilisateur ne dispose que des permissions strictement nécessaires à ses responsabilités (par exemple, l'Analyste sécurité ne peut pas gérer les comptes utilisateurs) ; chaque module ne sollicite des autres modules que les données strictement nécessaires à sa mission. |

Ces mécanismes reprennent et précisent, au niveau architectural, les exigences de sécurité déjà formulées en section 4 du cahier des charges et en section 6 des spécifications techniques, sans en détailler l'implémentation technique.

---

## 10. Points d'extension

L'architecture proposée a été conçue pour permettre les évolutions suivantes, déjà anticipées en section 14 du cahier des charges, sans remise en cause de la structure générale :

| Module concerné | Évolution envisageable | Facilité par |
|---|---|---|
| **Détection** | Ajout de mécanismes de détection comportementale ou de Machine Learning. | La Détection reçoit des indicateurs génériques de l'Analyse et applique des règles fournies par la Configuration ; un nouveau mode d'évaluation peut être ajouté sans modifier les autres modules. |
| **Configuration** | Ajout de nouveaux types de règles, de seuils ou de sources de listes noires (threat intelligence). | Le module centralise déjà l'ensemble des paramètres ; l'ajout d'un nouveau type de paramètre n'affecte que ce module et la Détection. |
| **Gestion des alertes** | Ajout de notifications par e-mail, Telegram ou intégration avec un SIEM externe. | La Gestion des alertes émet déjà des événements structurés (alerte créée, statut modifié) ; un nouveau canal de diffusion peut s'y greffer sans modifier la Détection ni la Journalisation. |
| **API Backend / Interface Web** | Ajout de fonctionnalités de tableau de bord temps réel, d'export PDF ou Excel. | L'API Backend constitue déjà le point d'accès unique aux données ; de nouvelles routes de consultation peuvent être ajoutées sans modifier les modules internes. |
| **Base de données** | Ajout de la géolocalisation des adresses IP dans les statistiques et les alertes. | La Base de données centralise déjà les alertes et journaux ; un enrichissement des données stockées n'affecte pas la logique des autres modules. |

Cette organisation modulaire garantit que chaque évolution future se traduit par une modification localisée à un ou deux modules, sans effet de bord sur l'ensemble du système.

---

## 11. Vérification de cohérence

### 11.1 Cohérence avec le cahier des charges

| Élément du cahier des charges | Vérification |
|---|---|
| Fonctionnalités F1 à F10 | Toutes couvertes par un ou plusieurs modules (ex. F4 « appliquer des règles » → Détection et Configuration ; F9 « gérer les règles » → Configuration et API Backend). |
| Profils utilisateurs et permissions (section 5) | Repris dans le mécanisme d'autorisation décrit en section 9, appliqué de façon centralisée par l'API Backend et l'Authentification. |
| Menaces à détecter (section 7) | Couvertes par le couple Détection/Configuration, qui applique les règles associées à chaque menace, conformément à la conception UML. |
| Limites du projet (section 13) | Respectées : aucune fonction de blocage automatique, aucune haute disponibilité, aucun mécanisme de Machine Learning n'apparaissent dans l'architecture proposée. |

### 11.2 Cohérence avec les spécifications techniques

| Élément des spécifications techniques | Vérification |
|---|---|
| Neuf composants logiques (section 3) | Tous repris à l'identique, avec l'ajout du module Configuration rendu nécessaire par la centralisation explicite des règles, seuils et listes noires. |
| Flux de données de bout en bout (section 4) | Repris à l'identique dans le schéma global (section 3.2) et le diagramme des échanges (section 5.2) de ce document. |
| Contraintes techniques (section 6) | Respectées : aucune contrainte de performance, sécurité, modularité, évolutivité, maintenabilité ou portabilité n'est contredite par l'architecture proposée. |
| Gestion des erreurs (section 8) | Reprise et précisée en section 8 de ce document, selon les mêmes cas (perte de paquets, erreur de capture, indisponibilité de la base de données, erreur interne, utilisateur non authentifié). |

### 11.3 Cohérence avec la conception UML

| Élément de la conception UML | Vérification |
|---|---|
| Classes métier et de service (section 3) | Correspondent directement aux modules décrits en section 4 de ce document (PacketCapture → Capture réseau, TrafficAnalyzer → Analyse, DetectionEngine → Détection, AlertManager → Gestion des alertes, AuthService → Authentification). |
| Diagramme de composants (section 5) | Cohérent avec le schéma global de ce document (section 3.2), à l'ajout près du module Configuration, absent du Livrable 3. |
| Diagramme de déploiement (section 6) | Compatible avec l'architecture proposée : les modules Capture, Analyse, Détection, Alertes, Journalisation, Authentification, API Backend et Configuration peuvent être hébergés sur le même nœud « IDS Backend » déjà défini. |

### 11.4 Ajustement nécessaire signalé

L'introduction du module **Configuration** dans ce livrable constitue un ajout par rapport à la conception UML (Livrable 3), qui ne l'avait pas identifié comme une classe ou un composant distinct. Cet ajout ne contredit aucun élément déjà validé : il regroupe explicitement des responsabilités (règles, seuils, listes noires) qui étaient déjà mentionnées de façon dispersée dans les livrables précédents (notamment associées à la classe Règle et au Moteur de détection). Il est recommandé, lors d'un futur ajustement de la conception UML, d'introduire une classe ou un composant Configuration afin de conserver une cohérence complète entre les livrables ; ce point est signalé ici à titre de suivi, sans qu'aucune modification ne soit apportée au Livrable 3 dans le cadre du présent document.

---

*Fin du document — Livrable 4.*
