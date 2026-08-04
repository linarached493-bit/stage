from app.configuration.models import AdresseListeNoire, StatutListeNoire
from app.configuration.service import adresses_blacklistees_actives


def test_adresses_blacklistees_actives_ignore_les_entrees_inactives(db_session):
    db_session.add_all(
        [
            AdresseListeNoire(adresse_ip="203.0.113.66", statut=StatutListeNoire.ACTIVE),
            AdresseListeNoire(adresse_ip="198.51.100.10", statut=StatutListeNoire.INACTIVE),
        ]
    )
    db_session.commit()

    resultat = adresses_blacklistees_actives(db_session)

    assert resultat == frozenset({"203.0.113.66"})


def test_adresses_blacklistees_actives_vide_si_aucune_entree(db_session):
    assert adresses_blacklistees_actives(db_session) == frozenset()
