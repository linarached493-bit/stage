# Conception de la base de données — IDS pour le Centre Cinématographique Marocain (CCM)

**Version :** 1.0
**Date :** 03/08/2026
**Livrable :** Livrable 5 — Conception de la base de données
**Documents de référence :** `docs/cahier_des_charges.md` (Livrable 1), `docs/specifications_techniques.md` (Livrable 2), `docs/conception_uml.md` (Livrable 3), `docs/architecture_logicielle.md` (Livrable 4)
**Statut :** Conception de données — aucun SQL, aucune implémentation

---

## 1. Objectif du document

### 1.1 Rôle de la base de données

Ce document a pour objectif de définir la structure logique des données manipulées par le système, en cohérence avec l'ensemble des livrables déjà validés. La base de données constitue le support de persistance unique du système : elle conserve les comptes utilisateurs, les alertes, les journaux d'événements, les règles de détection, les statistiques, les paramètres de configuration et la liste noire d'adresses IP, conformément au module « Base de données » décrit en section 4.9 de l'architecture logicielle.

Ce document reste au niveau **conceptuel et logique** : il décrit les entités, leurs informations et leurs relations, sans recourir à un langage de définition de données (aucun SQL), sans script de migration, et sans type technique de base de données (aucun VARCHAR, INT, ni équivalent).

### 1.2 Lien avec les livrables précédents

- Le **cahier des charges** (section 10) a identifié les entités métier de base : Utilisateur, Alerte, Log, Règle, Statistique.
- Les **spécifications techniques** ont retenu PostgreSQL comme système de gestion de base de données et ont défini le module « Base de données » comme point de persistance central (section 3.8).
- La **conception UML** a représenté ces entités sous forme de classes (Utilisateur, Alerte, Log, Règle, Statistique) avec leurs attributs et leurs relations principales.
- L'**architecture logicielle** a introduit le module « Configuration », regroupant explicitement les règles, seuils, listes noires et paramètres généraux (section 4.10), ce qui justifie l'introduction, dans ce livrable, des entités **Configuration** et **Liste noire** comme entités de données à part entière.
- Ce document introduit également l'entité **Rôle**, qui n'était représentée dans la conception UML que sous la forme d'un attribut « profil » de la classe Utilisateur. Cette évolution est motivée par une exigence de conception de données classique (éviter les valeurs répétées, garantir la cohérence des profils) et est signalée comme un ajustement en section 10 de ce document.

Aucun document précédent n'est modifié par ce livrable.

---

## 2. Choix du SGBD

### 2.1 SGBD retenu

PostgreSQL est confirmé comme système de gestion de base de données relationnelle pour ce projet, conformément au choix déjà annoncé en section 8 du cahier des charges et en section 5 des spécifications techniques.

### 2.2 Justification

