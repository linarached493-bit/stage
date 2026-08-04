"""Type de donnée produit par la Capture réseau (docs/architecture_logicielle.md,
section 4.1, sortie « paquet structuré »).

Tant que la capture réseau live n'est pas branchée (nécessite Scapy et
des privilèges d'écoute réseau, voir docs/plan_de_developpement.md,
tâche CAP-1), ces événements sont produits soit par un test, soit par
tout futur adaptateur de capture.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EvenementReseau:
    ip_source: str
    type_evenement: str
    horodatage: datetime
    ip_destination: str | None = None
    port: int | None = None
    protocole: str | None = None
