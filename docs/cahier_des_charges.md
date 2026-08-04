# Cahier des charges — Système de Détection d'Intrusion (IDS) pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 1 — Cahier des charges
**Cadre :** Stage d'observation de fin de première année de cycle d'ingénieur
**Statut :** Document d'analyse des besoins

---

## 1. Présentation du projet

### 1.1 Contexte

Ce document constitue le premier livrable d'un projet mené dans le cadre d'un stage d'observation de fin de première année de cycle d'ingénieur. Il vise à poser les bases d'un système de détection d'intrusion (IDS) pédagogique, conçu pour le Centre Cinématographique Marocain (CCM), et servira de référence pour l'ensemble des livrables ultérieurs du projet.

Le stage d'observation offre l'occasion de découvrir, de manière encadrée, les grandes étapes d'un projet informatique réel : de l'analyse des besoins jusqu'à la conception d'un système, en passant par la compréhension des enjeux propres à un organisme d'accueil. Le choix d'un IDS permet d'aborder des notions fondamentales de cybersécurité et de réseaux informatiques, tout en restant sur un périmètre volontairement limité et progressif, adapté à un premier contact avec un projet d'ingénierie.

### 1.2 Présentation du CCM

Le Centre Cinématographique Marocain (CCM) est un établissement public marocain chargé de la régulation, du soutien et du développement de l'industrie cinématographique nationale. Ses missions incluent notamment :