- **Nature relationnelle des données** : les entités manipulées par le système (utilisateurs, alertes, règles, journaux) entretiennent des relations claires et structurées (un utilisateur qualifie des alertes, une règle déclenche des alertes, une alerte peut s'appuyer sur des entrées de journal), ce qui correspond naturellement au modèle relationnel.
- **Intégrité référentielle native** : PostgreSQL permet d'imposer nativement des contraintes de cohérence entre entités (unicité, références obligatoires), ce qui est essentiel pour un système où la fiabilité des alertes et des journaux conditionne la confiance accordée au système.
- **Robustesse et maturité** : PostgreSQL est un système éprouvé, largement documenté, avec une gestion transactionnelle fiable, adaptée à un système devant garantir qu'aucune alerte ni aucun événement ne soit perdu lors de son enregistrement.
- **Flexibilité pour les données semi-structurées** : les conditions de déclenchement des règles de détection peuvent nécessiter une représentation flexible (seuils, motifs, références à une liste), que PostgreSQL sait accueillir sans remettre en cause son modèle relationnel global.
- **Cohérence avec l'écosystème technique retenu** : PostgreSQL s'intègre naturellement avec les autres choix technologiques déjà validés (Python, FastAPI, Docker).

### 2.3 Avantages pour ce projet

- Garantit la cohérence des données entre les alertes, les journaux, les règles et les utilisateurs grâce aux contraintes d'intégrité référentielle.
- Permet une évolution progressive du schéma de données à mesure que de nouvelles règles ou de nouveaux types d'alertes sont introduits.
- Offre une base solide pour les futurs besoins statistiques (agrégations, comptages, filtrages par période).

### 2.4 Limites pour ce projet

- Nécessite une administration minimale (sauvegardes, gestion des accès) qui doit être assurée, même dans un cadre pédagogique.
- N'est pas nativement optimisé pour des volumes très importants de données de type séries temporelles à très haute fréquence ; ce point reste toutefois cohérent avec le périmètre pédagogique et les volumes attendus, conformément aux hypothèses de fonctionnement déjà posées dans les spécifications techniques.
- Une utilisation non maîtrisée du modèle relationnel (absence d'index pertinents, requêtes non optimisées) pourrait limiter les performances à mesure que le volume de journaux augmente ; ce point relève de la conception détaillée et de l'implémentation, hors périmètre de ce document.

---

## 3. Entités du système

### 3.1 Utilisateur

- **Rôle** : représente une personne disposant d'un accès au système.
- **Description** : chaque utilisateur est rattaché à un rôle déterminant ses permissions, conformément à la matrice définie dans le cahier des charges.
- **Informations principales stockées** : identité de connexion, mot de passe protégé, rôle associé, statut du compte, historique de connexion.

### 3.2 Rôle

- **Rôle** : représente un profil d'utilisateur et l'ensemble des permissions qui lui sont associées (Administrateur, Analyste sécurité, Utilisateur en lecture seule).
- **Description** : cette entité évite de répéter les libellés de profil pour chaque utilisateur et centralise la définition des profils reconnus par le système.
- **Informations principales stockées** : nom du profil, description du profil.

### 3.3 Alerte

- **Rôle** : représente une détection positive produite par le module de détection.
- **Description** : chaque alerte est rattachée à la règle qui l'a déclenchée et suit un cycle de traitement (nouvelle, en cours, traitée, faux positif), conformément au cas d'utilisation UC8 du cahier des charges.
- **Informations principales stockées** : règle d'origine, type de menace, adresses concernées, gravité, horodatage, statut de traitement, utilisateur ayant qualifié l'alerte.

### 3.4 Log (journal d'événement)

- **Rôle** : représente un événement réseau observé, qu'il ait ou non donné lieu à une alerte.
- **Description** : constitue la trace exhaustive de l'activité réseau analysée par le système, à des fins d'investigation.
- **Informations principales stockées** : horodatage, type d'événement, adresses et ports concernés, protocole, référence éventuelle à une alerte associée.

### 3.5 Règle

- **Rôle** : représente une condition de détection utilisée par le moteur de détection pour identifier un type de menace donné.
- **Description** : chaque règle correspond à l'une des menaces définies en section 7 du cahier des charges, ou à toute nouvelle menace introduite ultérieurement.
- **Informations principales stockées** : nom, description, type de menace associé, condition de déclenchement, gravité associée, statut d'activation, auteur, dates de création et de modification.

### 3.6 Statistique

- **Rôle** : représente une synthèse agrégée de l'activité réseau et des alertes sur une période donnée.
- **Description** : alimente le tableau de bord statistique (cas d'utilisation UC5 du cahier des charges) à partir des données d'alertes et de journaux.
- **Informations principales stockées** : période considérée, volumétrie observée, répartition des alertes par type et par gravité, date de calcul.

### 3.7 Configuration

- **Rôle** : représente un paramètre général du système, distinct des règles de détection et de la liste noire.
- **Description** : correspond au module « Configuration » de l'architecture logicielle ; centralise les réglages globaux (par exemple l'interface réseau surveillée ou la fenêtre d'observation utilisée par l'analyse).
- **Informations principales stockées** : nom du paramètre, valeur associée, description, historique de modification.

### 3.8 Liste noire (IP blacklist)

- **Rôle** : représente une adresse IP identifiée comme malveillante, utilisée par la règle de détection correspondant à la menace « communication avec une IP blacklistée ».
- **Description** : constitue une liste de référence consultée par le moteur de détection ; alimentée et maintenue par les utilisateurs habilités.
- **Informations principales stockées** : adresse IP, motif ou source de l'ajout, date d'ajout, statut d'activation.

---

## 4. Relations entre les entités

### 4.1 Description des relations

| Relation | Cardinalité | Justification |
|---|---|---|
| Rôle → Utilisateur | 1 rôle pour 0 à n utilisateurs ; 1 utilisateur pour exactement 1 rôle | Chaque utilisateur doit être rattaché à un profil reconnu par le système ; un même profil s'applique à plusieurs utilisateurs. |
| Utilisateur (auteur) → Règle | 1 utilisateur pour 0 à n règles ; 1 règle pour exactement 1 utilisateur auteur | Chaque règle doit pouvoir être rattachée à l'utilisateur habilité qui l'a créée ou modifiée en dernier, conformément à l'exigence de traçabilité. |
| Règle → Alerte | 1 règle pour 0 à n alertes ; 1 alerte pour exactement 1 règle d'origine | Chaque alerte résulte de l'évaluation positive d'une règle précise ; une même règle peut déclencher plusieurs alertes au fil du temps. |
| Utilisateur (qualification) → Alerte | 1 utilisateur pour 0 à n alertes qualifiées ; 1 alerte pour 0 ou 1 utilisateur ayant qualifié son statut | Une alerte peut rester non qualifiée (statut « nouvelle ») ou être qualifiée par un unique utilisateur habilité. |
| Alerte → Log | 1 alerte pour 0 à n entrées de journal associées ; 1 entrée de journal pour 0 ou 1 alerte associée | Une alerte peut s'appuyer sur plusieurs événements journalisés comme éléments de preuve ; un événement journalisé n'est pas nécessairement lié à une alerte. |
| Configuration → Liste noire | 1 configuration pour 0 à n entrées de liste noire | La liste noire est gérée comme un ensemble de paramètres rattachés à la configuration générale du système, conformément au regroupement opéré par le module Configuration de l'architecture logicielle. |
| Alerte / Log → Statistique | Relation de calcul (agrégation), non une association relationnelle stricte | Les statistiques sont calculées à partir des alertes et des journaux existants ; elles ne constituent pas une référence directe et permanente vers des enregistrements précis, mais une synthèse recalculée sur une période donnée. |

### 4.2 Diagramme entité-association (ASCII)

```
┌───────────┐      1        0..n      ┌───────────────┐
│    Rôle      │──────────────────────►│   Utilisateur     │
└───────────┘                        └───────┬───────┘
                                              │ 1 (auteur)
                                              │
                                              ▼ 0..n
                                      ┌───────────────┐
                                      │      Règle         │
                                      └───────┬───────┘
                                              │ 1
                                              │
                                              ▼ 0..n
                                      ┌───────────────┐        0..1        0..n      ┌───────────────┐
                                      │      Alerte         │◄──────────────────────│   Utilisateur     │
                                      └───────┬───────┘        (qualifie)           └───────────────┘
                                              │ 1
                                              │
                                              ▼ 0..n
                                      ┌───────────────┐
                                      │        Log           │
                                      └───────────────┘

┌────────────────┐      1        0..n      ┌───────────────────┐
│  Configuration     │──────────────────────►│   Liste noire        │
└────────────────┘                        └───────────────────┘

┌───────────────┐   calcul / agrégation   ┌───────────────┐
│     Alerte         │◄────────────────────────│   Statistique      │
└───────────────┘                        └───────────────┘
┌───────────────┐   calcul / agrégation           ▲
│       Log           │─────────────────────────────────┘
└───────────────┘
```

---

## 5. Dictionnaire de données

### 5.1 Utilisateur

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique l'utilisateur | Obligatoire | Unique |
| Nom d'utilisateur | Nom utilisé pour la connexion | Obligatoire | Unique |
| Mot de passe protégé | Représentation protégée du mot de passe | Obligatoire | Ne doit jamais être stocké en clair |
| Rôle associé | Profil déterminant les permissions | Obligatoire | Doit référencer un rôle existant |
| Statut du compte | Indique si le compte est actif ou désactivé | Obligatoire | Valeur parmi un ensemble fermé (actif, désactivé) |
| Date de création | Date de création du compte | Obligatoire | — |
| Date de dernière connexion | Date de la dernière connexion réussie | Optionnel | — |

### 5.2 Rôle

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique le rôle | Obligatoire | Unique |
| Nom du rôle | Libellé du profil (Administrateur, Analyste sécurité, Lecture seule) | Obligatoire | Unique |
| Description | Explication du rôle et de son périmètre | Optionnel | — |

### 5.3 Alerte

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique l'alerte | Obligatoire | Unique |
| Règle d'origine | Règle ayant déclenché l'alerte | Obligatoire | Doit référencer une règle existante |
| Type de menace | Type de menace détecté, conservé au moment de la détection | Obligatoire | Doit correspondre à un type reconnu par le système |
| Adresse IP source | Adresse à l'origine du comportement détecté | Obligatoire | — |
| Adresse IP destination | Adresse visée par le comportement détecté | Optionnel | — |
| Port(s) concerné(s) | Port ou ports impliqués dans la détection | Optionnel | — |
| Gravité | Niveau de gravité associé à la détection | Obligatoire | Valeur parmi un ensemble fermé (ex. Moyen, Élevé) |
| Horodatage de détection | Date et heure de la détection | Obligatoire | — |
| Statut de traitement | État d'avancement du traitement de l'alerte | Obligatoire | Valeur parmi un ensemble fermé (nouvelle, en cours, traitée, faux positif) ; valeur initiale « nouvelle » |
| Utilisateur ayant qualifié | Utilisateur ayant modifié le statut de l'alerte | Optionnel | Doit référencer un utilisateur existant si renseigné |
| Date de dernière mise à jour du statut | Date du dernier changement de statut | Optionnel | — |

### 5.4 Log (journal d'événement)

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique l'entrée de journal | Obligatoire | Unique |
| Horodatage | Date et heure de l'événement observé | Obligatoire | — |
| Type d'événement | Nature de l'événement observé | Obligatoire | — |
| Adresse IP source | Adresse à l'origine de l'événement | Obligatoire | — |
| Adresse IP destination | Adresse visée par l'événement | Optionnel | — |
| Port(s) concerné(s) | Port ou ports impliqués | Optionnel | — |
| Protocole | Protocole réseau observé | Optionnel | — |
| Alerte associée | Alerte à laquelle l'événement est éventuellement rattaché | Optionnel | Doit référencer une alerte existante si renseigné |

### 5.5 Règle

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique la règle | Obligatoire | Unique |
| Nom | Nom de la règle | Obligatoire | Unique |
| Description | Explication de la règle | Optionnel | — |
| Type de menace associé | Menace que la règle permet de détecter | Obligatoire | Doit correspondre à une menace reconnue par le système |
| Condition de déclenchement | Description structurée de la condition (seuil, motif, référence à une liste) | Obligatoire | — |
| Gravité associée | Niveau de gravité attribué en cas de détection | Obligatoire | Valeur parmi un ensemble fermé |
| Statut | Indique si la règle est active ou inactive | Obligatoire | Valeur parmi un ensemble fermé (active, inactive) |
| Auteur | Utilisateur ayant créé ou modifié la règle en dernier | Obligatoire | Doit référencer un utilisateur existant |
| Date de création | Date de création de la règle | Obligatoire | — |
| Date de dernière modification | Date de la dernière modification | Optionnel | — |

### 5.6 Statistique

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique la synthèse statistique | Obligatoire | Unique |
| Période considérée (début) | Date de début de la période analysée | Obligatoire | — |
| Période considérée (fin) | Date de fin de la période analysée | Obligatoire | Doit être postérieure à la date de début |
| Volumétrie de trafic observée | Indicateur global du volume de trafic analysé sur la période | Obligatoire | — |
| Répartition des alertes par type | Nombre d'alertes observées par type de menace sur la période | Obligatoire | — |
| Répartition des alertes par gravité | Nombre d'alertes observées par niveau de gravité sur la période | Obligatoire | — |
| Date de calcul | Date à laquelle la synthèse a été produite | Obligatoire | — |

### 5.7 Configuration

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique le paramètre | Obligatoire | Unique |
| Nom du paramètre | Libellé identifiant le paramètre | Obligatoire | Unique |
| Valeur du paramètre | Valeur actuellement appliquée | Obligatoire | — |
| Description | Explication du rôle du paramètre | Optionnel | — |
| Utilisateur ayant modifié | Dernier utilisateur ayant modifié le paramètre | Optionnel | Doit référencer un utilisateur existant si renseigné |
| Date de dernière modification | Date de la dernière modification | Optionnel | — |

### 5.8 Liste noire (IP blacklist)

| Information | Description | Obligatoire / Optionnel | Contraintes fonctionnelles |
|---|---|---|---|
| Identifiant | Identifie de façon unique l'entrée de la liste noire | Obligatoire | Unique |
| Adresse IP | Adresse identifiée comme malveillante | Obligatoire | Unique |
| Motif / source | Raison de l'ajout ou origine du renseignement | Optionnel | — |
| Date d'ajout | Date d'ajout de l'adresse à la liste | Obligatoire | — |
| Statut | Indique si l'entrée est active ou inactive | Obligatoire | Valeur parmi un ensemble fermé (active, inactive) |

---

## 6. Règles d'intégrité

### 6.1 Unicité

- Le nom d'utilisateur, le nom de rôle, le nom de règle et le nom de paramètre de configuration doivent être uniques, afin d'éviter toute ambiguïté d'identification.
- Une même adresse IP ne peut figurer qu'une seule fois dans la liste noire, afin d'éviter les doublons de gestion.

### 6.2 Références entre entités

- Un utilisateur doit obligatoirement être rattaché à un rôle existant.
- Une règle doit obligatoirement être rattachée à un utilisateur auteur existant.
- Une alerte doit obligatoirement être rattachée à une règle d'origine existante.
- Une entrée de journal, si elle référence une alerte, doit référencer une alerte existante.
- L'utilisateur ayant qualifié une alerte ou modifié un paramètre de configuration, s'il est renseigné, doit correspondre à un utilisateur existant.

### 6.3 Suppression

- La suppression d'un rôle utilisé par au moins un utilisateur doit être interdite, ou conditionnée à la réattribution préalable des utilisateurs concernés à un autre rôle.
- La suppression d'une règle ayant déjà déclenché des alertes doit être évitée au profit d'une désactivation (changement de statut), afin de préserver l'intégrité historique des alertes déjà générées.
- La suppression d'un utilisateur ayant créé des règles ou qualifié des alertes doit être traitée avec précaution, afin de ne pas rompre la traçabilité historique ; une désactivation du compte est privilégiée par rapport à une suppression définitive.
- La suppression d'une entrée de journal ou d'une alerte ne doit pas être une opération courante, dans la mesure où ces données constituent la preuve de l'activité observée ; une politique de conservation encadre leur cycle de vie (voir section 7).

### 6.4 Mise à jour

- La modification d'une règle ne doit pas altérer rétroactivement les alertes déjà générées sur la base de sa version antérieure ; les informations de type de menace et de gravité doivent être conservées sur l'alerte au moment de sa création, indépendamment de modifications ultérieures de la règle.
- La modification du statut d'une alerte doit être historisée par la mise à jour de la date de dernière modification de statut.
- La modification d'un paramètre de configuration doit être tracée par l'enregistrement de l'utilisateur et de la date de modification.

### 6.5 Cohérence des données

- La date de fin d'une période statistique doit toujours être postérieure à sa date de début.
- Le statut d'une alerte doit toujours appartenir à l'ensemble des valeurs reconnues par le système (nouvelle, en cours, traitée, faux positif).
- Le type de menace associé à une règle ou à une alerte doit correspondre à une menace reconnue par le système, telle que définie dans le cahier des charges.

---

## 7. Politique de conservation

| Type de donnée | Orientation de conservation |
|---|---|
| **Alertes** | Les alertes doivent être conservées suffisamment longtemps pour permettre l'investigation d'incidents et la production de statistiques historiques. La durée précise de conservation n'est pas fixée dans ce document et doit être validée avec le CCM, notamment au regard d'éventuelles exigences légales applicables aux données à caractère personnel. |
| **Journaux** | Les journaux d'événements représentant un volume potentiellement important, une politique de conservation différenciée (conservation complète sur une période récente, conservation synthétique au-delà) pourra être envisagée ; les seuils précis restent à définir avec le CCM. |
| **Statistiques** | Les statistiques, étant des synthèses agrégées, peuvent être conservées sur une durée plus longue que les données brutes dont elles sont issues, sans réintroduire d'information individuelle sensible. |
| **Configurations** | L'historique des modifications de configuration (règles, paramètres, listes noires) doit être conservé au moins le temps nécessaire à la traçabilité des décisions prises par les utilisateurs habilités ; la durée précise reste à définir. |

Cette section ne fixe volontairement aucune valeur numérique de rétention, ces éléments faisant partie des points restant à valider avec le CCM (cf. question ouverte n° 6 du cahier des charges).

---

## 8. Contraintes de sécurité

| Aspect | Mesure générale |
|---|---|
| **Protection des comptes** | Le mot de passe de chaque utilisateur doit être conservé sous une forme protégée, jamais en clair ; l'accès aux informations d'un compte doit être limité à l'utilisateur concerné et aux administrateurs habilités. |
| **Confidentialité** | L'accès aux données (alertes, journaux, règles, statistiques) doit être restreint selon le rôle de l'utilisateur, conformément à la matrice de permissions définie dans le cahier des charges. |
| **Intégrité** | Les contraintes de référence et d'unicité décrites en section 6 doivent garantir qu'aucune donnée incohérente (référence à une entité inexistante, doublon) ne puisse être introduite dans la base. |
| **Traçabilité** | Toute création ou modification d'une règle, d'un paramètre de configuration ou d'une entrée de liste noire doit être associée à l'utilisateur responsable et horodatée, afin de permettre une revue ultérieure des décisions prises. |
| **Sauvegardes** | Les données persistées doivent faire l'objet d'une stratégie de sauvegarde régulière, afin de garantir leur récupération en cas d'incident technique ; les modalités précises (fréquence, support) relèvent d'un livrable ultérieur d'implémentation. |

---

## 9. Évolutivité

Le modèle de données proposé a été conçu pour accueillir les évolutions suivantes sans remise en cause de sa structure générale :

- **Nouvelles règles** : l'entité Règle repose sur une condition de déclenchement décrite de façon générique ; l'ajout d'une nouvelle règle, y compris pour une menace non encore identifiée, ne nécessite pas de modification du modèle de données.
- **Nouveaux types d'alertes** : le type de menace associé à une alerte n'est pas limité à une liste figée au niveau du modèle ; il correspond à un type reconnu par le système, dont l'ensemble peut être enrichi sans modifier la structure de l'entité Alerte.
- **Nouvelles statistiques** : l'entité Statistique repose sur une période et des indicateurs agrégés ; de nouvelles dimensions d'analyse (par exemple une répartition par adresse IP ou par zone géographique) peuvent être ajoutées en complément des indicateurs déjà définis, sans remettre en cause les statistiques existantes.
- **Nouvelles méthodes de détection** : la séparation entre l'entité Règle (condition de détection) et le moteur de détection qui l'exploite, déjà actée dans l'architecture logicielle, permet d'envisager de nouvelles formes de conditions (par exemple issues d'un modèle de détection comportementale ou de Machine Learning) sans modifier les autres entités du système.

---

## 10. Vérification de cohérence

### 10.1 Cohérence avec le cahier des charges

| Élément du cahier des charges | Vérification |
|---|---|
| Entités de données (section 10) | Utilisateur, Alerte, Log, Règle et Statistique sont toutes reprises ; les entités Rôle, Configuration et Liste noire constituent des précisions complémentaires, cohérentes avec les besoins déjà exprimés (profils utilisateurs, paramétrage des règles, gestion d'une liste noire) mais non identifiées individuellement dans le cahier des charges d'origine. |
| Profils utilisateurs et permissions (section 5) | Repris fidèlement par la relation Rôle → Utilisateur et par les contraintes d'accès décrites en section 8. |
| Cas d'utilisation UC8 (qualifier une alerte) | Repris par la relation optionnelle Utilisateur → Alerte et par l'attribut statut de traitement. |
| Menaces à détecter (section 7) | Couvertes par l'entité Règle, dont le type de menace associé doit correspondre à l'une des neuf menaces définies, ou à toute menace ajoutée ultérieurement. |

### 10.2 Cohérence avec les spécifications techniques

| Élément des spécifications techniques | Vérification |
|---|---|
| Choix de PostgreSQL (section 5) | Confirmé et approfondi en section 2 de ce document. |
| Module Base de données (section 3.8) | Les entités décrites correspondent aux données que ce module doit stocker et restituer. |
| Gestion des erreurs — indisponibilité de la base de données (section 8) | Sans impact direct sur le modèle de données ; ce point reste géré au niveau architectural, non au niveau de la structure des données. |

### 10.3 Cohérence avec la conception UML

| Élément de la conception UML | Vérification |
|---|---|
| Classes Utilisateur, Alerte, Log, Règle, Statistique | Reprises à l'identique comme entités de données, avec les mêmes attributs principaux. |
| Attribut « profil » de la classe Utilisateur | Ce document propose de le transformer en une relation vers une entité Rôle distincte ; il s'agit d'un raffinement du modèle de données par rapport à la conception UML, signalé comme écart en section 10.5 ci-dessous. |
| Relation Règle → Alerte, Utilisateur → Règle, Utilisateur → Alerte | Reprises fidèlement, avec précision des cardinalités. |

### 10.4 Cohérence avec l'architecture logicielle

| Élément de l'architecture logicielle | Vérification |
|---|---|
| Module Configuration (section 4.10) | Traduit fidèlement en entités Configuration et Liste noire dans ce document. |
| Flux « Détection consulte Configuration » | Cohérent avec la relation Règle (condition de déclenchement) et l'entité Liste noire, consultées par le moteur de détection. |

### 10.5 Écarts et décisions restant à valider

- **Introduction de l'entité Rôle** : ce document remplace l'attribut « profil » de la classe Utilisateur (Livrable 3) par une entité Rôle distincte. Ce choix améliore la cohérence des données mais constitue un écart par rapport à la conception UML telle que validée ; il est recommandé de mettre à jour ultérieurement le diagramme de classes pour refléter cette évolution, sans qu'aucune modification ne soit apportée ici aux livrables précédents.
- **Introduction des entités Configuration et Liste noire** : ces entités précisent, au niveau des données, le module Configuration déjà introduit dans l'architecture logicielle (Livrable 4) ; elles ne contredisent aucun élément validé mais n'avaient pas été anticipées dans le cahier des charges d'origine.
- **Statut d'entité pour la Statistique** : la question de savoir si les statistiques doivent être stockées de façon persistante (entité à part entière, comme modélisée ici) ou recalculées à la demande sans persistance reste une question ouverte, déjà signalée dans les spécifications techniques (section 11, question 4) et dans la conception UML (section 8.3) ; ce document retient, par prudence, une hypothèse de persistance, à confirmer.
- **Durées de conservation** : les durées précises de conservation des alertes, journaux, statistiques et configurations ne sont pas fixées dans ce document et restent à valider avec le CCM, conformément à la question ouverte n° 6 du cahier des charges.
- **Modalités de sauvegarde** : la stratégie de sauvegarde n'est décrite qu'au niveau des principes généraux (section 8) ; ses modalités précises (fréquence, support, procédure de restauration) restent à définir dans un livrable ultérieur.

---

*Fin du document — Livrable 5.*
