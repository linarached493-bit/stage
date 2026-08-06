// Page Statistiques : indicateurs principaux + répartitions, en lecture
// seule avec rafraîchissement manuel. Même architecture que les autres
// pages : toute la logique vit dans useStatistiques(), cette page
// assemble les composants présentationnels. Aucun graphique, aucune
// bibliothèque de visualisation, conformément à la consigne de ce tour.

import Badge from "../components/Badge";
import { libelleGravite, libelleStatut, toneGravite, toneStatut } from "../components/alerts/alertLabels";
import IndicateurCarte from "../components/statistics/IndicateurCarte";
import RepartitionTable from "../components/statistics/RepartitionTable";
import { useStatistiques } from "../hooks/useStatistiques";

function StatisticsPage() {
  const { statistiques, chargement, erreur, recharger } = useStatistiques();

  return (
    <section>
      <header className="statistiques-entete">
        <h1>Statistiques</h1>
        <button type="button" onClick={recharger} disabled={chargement}>
          Actualiser
        </button>
      </header>

      {chargement && <p>Chargement des statistiques...</p>}
      {erreur && <p role="alert">{erreur}</p>}

      {statistiques && (
        <>
          <div className="indicateurs">
            <IndicateurCarte libelle="Alertes au total" valeur={statistiques.nombre_total_alertes} />
            <IndicateurCarte libelle="Règles actives" valeur={statistiques.regles_actives} />
            <IndicateurCarte libelle="Règles inactives" valeur={statistiques.regles_inactives} />
            <IndicateurCarte
              libelle="Adresses en liste noire"
              valeur={statistiques.adresses_liste_noire}
            />
            <IndicateurCarte libelle="Logs au total" valeur={statistiques.nombre_total_logs} />
          </div>

          <RepartitionTable
            titre="Alertes par gravité"
            repartition={statistiques.alertes_par_gravite}
            libelleColonneCle="Gravité"
            rendreCle={(cle) => <Badge tone={toneGravite(cle)}>{libelleGravite(cle)}</Badge>}
          />
          <RepartitionTable
            titre="Alertes par statut"
            repartition={statistiques.alertes_par_statut}
            libelleColonneCle="Statut"
            rendreCle={(cle) => <Badge tone={toneStatut(cle)}>{libelleStatut(cle)}</Badge>}
          />
          <RepartitionTable
            titre="Alertes par type de menace"
            repartition={statistiques.alertes_par_type_menace}
            libelleColonneCle="Type de menace"
          />
          <RepartitionTable
            titre="Utilisateurs par rôle"
            repartition={statistiques.utilisateurs_par_role}
            libelleColonneCle="Rôle"
          />
        </>
      )}
    </section>
  );
}

export default StatisticsPage;
