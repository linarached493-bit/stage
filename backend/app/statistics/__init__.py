"""Module Statistiques (docs/cahier_des_charges.md, F10 « afficher des
statistiques » ; UC5 « Consulter les statistiques »).

Contrairement aux neuf autres modules, ce module n'est pas prévu dans
docs/architecture_logicielle.md (section 3) : les statistiques y sont
décrites comme une agrégation calculée à partir des données d'autres
modules (Alerte, Log), pas comme un module autonome. Il est créé ici
car la ressource Statistiques (docs/conception_api_rest.md, section 4.6)
regroupe des données de plusieurs modules (Alertes, Règles, Utilisateurs,
Liste noire, Logs) : la rattacher à l'un d'entre eux aurait été trompeur.
Aucun modèle SQLAlchemy dans ce module — voir app/statistics/service.py.
"""
