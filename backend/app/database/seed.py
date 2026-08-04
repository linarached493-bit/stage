"""Données de référence initiales (docs/plan_de_developpement.md, tâche DB-7).

Contient uniquement les trois rôles reconnus par le système
(docs/cahier_des_charges.md, section 5). Idempotent : n'insère un rôle
que s'il n'existe pas déjà.
"""

from sqlalchemy.orm import Session

from app.auth.models import Role

ROLES_DE_REFERENCE = (
    ("Administrateur", "Accès complet au système."),
    ("Analyste sécurité", "Consultation et gestion des règles et des alertes."),
    ("Lecture seule", "Consultation des alertes et des statistiques uniquement."),
)


def seed_roles(session: Session) -> list[Role]:
    roles_existants = {role.nom for role in session.query(Role).all()}
    roles_crees = []
    for nom, description in ROLES_DE_REFERENCE:
        if nom not in roles_existants:
            role = Role(nom=nom, description=description)
            session.add(role)
            roles_crees.append(role)
    if roles_crees:
        session.commit()
    return roles_crees
