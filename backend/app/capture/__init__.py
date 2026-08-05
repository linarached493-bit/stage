"""Module Capture réseau (docs/architecture_logicielle.md, section 4.1).

Mission : observer le trafic circulant sur l'interface réseau
surveillée et le transformer en événements structurés
(`app.capture.events.EvenementReseau`) exploitables par le Moteur de
détection, sans effectuer aucune détection elle-même.

Voir app/capture/sniffer.py pour la transformation Scapy -> événement
(`paquet_vers_evenement`) et l'écoute en direct (`capturer`).
"""
