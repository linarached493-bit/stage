# Préparation de l'implémentation — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 8 — Préparation de l'implémentation
**Documents de référence :** l'ensemble des sept livrables précédents (Livrables 1 à 7)
**Statut :** Synthèse de fin de conception — aucune implémentation, aucun développement engagé

---

## 1. Objectif du document

### 1.1 Rôle de ce document

Ce document constitue la synthèse finale de la phase de conception du projet. Il rassemble, sous une forme consolidée, l'ensemble des décisions d'architecture déjà prises dans les sept livrables précédents, ainsi que l'ensemble des questions encore ouvertes qui doivent être tranchées avant de démarrer le développement. Il définit également les prérequis matériels et organisationnels, la stratégie d'implémentation, de validation et d'intégration, et une checklist finale conditionnant le passage à la phase de développement.

Ce document ne contient ni code, ni structure de projet, ni détail d'implémentation technique. Il s'agit d'un document de **clôture de la phase de conception** et de **préparation** de la phase suivante.

### 1.2 Lien avec les livrables précédents

Ce document ne redéfinit aucun élément de conception : il relit et consolide les sept livrables déjà produits (cahier des charges, spécifications techniques, conception UML, architecture logicielle, conception de la base de données, conception de l'API REST, plan de développement), afin de vérifier que l'ensemble forme un tout cohérent et prêt à être implémenté. Toute décision rappelée dans ce document renvoie explicitement au livrable qui l'a établie.

---

## 2. Synthèse des décisions d'architecture

| Domaine | Décision retenue | Livrable d'origine |
|---|---|---|
| Nature du système | IDS réseau (NIDS), fonctionnant en observation et alerte, sans blocage automatique du trafic. | Livrable 1 |
| Profils utilisateurs | Trois profils : Administrateur, Analyste sécurité, Utilisateur en lecture seule, avec matrice de permissions dédiée. | Livrable 1 |
| Menaces couvertes | Neuf menaces : Port Scan, SYN Flood, ICMP Flood, Brute Force, tentatives répétées de connexion, IP blacklistée, ports interdits, activité réseau inhabituelle, trafic anormal simple. | Livrable 1 |
| Choix technologiques | Python, FastAPI, Scapy, PostgreSQL, React, Docker, Linux. | Livrable 1 / Livrable 2 |
| Organisation modulaire | Dix modules fonctionnels : Capture réseau, Analyse, Détection, Gestion des alertes, Journalisation, Authentification, API Backend, Interface Web, Base de données, Configuration. | Livrable 2 / Livrable 4 |
| Flux de données | Chaîne linéaire Capture → Analyse → Détection → Gestion des alertes → Journalisation → Base de données ; Interface Web n'accédant qu'à l'API Backend, point d'accès unique du système. | Livrable 2 / Livrable 4 |
| Modèle de données | Huit entités : Utilisateur, Rôle, Alerte, Log, Règle, Statistique, Configuration, Liste noire ; relations et contraintes d'intégrité définies. | Livrable 5 |
| API REST | Huit ressources exposées sous un préfixe de version (`/v1`), authentification par session, autorisation par rôle centralisée au niveau de l'API Backend. | Livrable 6 |
| Gestion des erreurs | Isolation des défaillances entre modules, signalement explicite, dégradation progressive, refus explicite des accès non autorisés. | Livrable 2 / Livrable 4 / Livrable 6 |
| Sécurité | Authentification obligatoire, autorisation par rôle, protection des mots de passe, principe du moindre privilège, journalisation des actions sensibles. | Livrable 1 / Livrable 4 / Livrable 6 |
| Stratégie de développement | Développement incrémental en douze phases, construction de bas en haut (données → logique métier → API → interface), validation progressive. | Livrable 7 |
| Limites explicites de cette version | Pas de blocage automatique, pas de Machine Learning, pas de haute disponibilité, pas d'intégration SIEM, pas de notifications externes. | Livrable 1 / Livrable 4 |

---

## 3. Décisions restant à valider

Les tableaux suivants consolident, par thématique, l'ensemble des questions restées ouvertes dans les sept livrables précédents.

### 3.1 Réseau et capture

| Question | Origine | Impact | Décision recommandée | Priorité |
|---|---|---|---|---|
| Périmètre réseau exact à surveiller | Livrable 1 (Q1) | Élevé | À défaut de validation par le CCM, retenir un segment de test isolé et représentatif pour le développement et la démonstration. | Critique |
| Emplacement technique du point de capture | Livrable 1 (Q2), Livrable 2 (Q1) | Élevé | Retenir un mode d'écoute en miroir sur l'environnement de test si l'accès au réseau réel n'est pas disponible au moment du développement. | Critique |
| Volumétrie réelle attendue / montée en charge | Livrable 1 (Q3), Livrable 2 (Q5) | Moyen | Conserver les hypothèses de fonctionnement déjà posées (Livrable 2, section 9) et les ajuster lors des tests de validation. | Moyenne |

### 3.2 Déploiement et fonctionnement interne

| Question | Origine | Impact | Décision recommandée | Priorité |
|---|---|---|---|---|
| Environnement d'hébergement définitif (machine unique ou répartie) | Livrable 1 (Q4), Livrable 2 (Q8), Livrable 4 (section 6.2) | Élevé | Retenir un déploiement sur une seule machine Linux pour cette première version, conformément aux hypothèses déjà validées. | Haute |
| Mode d'exécution de l'Analyse et de la Détection (flux continu ou traitement par lots) | Livrable 2 (Q2) | Moyen | Retenir un traitement en flux continu, cohérent avec l'objectif de détection quasi temps réel du cahier des charges. | Haute |
| Mode de communication interne entre modules (synchrone ou asynchrone) | Livrable 2 (Q7) | Moyen | Retenir une communication asynchrone pour la chaîne de traitement du trafic, et synchrone pour les échanges API / Interface Web ; à confirmer lors de l'implémentation. | Moyenne |
| Format d'échange interne entre modules | Livrable 2 (Q10) | Faible | Décision sans impact sur la conception déjà validée ; à fixer librement lors de l'implémentation. | Faible |

### 3.3 Données et persistance

| Question | Origine | Impact | Décision recommandée | Priorité |
|---|---|---|---|---|
| Statut de persistance des statistiques (calculées à la demande ou stockées) | Livrable 2 (Q4), Livrable 3 (section 8.3), Livrable 5 (section 10.5), Livrable 6 (section 10.4) | Moyen | Retenir un calcul à la demande pour cette première version, plus simple à mettre en œuvre et cohérent avec le principe de simplicité du cahier des charges. | Haute |
| Politique de conservation des alertes, journaux, statistiques et configurations | Livrable 1 (Q6), Livrable 2 (Q6), Livrable 5 (section 7) | Moyen | Retenir une conservation complète pendant la durée du projet, sans purge automatique dans cette version ; réévaluer en cas de passage en production. | Moyenne |
| Modalités précises de sauvegarde | Livrable 5 (section 8) | Faible | Une sauvegarde manuelle ponctuelle est suffisante pour cette version pédagogique. | Faible |
| Granularité de l'entité Règle par type de menace | Livrable 3 (section 8.3) | Moyen | Conserver une structure générique unique et paramétrable, sans sous-classification par menace, conformément au principe d'évolutivité déjà retenu. | Haute |
| Écart entité Rôle / attribut « profil » entre la conception UML et la conception de la base de données | Livrable 5 (section 10.5) | Faible | Retenir l'entité Rôle telle que définie dans la conception de la base de données ; l'ajustement du diagramme de classes est documentaire et non bloquant pour le développement. | Moyenne |
| Absence du module Configuration dans la conception UML d'origine | Livrable 4 (section 11.4) | Faible | Même traitement que le point précédent : ajustement documentaire non bloquant. | Faible |

### 3.4 Sécurité et accès

| Question | Origine | Impact | Décision recommandée | Priorité |
|---|---|---|---|---|
| Source et modalités de gestion de la liste noire d'IP | Livrable 1 (Q7) | Moyen | Démarrer avec une liste noire alimentée manuellement par les utilisateurs habilités ; envisager une source externe de renseignement dans une évolution future. | Moyenne |
| Politique de ports autorisés / interdits | Livrable 1 (Q8) | Moyen | Établir une liste initiale simple à valider avec le CCM, modifiable ultérieurement via la ressource Configuration. | Haute |
| Niveau d'automatisation attendu à terme (évolution vers un blocage de type IPS) | Livrable 1 (Q9) | Faible (pour cette version) | Confirmer que cette version reste strictement en observation, sans blocage automatique, conformément aux limites déjà actées. | Faible |
| Seuils de protection contre les abus d'authentification | Livrable 6 (section 8) | Moyen | Retenir un seuil simple de tentatives sur une courte période pour cette version, ajustable ultérieurement. | Haute |
| Durée de validité d'une session utilisateur | Livrable 2 (Q9) | Faible | Retenir une durée de session modérée adaptée à un usage interne ; à confirmer avant l'implémentation de l'Authentification. | Moyenne |
| Accès du profil Lecture seule aux journaux (incohérence relevée entre le cahier des charges et la conception UML) | Livrable 6 (section 10.4) | Moyen | Trancher en faveur de l'absence d'accès (position la plus restrictive, conforme au principe du moindre privilège), à confirmer avec le CCM. | Haute |
| Permissions précises sur les ressources Configuration et Liste noire | Livrable 6 (section 10.4) | Moyen | Confirmer l'attribution déjà proposée : Configuration réservée à l'Administrateur ; Liste noire ouverte à l'Administrateur et à l'Analyste sécurité. | Haute |
| Accès des utilisateurs en lecture seule depuis l'extérieur du réseau du CCM | Livrable 1 (Q11) | Faible | Restreindre l'accès au réseau interne pour cette première version, par prudence. | Faible |

### 3.5 Organisation du projet

| Question | Origine | Impact | Décision recommandée | Priorité |
|---|---|---|---|---|
| Disponibilité des ressources humaines pour les rôles Administrateur et Analyste sécurité | Livrable 1 (Q5) | Organisationnel | À clarifier avec le CCM ; sans impact direct sur la conception technique déjà validée. | Moyenne |
| Processus de gestion et d'escalade des alertes selon leur gravité | Livrable 1 (Q10) | Moyen | Hors périmètre technique de cette version (aucune notification automatique) ; processus organisationnel à définir par le CCM indépendamment du développement. | Faible |
| Calendrier et disponibilité pour la suite du projet | Livrable 1 (Q12) | Organisationnel | À confronter avec l'ordre d'implémentation recommandé (Livrable 7, section 5) avant le démarrage du développement. | Moyenne |

---

## 4. Prérequis avant développement

### 4.1 Environnement de développement

- Poste de développement disposant d'un système compatible avec l'environnement conteneurisé cible (Linux ou environnement équivalent).
- Outil de conteneurisation opérationnel, permettant de reproduire l'environnement de déploiement prévu.
- Éditeur ou environnement de développement adapté aux langages retenus (Python, JavaScript/React).

### 4.2 Outils

- Outil de gestion de version, avec un dépôt initialisé et accessible.
- Outil d'exécution et de suivi des tests, cohérent avec les niveaux de test définis dans le plan de développement.
- Outil de suivi des tâches, reprenant le découpage en phases et tâches du plan de développement (Livrable 7).

### 4.3 Dépendances

- Disponibilité confirmée des bibliothèques et frameworks retenus (Python, FastAPI, Scapy, React) dans les versions compatibles avec l'environnement cible.
- Disponibilité du système de gestion de base de données retenu (PostgreSQL).

### 4.4 Accès réseau

- Confirmation du segment réseau à surveiller, ou mise à disposition d'un environnement réseau de test isolé permettant de simuler les neuf menaces à détecter.
- Droits d'accès nécessaires à l'écoute du trafic (accès à l'interface réseau en mode d'observation).

### 4.5 Accès à la base de données

- Instance de base de données accessible depuis l'environnement de développement.
- Droits de création et de modification de la structure de données nécessaires à la phase « Base de données » du plan de développement.

### 4.6 Jeux de données

- Jeu de données de référence initial (rôles reconnus, comptes de test pour chaque profil utilisateur).
- Jeu de trafic ou de scénarios simulant chacune des neuf menaces à détecter, nécessaire à la validation du moteur de détection.

### 4.7 Environnement de test

- Environnement distinct de l'environnement de développement courant, permettant l'exécution des tests d'intégration, fonctionnels et de validation sans risque pour un environnement de production existant.
- Accès à un trafic ou à un environnement réseau contrôlé, permettant de rejouer les scénarios de menace de façon reproductible.

Aucune modalité d'installation ou de configuration détaillée de ces éléments n'est décrite dans ce document ; seule leur disponibilité est requise avant le démarrage du développement.

---

## 5. Stratégie d'implémentation

L'ordre de développement recommandé, déjà établi en section 5 du plan de développement (Livrable 7), est confirmé et rappelé ici :

1. **Initialisation du projet** — met en place les fondations nécessaires à toute activité de développement.
2. **Base de données** — l'ensemble des modules applicatifs dépend, directement ou indirectement, de la persistance des données.
3. **Backend** — nécessaire pour exposer la base de données aux modules métier.
4. **Authentification** et **Capture réseau**, développées en parallèle — ces deux modules ne dépendent l'un de l'autre pour aucune donnée ni aucun comportement, ce qui permet d'optimiser le temps disponible.
5. **Moteur de détection** — ne peut être construit qu'une fois la Capture réseau et la Base de données disponibles, puisqu'il dépend des indicateurs et des règles qu'elles fournissent.
6. **API REST** — expose les données et fonctionnalités déjà rendues disponibles par l'Authentification, le Moteur de détection et le Backend.
7. **Interface Web** — ne peut être développée de façon pertinente qu'une fois l'API REST disponible, celle-ci constituant son unique point d'accès.
8. **Intégration, Tests, Documentation, Préparation de la démonstration** — clôturent le développement en assemblant, vérifiant et présentant le système complet.

Cette stratégie privilégie une construction progressive **de bas en haut** : les fondations (données, logique métier) sont construites avant les couches d'exposition (API) et de présentation (interface), ce qui limite le risque de devoir remettre en cause un module déjà achevé et permet de disposer, à chaque étape, d'un sous-ensemble du système vérifiable de façon autonome.

---

## 6. Stratégie de validation

Chaque module est validé avant que le développement ne se poursuive sur les modules qui en dépendent, selon les principes suivants :

| Étape de validation | Critère de passage au module suivant |
|---|---|
| Validation de conformité à la mission du module | Le module réalise effectivement la mission et les responsabilités qui lui ont été assignées dans l'architecture logicielle (Livrable 4), sans écart non justifié. |
| Validation par les tests unitaires | Le comportement interne du module est vérifié de façon isolée, conformément au niveau de test « unitaire » défini dans le plan de développement (Livrable 7, section 6). |
| Validation des échanges avec les modules dépendants | Les données produites ou consommées par le module correspondent au flux de données déjà défini (spécifications techniques, section 4 ; architecture logicielle, section 5). |
| Validation au regard des critères de phase | Le module satisfait au critère de validation défini pour sa phase dans le plan de développement (Livrable 7, section 8), avant que la phase suivante ne débute. |

Un module n'est considéré comme prêt à être intégré que lorsque ces quatre niveaux de validation sont satisfaits ; un module non conforme à sa mission ou à ses échanges attendus doit être corrigé avant toute poursuite du développement sur les modules qui en dépendent.

---

## 7. Stratégie d'intégration

L'assemblage progressif des modules suit les étapes suivantes, cohérentes avec la phase « Intégration » du plan de développement (Livrable 7, section 4.9) :

1. **Intégration de la chaîne de traitement du trafic** : assemblage de la Capture réseau, de l'Analyse, du Moteur de détection, de la Gestion des alertes et de la Journalisation, afin de vérifier qu'un événement réseau observé produit correctement une alerte journalisée.
2. **Intégration de l'API Backend avec les modules internes** : vérification que l'API Backend accède correctement à l'Authentification, à la Base de données, à la Gestion des alertes, à la Journalisation et à la Configuration.
3. **Intégration de l'Interface Web avec l'API Backend** : assemblage complet dans l'environnement conteneurisé cible, afin de vérifier que chaque cas d'utilisation du cahier des charges est réalisable de bout en bout.
4. **Vérification de bout en bout sur les neuf menaces** : rejeu de scénarios représentatifs de chacune des neuf menaces définies dans le cahier des charges, afin de confirmer que le système intégré détecte, alerte et restitue correctement chaque cas.

Cette progression garantit que l'intégration ne porte jamais, en une seule fois, sur l'ensemble du système : chaque étape ajoute un niveau supplémentaire (traitement interne, puis exposition, puis présentation), ce qui facilite l'identification de l'origine d'un éventuel dysfonctionnement.

---

## 8. Critères de préparation

Avant le démarrage effectif du développement, les éléments suivants doivent être vérifiés :

- [ ] Les sept livrables précédents sont formellement validés et aucun n'est en attente de modification.
- [ ] Chacune des questions consolidées en section 3 de ce document a reçu une décision explicite (validation du CCM ou hypothèse de travail assumée).
- [ ] Les prérequis listés en section 4 (environnement, outils, dépendances, accès réseau, accès base de données, jeux de données, environnement de test) sont réunis.
- [ ] L'ordre d'implémentation recommandé (section 5) est partagé et accepté par les parties prenantes du projet.
- [ ] Les critères de validation par module (section 6) et les étapes d'intégration (section 7) sont compris et acceptés comme cadre de travail.
- [ ] Le calendrier disponible pour le développement a été confronté à l'ampleur du plan de développement (Livrable 7).
- [ ] Un premier scénario de démonstration cible (menaces représentatives à couvrir en priorité) est identifié, même de façon provisoire.

---

## 9. Conclusion

La phase de conception du projet d'IDS destiné au Centre Cinématographique Marocain est arrivée à son terme. Les huit dimensions du système ont été traitées de façon progressive et cohérente : le besoin (cahier des charges), la spécification technique, la conception UML, l'architecture logicielle, la conception de la base de données, la conception de l'API REST, le plan de développement, et enfin la présente synthèse de préparation.

Chaque livrable s'est appuyé sur les précédents sans les remettre en cause, tout en signalant de façon transparente les écarts, ajustements et questions restées ouvertes plutôt que de les masquer. Ces points, consolidés en section 3, ne remettent pas en cause la cohérence globale de la conception : ils représentent des décisions de détail ou de confirmation restant à obtenir, principalement auprès du CCM, avant ou pendant le développement.

**Le projet est prêt à entrer en phase d'implémentation (Livrable 8 bis / développement), sous réserve de la validation des points encore ouverts listés en section 3 et de la réunion des prérequis énumérés en section 4.** Aucune ligne de code n'a été produite à ce stade, conformément au périmètre de ce livrable ; le développement pourra débuter dès que les critères de préparation énoncés en section 8 seront satisfaits.

---

*Fin du document — Livrable 8.*
