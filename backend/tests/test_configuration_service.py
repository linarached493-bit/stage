import json

from app.configuration.models import AdresseListeNoire, ParametreConfiguration, StatutListeNoire
from app.configuration.service import adresses_blacklistees_actives, ports_interdits_actifs


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


def test_ports_interdits_actifs_lit_le_parametre_de_configuration(db_session):
    db_session.add(
        ParametreConfiguration(
            nom_parametre="ports_interdits",
            valeur=json.dumps([23, 3389]),
            description="Ports interdits par la politique de sécurité du CCM",
        )
    )
    db_session.commit()

    resultat = ports_interdits_actifs(db_session)

    assert resultat == frozenset({23, 3389})


def test_ports_interdits_actifs_vide_si_parametre_absent(db_session):
    assert ports_interdits_actifs(db_session) == frozenset()
