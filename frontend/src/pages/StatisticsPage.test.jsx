import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as statisticsService from "../api/statisticsService";
import { useAuth } from "../context/AuthContext";
import StatisticsPage from "./StatisticsPage";

vi.mock("../api/statisticsService");
vi.mock("../context/AuthContext");

const STATISTIQUES = {
  nombre_total_alertes: 12,
  alertes_par_gravite: { moyen: 8, eleve: 4 },
  alertes_par_statut: { nouvelle: 5, traitee: 7 },
  alertes_par_type_menace: { port_scan: 6, syn_flood: 6 },
  regles_actives: 9,
  regles_inactives: 2,
  utilisateurs_par_role: { Administrateur: 1, "Analyste sécurité": 15 },
  adresses_liste_noire: 3,
  nombre_total_logs: 42,
};

beforeEach(() => {
  vi.resetAllMocks();
  useAuth.mockReturnValue({ jeton: "jeton-test" });
  statisticsService.fetchStatistiques.mockResolvedValue(STATISTIQUES);
});

describe("StatisticsPage", () => {
  it("affiche le chargement puis les indicateurs principaux", async () => {
    render(<StatisticsPage />);

    expect(screen.getByText(/chargement des statistiques/i)).toBeInTheDocument();
    expect(await screen.findByText("12")).toBeInTheDocument();
    expect(screen.getByText("Alertes au total")).toBeInTheDocument();
    expect(screen.getByText("9")).toBeInTheDocument();
    expect(screen.getByText("Règles actives")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("Règles inactives")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Adresses en liste noire")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Logs au total")).toBeInTheDocument();
    expect(statisticsService.fetchStatistiques).toHaveBeenCalledWith("jeton-test");
  });

  it("affiche la répartition des alertes par gravité, statut et type de menace", async () => {
    render(<StatisticsPage />);
    await screen.findByText("Alertes au total");

    expect(screen.getByRole("heading", { name: /alertes par gravité/i })).toBeInTheDocument();
    expect(screen.getByText("Moyen")).toBeInTheDocument();
    expect(screen.getByText("Élevé")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: /alertes par statut/i })).toBeInTheDocument();
    expect(screen.getByText("Nouvelle")).toBeInTheDocument();
    expect(screen.getByText("Traitée")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: /alertes par type de menace/i })).toBeInTheDocument();
    expect(screen.getByText("port_scan")).toBeInTheDocument();
    expect(screen.getByText("syn_flood")).toBeInTheDocument();
  });

  it("affiche la répartition des utilisateurs par rôle", async () => {
    render(<StatisticsPage />);
    await screen.findByText("Alertes au total");

    expect(screen.getByRole("heading", { name: /utilisateurs par rôle/i })).toBeInTheDocument();
    expect(screen.getByText("Administrateur")).toBeInTheDocument();
    expect(screen.getByText("Analyste sécurité")).toBeInTheDocument();
  });

  it("affiche un message d'erreur en cas d'echec reseau du chargement", async () => {
    statisticsService.fetchStatistiques.mockRejectedValue(new Error("réseau indisponible"));

    render(<StatisticsPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /impossible de récupérer les statistiques/i,
    );
  });

  it("rafraichit les statistiques au clic sur Actualiser", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<StatisticsPage />);
    await screen.findByText("Alertes au total");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /actualiser/i }));

    expect(statisticsService.fetchStatistiques).toHaveBeenCalledTimes(2);
  });

  it("desactive le bouton Actualiser pendant le chargement", async () => {
    let resoudre;
    statisticsService.fetchStatistiques.mockReturnValue(
      new Promise((resolve) => {
        resoudre = resolve;
      }),
    );

    render(<StatisticsPage />);

    expect(screen.getByRole("button", { name: /actualiser/i })).toBeDisabled();

    resoudre(STATISTIQUES);
    await screen.findByText("Alertes au total");

    expect(screen.getByRole("button", { name: /actualiser/i })).not.toBeDisabled();
  });
});
