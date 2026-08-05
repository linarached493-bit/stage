"""Capture réseau (docs/architecture_logicielle.md, section 4.1 ;
docs/plan_de_developpement.md, tâche CAP-1).

Unique responsabilité de ce module, comme documenté dans le cahier des
charges de cette étape :

    Paquet réseau -> Extraction -> Création d'un événement -> Transmission

Aucune détection ici : ce module ne fait qu'observer et traduire. Le
Moteur de détection (app/detection/engine.py) n'est ni importé ni
appelé — il reste totalement inchangé, comme le sont les 9 règles déjà
implémentées.

Vocabulaire de `type_evenement` produit, volontairement limité aux
valeurs déjà reconnues par les règles existantes (voir
app/detection/engine.py:CALCULATEURS_INDICATEURS) :
- "icmp"      : paquet ICMP (ICMP Flood)
- "syn"       : paquet TCP avec le seul drapeau SYN actif, c'est-à-dire
                une tentative de connexion non finalisée (SYN Flood)
- "connexion" : tout autre paquet TCP (connexion établie ou en cours)
                ou tout paquet UDP (Tentatives répétées de connexion ;
                exploité aussi, sans condition sur le type, par Port
                Scan, IP blacklistée, Ports interdits, Activité
                inhabituelle et Trafic anormal simple)

"echec_authentification" / "authentification_reussie" (Brute Force) ne
peuvent PAS être produits ici : ce sont des événements de couche
applicative (résultat d'une tentative de connexion à un service), non
observables dans les en-têtes IP/TCP/UDP/ICMP capturés par ce module.
Cette limite est assumée et documentée dans le bilan de ce livrable.
"""

from collections.abc import Callable, Iterable
from datetime import UTC, datetime

from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.packet import Packet
from scapy.sendrecv import sniff

from app.capture.events import EvenementReseau


def paquet_vers_evenement(paquet: Packet) -> EvenementReseau | None:
    """Extrait d'un paquet Scapy les seules informations utiles au moteur
    de détection et les transforme en `EvenementReseau`.

    Retourne `None` pour tout paquet non pris en charge (sans couche IP,
    ou dont le protocole de transport n'est ni TCP, ni UDP, ni ICMP) :
    c'est le rejet explicite demandé, plutôt qu'un événement partiel ou
    incorrect.
    """
    if IP not in paquet:
        return None

    ip_source = paquet[IP].src
    ip_destination = paquet[IP].dst
    horodatage = datetime.fromtimestamp(float(paquet.time), tz=UTC)

    if ICMP in paquet:
        return EvenementReseau(
            ip_source=ip_source,
            ip_destination=ip_destination,
            type_evenement="icmp",
            horodatage=horodatage,
            protocole="ICMP",
        )

    if TCP in paquet:
        drapeaux = paquet[TCP].flags
        syn_pur = "S" in drapeaux and "A" not in drapeaux
        return EvenementReseau(
            ip_source=ip_source,
            ip_destination=ip_destination,
            type_evenement="syn" if syn_pur else "connexion",
            horodatage=horodatage,
            port=paquet[TCP].dport,
            protocole="TCP",
        )

    if UDP in paquet:
        return EvenementReseau(
            ip_source=ip_source,
            ip_destination=ip_destination,
            type_evenement="connexion",
            horodatage=horodatage,
            port=paquet[UDP].dport,
            protocole="UDP",
        )

    return None


def _traiter_un_paquet(paquet: Packet, gestionnaire: Callable[[EvenementReseau], None]) -> None:
    evenement = paquet_vers_evenement(paquet)
    if evenement is not None:
        gestionnaire(evenement)


def traiter_paquets(
    paquets: Iterable[Packet], gestionnaire: Callable[[EvenementReseau], None]
) -> None:
    """Convertit chaque paquet reconnu et le transmet à `gestionnaire`
    (par exemple une fonction qui l'ajoute à un tampon consulté ensuite
    par le Moteur de détection). Cœur testable de ce module : reçoit
    n'importe quel itérable de paquets, réels ou simulés en test —
    utilisée aussi bien par `capturer` ci-dessous que par les tests.
    """
    for paquet in paquets:
        _traiter_un_paquet(paquet, gestionnaire)


def capturer(
    interface: str,
    gestionnaire: Callable[[EvenementReseau], None],
    nombre_max: int | None = None,
) -> None:
    """Écoute `interface` en direct via Scapy et transmet chaque paquet
    reconnu à `gestionnaire`.

    Nécessite des privilèges d'écoute réseau (Npcap sous Windows, root
    sous Linux) non disponibles dans cet environnement de développement
    (voir docs/preparation_implementation.md, section 3.1) : cette
    fonction n'est donc pas exercée par les tests automatisés, seule sa
    logique de transformation (`paquet_vers_evenement`) et de
    transmission (`traiter_paquets`) l'est.
    """
    sniff(
        iface=interface,
        prn=lambda paquet: _traiter_un_paquet(paquet, gestionnaire),
        store=False,
        count=nombre_max or 0,
    )
