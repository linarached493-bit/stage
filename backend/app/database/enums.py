"""Valeurs fermées partagées entre plusieurs entités (voir
docs/conception_base_de_donnees.md, section 5).

Le type de menace n'est volontairement pas un enum fermé ici : la
décision retenue (docs/preparation_implementation.md, section 3.3) est
de garder l'entité Règle générique et paramétrable pour ne pas figer la
liste des menaces dans le schéma de données.
"""

import enum


class Gravite(str, enum.Enum):
    MOYEN = "moyen"
    ELEVE = "eleve"