- la délivrance d'agréments aux sociétés et professionnels du secteur cinématographique ;
- l'instruction et le suivi des demandes de subventions et d'aides à la production ;
- la gestion administrative de dossiers relatifs aux tournages et aux productions ;
- la mise à disposition de services numériques pour les professionnels du secteur (dépôt de dossiers, consultation de statuts, échanges d'informations).

Ces missions impliquent la manipulation d'informations sensibles (données administratives, financières et personnelles), ainsi que l'utilisation d'une infrastructure réseau et informatique pour assurer la continuité de ces services.

### 1.3 Problématique

Le CCM, comme toute organisation connectée à Internet, est exposé à des menaces informatiques : tentatives d'intrusion, balayages de ports, attaques par saturation, tentatives de connexion frauduleuses, ou encore communications avec des adresses IP connues comme malveillantes. Aucun mécanisme de surveillance réseau dédié n'est aujourd'hui en place pour identifier ce type de comportements suspects.

La problématique du projet peut donc être formulée ainsi : **comment concevoir un système simple et pédagogique permettant d'observer le trafic réseau d'une organisation afin d'y détecter des comportements suspects, de générer des alertes exploitables, et de constituer une première base de vigilance en matière de sécurité réseau ?**

### 1.4 Objectifs du projet

- Comprendre et analyser les besoins de surveillance réseau dans un contexte organisationnel réel.
- Concevoir les bases fonctionnelles d'un système de détection d'intrusion (IDS) réseau.
- Identifier les principales menaces réseau pertinentes pour le contexte du CCM.
- Poser un cadre clair de fonctionnalités, d'exigences et de limites, servant de référence aux livrables suivants (conception, architecture technique, implémentation).
- Constituer un support d'apprentissage structuré sur les fondamentaux de la cybersécurité réseau et de la démarche d'ingénierie logicielle.

### 1.5 Importance d'un IDS pour le CCM

- **Nature institutionnelle** : en tant qu'établissement public, le CCM est en contact avec de nombreux professionnels et administrés ; toute compromission aurait un impact sur la confiance envers l'institution.
- **Sensibilité des données traitées** : dossiers de subvention, données personnelles et documents administratifs nécessitent une vigilance particulière.
- **Continuité de service** : les services numériques du CCM sont utilisés par les professionnels du cinéma ; leur indisponibilité aurait un impact direct sur le secteur.
- **Absence de dispositif existant** : aucun outil de surveillance réseau n'est aujourd'hui déployé, ce qui laisse l'organisation sans visibilité sur d'éventuelles activités suspectes.
- **Valeur pédagogique et pratique** : même dans une version simple, un IDS constitue une première brique concrète de vigilance et de sensibilisation à la sécurité réseau.

### 1.6 Périmètre général du projet

Ce premier livrable se limite à l'analyse des besoins. Le projet global, dont les étapes suivantes feront l'objet de livrables distincts, portera sur :

- la surveillance d'un segment de réseau représentatif (et non de l'ensemble du système d'information du CCM) ;
- la détection d'un ensemble ciblé de menaces réseau couramment rencontrées, listées en section 7 ;
- un système fonctionnant en observation (détection et alerte), sans capacité de blocage automatique du trafic ;
- une solution pédagogique mais construite selon une démarche professionnelle, avec des choix techniques réalistes.

Toute question relative à la conception détaillée, à l'architecture technique, aux diagrammes UML, à l'API ou à la base de données sera traitée dans les livrables suivants et n'est pas abordée ici.

---

## 2. Description générale

### 2.1 Qu'est-ce qu'un IDS ?

Un IDS (*Intrusion Detection System*, système de détection d'intrusion) est un dispositif dont la fonction est d'observer un flux d'informations — ici, le trafic réseau — afin d'y détecter des signes d'activité suspecte, anormale ou malveillante. Il agit comme un outil de surveillance et d'alerte, et non comme un outil de blocage : il informe qu'un événement suspect s'est produit, mais n'interrompt pas lui-même le trafic concerné.

### 2.2 Les différents types d'IDS

| Critère | Type | Description |
|---|---|---|
| Emplacement de la surveillance | **NIDS** (Network IDS) | Surveille le trafic circulant sur un segment de réseau. |
| Emplacement de la surveillance | **HIDS** (Host IDS) | Surveille l'activité d'une machine unique (journaux système, fichiers). |
| Méthode de détection | **Basé sur signatures** | Compare le trafic observé à des motifs d'attaques connues. |
| Méthode de détection | **Basé sur anomalies** | Compare le trafic observé à un comportement considéré comme normal, et signale les écarts. |
| Méthode de détection | **Hybride** | Combine les deux approches précédentes. |

### 2.3 Fonctionnement général d'un IDS

De manière générale, un IDS suit un enchaînement simple :

1. **Capture** du trafic circulant sur le réseau surveillé.
2. **Analyse** de ce trafic pour en extraire des informations utiles (adresses, ports, fréquence, volumétrie).
3. **Comparaison** de ces informations avec des règles ou des signatures de détection.
4. **Génération d'une alerte** lorsqu'une correspondance ou une anomalie est identifiée.
5. **Journalisation** des événements observés, qu'ils aient ou non déclenché une alerte.

### 2.4 Avantages d'un IDS

- Permet de détecter des tentatives d'intrusion qui passeraient inaperçues sans surveillance dédiée.
- Fournit une traçabilité des événements réseau, utile en cas d'incident.
- Sensibilise les équipes techniques à l'état de sécurité réel du réseau.
- Constitue une première étape simple et peu coûteuse vers une meilleure posture de sécurité.

### 2.5 Limites d'un IDS

- Il ne bloque pas les attaques : il les signale uniquement.
- Son efficacité dépend directement de la qualité des règles définies (une règle mal calibrée entraîne des fausses alertes ou, à l'inverse, des menaces non détectées).
- Il a une visibilité réduite sur le trafic chiffré, dont il ne peut analyser que les métadonnées.
- Il nécessite une supervision humaine pour que les alertes générées soient réellement exploitées.
- Il ne remplace pas une politique de sécurité globale (pare-feu, gestion des accès, sensibilisation des utilisateurs).

### 2.6 Pourquoi un IDS réseau est adapté au contexte du CCM

Un IDS réseau (NIDS) est particulièrement adapté au contexte du CCM car il permet de surveiller l'ensemble du trafic transitant par un point du réseau sans nécessiter l'installation d'un agent sur chaque poste ou serveur. Cette approche est cohérente avec une organisation aux ressources informatiques limitées, et permet de couvrir les menaces les plus courantes (balayages de ports, saturations, tentatives de connexion frauduleuses) qui sont par nature observables au niveau du trafic réseau. Cette approche est également adaptée à un contexte pédagogique, car elle permet de manipuler des notions réseau fondamentales.

---

## 3. Objectifs fonctionnels

| # | Fonctionnalité | Description |
|---|---|---|
| F1 | **Capturer le trafic réseau** | Écouter le trafic circulant sur une interface réseau afin d'en extraire les informations nécessaires à l'analyse (adresses, ports, protocole, taille des paquets). |
| F2 | **Analyser les paquets** | Traiter les données capturées pour en extraire des indicateurs utiles (fréquence de connexions, répartition des ports sollicités, volumétrie observée). |
| F3 | **Détecter des comportements suspects** | Identifier, à partir des indicateurs obtenus, les situations pouvant correspondre à une activité suspecte ou malveillante. |
| F4 | **Appliquer des règles de détection** | Comparer le trafic analysé à un ensemble de règles définissant les conditions de déclenchement d'une alerte (seuils, motifs, listes). |
| F5 | **Générer des alertes** | Produire, pour chaque détection positive, une alerte comportant un horodatage, un type de menace, une source et un niveau de gravité. |
| F6 | **Enregistrer les événements** | Conserver de manière durable l'historique des événements observés et des alertes générées, à des fins de consultation ultérieure. |
| F7 | **Consulter les journaux** | Permettre aux utilisateurs autorisés de rechercher et de consulter l'historique des événements enregistrés. |
| F8 | **Gérer les utilisateurs** | Permettre la création, la modification et la suppression de comptes utilisateurs, ainsi que l'attribution de leur profil. |
| F9 | **Gérer les règles** | Permettre aux utilisateurs habilités de créer, modifier ou désactiver les règles de détection utilisées par le système. |
| F10 | **Afficher des statistiques** | Présenter une vue synthétique de l'activité réseau observée et des alertes générées (répartition par type, évolution dans le temps). |

---

## 4. Exigences non fonctionnelles

| Exigence | Détail |
|---|---|
| **Performance** | Le système doit pouvoir analyser le trafic réseau en temps quasi réel, sans provoquer de retard important entre la capture d'un paquet suspect et la génération de l'alerte correspondante. |
| **Sécurité** | L'accès au système doit être protégé par une authentification. Les données sensibles (mots de passe notamment) ne doivent jamais être manipulées ou stockées en clair. |
| **Disponibilité** | Le système doit pouvoir fonctionner de manière continue, afin d'assurer une surveillance ininterrompue du réseau. |
| **Fiabilité** | Le système doit limiter autant que possible les fausses alertes tout en évitant de manquer les menaces qu'il est censé détecter. |
| **Maintenabilité** | Le système doit être organisé en modules clairement séparés, afin de faciliter sa compréhension, sa correction et son évolution par une équipe restreinte. |
| **Évolutivité** | Le système doit pouvoir accueillir de nouvelles règles de détection ou de nouveaux types de menaces sans remettre en cause son fonctionnement global. |
| **Simplicité** | Le système doit rester compréhensible et utilisable sans nécessiter une expertise poussée en sécurité informatique. |
| **Portabilité** | Le système doit pouvoir être installé et exécuté sur différents environnements, notamment des environnements Linux. |

---

## 5. Profils utilisateurs

### 5.1 Administrateur

- **Rôle** : responsable global du bon fonctionnement du système.
- **Responsabilités** : superviser le système, gérer les comptes utilisateurs, configurer les paramètres généraux.
- **Permissions** : accès complet à l'ensemble des fonctionnalités, y compris la gestion des utilisateurs et des règles.

### 5.2 Analyste sécurité

- **Rôle** : utilisateur technique chargé de l'analyse des alertes et des menaces.
- **Responsabilités** : consulter et qualifier les alertes, investiguer les journaux d'événements, proposer des ajustements aux règles de détection.
- **Permissions** : consultation complète des alertes, des journaux et des statistiques ; gestion des règles de détection ; pas d'accès à la gestion des comptes utilisateurs.

### 5.3 Utilisateur en lecture seule

- **Rôle** : utilisateur non technique souhaitant suivre l'état général de la sécurité réseau (par exemple, un responsable ou un observateur).
- **Responsabilités** : consulter les informations mises à disposition, sans intervenir sur le système.
- **Permissions** : consultation des alertes et des statistiques uniquement, sans aucune action de modification.

### 5.4 Tableau récapitulatif des permissions

| Fonctionnalité | Administrateur | Analyste sécurité | Lecture seule |
|---|:---:|:---:|:---:|
| Consulter les alertes | ✔ | ✔ | ✔ |
| Consulter les journaux | ✔ | ✔ | ✘ |
| Consulter les statistiques | ✔ | ✔ | ✔ |
| Gérer les règles de détection | ✔ | ✔ | ✘ |
| Gérer les utilisateurs | ✔ | ✘ | ✘ |

---

## 6. Cas d'utilisation

### UC1 — Authentification

- **Description** : un utilisateur s'authentifie afin d'accéder au système selon son profil.
- **Acteur** : Administrateur, Analyste sécurité, Utilisateur en lecture seule.
- **Préconditions** : l'utilisateur possède un compte actif.
- **Scénario principal** :
  1. L'utilisateur accède à la page de connexion.
  2. Il saisit ses identifiants.
  3. Le système vérifie les identifiants.
  4. Le système ouvre une session correspondant au profil de l'utilisateur.
- **Résultat attendu** : l'utilisateur accède à l'interface avec les droits associés à son profil.

### UC2 — Visualiser les alertes

- **Description** : consulter la liste des alertes générées par le système.
- **Acteur** : Administrateur, Analyste sécurité, Utilisateur en lecture seule.
- **Préconditions** : l'utilisateur est authentifié.
- **Scénario principal** :
  1. L'utilisateur accède au tableau des alertes.
  2. Le système affiche les alertes existantes, triées par date et par gravité.
- **Résultat attendu** : l'utilisateur dispose d'une vue à jour des menaces détectées.

### UC3 — Configurer une règle de détection

- **Description** : créer, modifier ou désactiver une règle utilisée par le système de détection.
- **Acteur** : Administrateur, Analyste sécurité.
- **Préconditions** : l'utilisateur dispose des droits nécessaires.
- **Scénario principal** :
  1. L'utilisateur accède à la gestion des règles.
  2. Il crée ou modifie une règle (condition, seuil, gravité).
  3. Le système enregistre la règle.
- **Résultat attendu** : le comportement de détection du système est mis à jour.

### UC4 — Consulter les journaux

- **Description** : rechercher et consulter l'historique des événements enregistrés.
- **Acteur** : Administrateur, Analyste sécurité.
- **Préconditions** : l'utilisateur est authentifié.
- **Scénario principal** :
  1. L'utilisateur accède au module de journalisation.
  2. Il applique un filtre (date, adresse IP, type d'événement).
  3. Le système affiche les événements correspondants.
- **Résultat attendu** : l'utilisateur peut retracer une activité passée.

### UC5 — Consulter les statistiques

- **Description** : consulter une synthèse de l'activité réseau et des alertes.
- **Acteur** : Administrateur, Analyste sécurité, Utilisateur en lecture seule.
- **Préconditions** : l'utilisateur est authentifié.
- **Scénario principal** :
  1. L'utilisateur accède au tableau de bord statistique.
  2. Le système présente une synthèse des alertes et du trafic observé.
- **Résultat attendu** : l'utilisateur obtient une vision d'ensemble de l'état de sécurité du réseau.

### UC6 — Gérer les utilisateurs

- **Description** : créer, modifier ou supprimer un compte utilisateur.
- **Acteur** : Administrateur.
- **Préconditions** : l'utilisateur est authentifié en tant qu'administrateur.
- **Scénario principal** :
  1. L'administrateur accède à la gestion des comptes.
  2. Il crée, modifie ou désactive un compte.
- **Résultat attendu** : la liste des comptes utilisateurs est mise à jour.

### UC7 — Détecter une menace et générer une alerte

- **Description** : le système identifie un comportement correspondant à une règle de détection et génère une alerte.
- **Acteur** : Système (déclenchement automatique).
- **Préconditions** : au moins une règle de détection active correspond au trafic observé.
- **Scénario principal** :
  1. Le système analyse le trafic capturé.
  2. Il identifie une correspondance avec une règle de détection.
  3. Une alerte est générée et enregistrée.
- **Résultat attendu** : une alerte exploitable est disponible pour consultation.

---

## 7. Menaces à détecter

### 7.1 Port Scan (balayage de ports)

| Aspect | Détail |
|---|---|
| **Description** | Tentative d'identification des ports ouverts sur une machine cible. |
| **Principe** | Envoi de requêtes vers une plage de ports afin d'observer les réponses obtenues. |
| **Impact** | Phase de reconnaissance précédant souvent une attaque plus ciblée. |
| **Méthode générale de détection** | Comptage du nombre de ports distincts sollicités par une même source sur une courte période. |
| **Niveau de gravité** | Moyen |

### 7.2 SYN Flood

| Aspect | Détail |
|---|---|
| **Description** | Attaque par saturation exploitant l'établissement de connexions TCP. |
| **Principe** | Envoi massif de requêtes de connexion (TCP SYN) sans finalisation, saturant les ressources de la cible. |
| **Impact** | Indisponibilité du service visé. |
| **Méthode générale de détection** | Surveillance d'un volume anormalement élevé de requêtes de connexion en provenance d'une même source. |
| **Niveau de gravité** | Élevé |

### 7.3 ICMP Flood

| Aspect | Détail |
|---|---|
| **Description** | Attaque par saturation basée sur l'envoi massif de requêtes ICMP (ping). |
| **Principe** | Génération d'un volume élevé de requêtes ICMP afin de saturer les ressources réseau de la cible. |
| **Impact** | Dégradation ou indisponibilité du réseau ou du système visé. |
| **Méthode générale de détection** | Surveillance du nombre de requêtes ICMP reçues par unité de temps. |
| **Niveau de gravité** | Moyen à élevé |

### 7.4 Brute Force

| Aspect | Détail |
|---|---|
| **Description** | Tentative de découverte d'identifiants valides par essais successifs. |
| **Principe** | Envoi répété de tentatives d'authentification avec des combinaisons différentes d'identifiants. |
| **Impact** | Compromission possible d'un compte ou d'un service. |
| **Méthode générale de détection** | Comptage des échecs d'authentification consécutifs pour une même source ou une même cible. |
| **Niveau de gravité** | Élevé |

### 7.5 Tentatives répétées de connexion

| Aspect | Détail |
|---|---|
| **Description** | Multiplication anormale de tentatives de connexion vers un ou plusieurs services. |
| **Principe** | Une même source initie un nombre inhabituel de connexions en peu de temps. |
| **Impact** | Peut indiquer une reconnaissance active ou une tentative d'exploitation automatisée. |
| **Méthode générale de détection** | Analyse de la fréquence des connexions par source sur une période donnée. |
| **Niveau de gravité** | Moyen |

### 7.6 Communication avec une IP blacklistée

| Aspect | Détail |
|---|---|
| **Description** | Échange de trafic avec une adresse IP répertoriée comme malveillante. |
| **Principe** | Comparaison des adresses observées dans le trafic avec une liste noire connue. |
| **Impact** | Peut signaler une compromission interne ou une tentative d'intrusion connue. |
| **Méthode générale de détection** | Correspondance directe entre les adresses observées et une liste noire de référence. |
| **Niveau de gravité** | Élevé |

### 7.7 Utilisation de ports interdits

| Aspect | Détail |
|---|---|
| **Description** | Utilisation d'un port réseau non autorisé par la politique de sécurité de l'organisation. |
| **Principe** | Détection de trafic à destination ou en provenance d'un port figurant sur une liste de ports interdits. |
| **Impact** | Peut indiquer un service non autorisé ou un usage non conforme. |
| **Méthode générale de détection** | Comparaison du port utilisé avec une liste de ports interdits configurée. |
| **Niveau de gravité** | Moyen |

### 7.8 Activité réseau inhabituelle

| Aspect | Détail |
|---|---|
| **Description** | Comportement s'écartant du profil habituel d'un utilisateur, d'une machine ou d'un service. |
| **Principe** | Comparaison de l'activité observée avec une référence de comportement considéré comme normal. |
| **Impact** | Peut révéler une compromission ou un usage détourné. |
| **Méthode générale de détection** | Analyse comparative entre l'activité courante et un profil de référence. |
| **Niveau de gravité** | Variable (moyen à élevé) |

### 7.9 Détection de trafic anormal simple

| Aspect | Détail |
|---|---|
| **Description** | Variation simple et mesurable du volume ou de la nature du trafic réseau. |
| **Principe** | Repérage de pics de volumétrie ou de flux inhabituels par rapport à une moyenne de référence. |
| **Impact** | Peut précéder ou accompagner une attaque. |
| **Méthode générale de détection** | Comparaison de la volumétrie courante avec des seuils simples définis à l'avance. |
| **Niveau de gravité** | Moyen |

### 7.10 Synthèse des gravités

| Menace | Gravité |
|---|:---:|
| Port Scan | Moyen |
| SYN Flood | Élevé |
| ICMP Flood | Moyen à élevé |
| Brute Force | Élevé |
| Tentatives répétées de connexion | Moyen |
| IP blacklistée | Élevé |
| Ports interdits | Moyen |
| Activité réseau inhabituelle | Moyen à élevé |
| Trafic anormal simple | Moyen |

---

## 8. Contraintes techniques

Les contraintes techniques suivantes constituent le cadre général envisagé pour le projet. Elles ne font l'objet d'aucune explicitation d'implémentation à ce stade, celle-ci relevant des livrables suivants.

| Composant | Contrainte |
|---|---|
| Langage backend | Python |
| Framework API | FastAPI |
| Capture réseau | Scapy |
| Base de données | PostgreSQL |
| Interface Web | React |
| Conteneurisation | Docker |
| Système d'exploitation cible | Linux |

---

## 9. Architecture fonctionnelle

Les modules fonctionnels suivants sont envisagés pour le système, sans entrer dans le détail technique de leur réalisation :

- **Capture réseau** : écoute du trafic circulant sur le réseau surveillé.
- **Analyse** : traitement du trafic capturé afin d'en extraire des indicateurs exploitables.
- **Détection** : évaluation des indicateurs au regard des règles de détection définies.
- **Gestion des alertes** : centralisation et suivi des alertes générées.
- **Journalisation** : enregistrement durable des événements observés.
- **Authentification** : gestion des utilisateurs et de leurs accès au système.
- **API** : point d'échange structuré entre les différents modules et l'interface web.
- **Interface Web** : consultation des alertes, des journaux, des statistiques et gestion des règles/utilisateurs.
- **Base de données** : conservation des informations relatives aux utilisateurs, alertes, journaux, règles et statistiques.

---

## 10. Données manipulées

Les entités métier suivantes seront manipulées par le système. Seul leur rôle est présenté ici ; leur structuration détaillée relève d'un livrable ultérieur.

| Entité | Rôle |
|---|---|
| **Utilisateur** | Représente une personne disposant d'un accès au système, avec un profil déterminant ses permissions. |
| **Alerte** | Représente une détection positive, associée à un type de menace, une gravité et un statut de traitement. |
| **Journal** | Représente un événement réseau observé, qu'il ait ou non donné lieu à une alerte. |
| **Règle** | Représente une condition de détection définie pour identifier un type de menace donné. |
| **Statistique** | Représente une synthèse agrégée de l'activité réseau et des alertes sur une période donnée. |

---

## 11. Diagramme fonctionnel

```
                 ┌───────────────────────────┐
                 │   Réseau du CCM (trafic)   │
                 └─────────────┬─────────────┘
                                │
                                ▼
                 ┌───────────────────────────┐
                 │      Capture réseau        │
                 └─────────────┬─────────────┘
                                │
                                ▼
                 ┌───────────────────────────┐
                 │          Analyse           │
                 └─────────────┬─────────────┘
                                │
                                ▼
                 ┌───────────────────────────┐
                 │          Détection         │◄──────┐
                 └─────────────┬─────────────┘        │
                                │                       │ règles
                                ▼                       │
                 ┌───────────────────────────┐         │
                 │   Gestion des alertes      │         │
                 └───────┬───────────┬───────┘         │
                         │           │                  │
             alertes     │           │ tous événements  │
                         ▼           ▼                  │
             ┌───────────────┐ ┌───────────────────┐    │
             │ Base de données│◄│  Journalisation    │    │
             └───────┬───────┘ └───────────────────┘    │
                     │                                    │
                     ▼                                    │
             ┌───────────────────────────┐                │
             │            API             │────────────────┘
             └─────────────┬─────────────┘
                            │
                            ▼
             ┌───────────────────────────┐      ┌────────────────────┐
             │       Interface Web        │◄────►│   Authentification  │
             └─────────────┬─────────────┘      └────────────────────┘
                            │
                            ▼
             ┌───────────────────────────┐
             │  Utilisateurs (Admin,      │
             │  Analyste, Lecture seule)  │
             └───────────────────────────┘
```

---

## 12. Critères de réussite

- Le système est capable de capturer et d'analyser le trafic réseau sur au moins une interface, de manière continue.
- Chacune des neuf menaces listées en section 7 est détectée par au moins une règle fonctionnelle.
- Chaque détection positive génère une alerte correctement horodatée et enregistrée.
- Les trois profils utilisateurs disposent d'un accès conforme au tableau de permissions défini en section 5.
- Les journaux et les alertes sont consultables via une interface dédiée.
- Une synthèse statistique de l'activité réseau et des alertes est disponible.
- La gestion des règles de détection est opérationnelle (création, modification, désactivation).
- Le présent cahier des charges est validé avant le démarrage des livrables suivants (conception, architecture, implémentation).

---

## 13. Limites du projet

Dans le cadre de cette première version, les éléments suivants sont explicitement **hors périmètre** :

- **Aucune fonction de blocage automatique du trafic** : le système détecte et alerte, il n'intervient pas sur le réseau (fonction IPS non traitée).
- **Aucune inspection du trafic chiffré** : seules les métadonnées de flux sont exploitées.
- **Aucun mécanisme de Machine Learning** : la détection repose uniquement sur des règles et des seuils configurés.
- **Aucune haute disponibilité ni redondance** : le système est conçu pour un déploiement unique et simple.
- **Aucune intégration avec un SIEM externe.**
- **Aucun système de notification externe** (email, Telegram, SMS) dans cette version.
- **Aucune supervision multi-sites.**
- **Aucune conception détaillée de l'architecture technique, de l'API ou de la base de données** : ces éléments relèvent des livrables suivants et ne sont pas traités dans ce document.

---

## 14. Évolutions futures

- **Détection comportementale** avancée, au-delà des règles simples.
- **Machine Learning** appliqué à la détection d'anomalies.
- **Intégration avec un SIEM** pour une gestion centralisée des événements de sécurité.
- **Notifications par e-mail** pour les alertes critiques.
- **Notifications via Telegram** pour une réactivité accrue.
- **Tableau de bord temps réel** avec mise à jour en direct.
- **Export des rapports au format PDF.**
- **Export des données au format Excel.**
- **Géolocalisation des adresses IP** impliquées dans les alertes.

---

## 15. Questions ouvertes

Les points suivants devront être clarifiés et validés avec les parties prenantes du CCM avant le démarrage du développement :

1. **Périmètre réseau exact** : quel segment du réseau du CCM devra être surveillé en priorité ?
2. **Point de capture** : où et comment le trafic sera-t-il rendu accessible au système ?
3. **Volumétrie réelle** : quel est le débit réseau attendu, pour dimensionner correctement l'analyse ?
4. **Contraintes d'hébergement** : sur quelle infrastructure le système sera-t-il déployé ?
5. **Disponibilité des ressources humaines** : qui, au CCM, assurera le rôle d'administrateur et d'analyste une fois le système en fonctionnement ?
6. **Politique de conservation des données** : quelle durée de rétention appliquer aux journaux et aux alertes ?
7. **Source de la liste noire d'IP** : quelle référence utiliser pour identifier les adresses IP malveillantes connues ?
8. **Politique de ports autorisés** : quels ports et services sont considérés comme autorisés par le CCM ?
9. **Niveau d'automatisation attendu à terme** : le CCM envisage-t-il une évolution future vers un blocage automatique du trafic ?
10. **Processus de traitement des alertes** : quel circuit de suivi doit être appliqué selon le niveau de gravité d'une alerte ?
11. **Accès des utilisateurs en lecture seule** : ces utilisateurs doivent-ils pouvoir accéder au système depuis l'extérieur du réseau du CCM ?
12. **Calendrier et disponibilité** : quelles contraintes de temps s'appliquent au déroulement des prochains livrables du projet ?

---

*Fin du document — Livrable 1.*
