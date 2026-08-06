import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as logsService from "../api/logsService";
import { useAuth } from "../context/AuthContext";
import LogsPage from "./LogsPage";

vi.mock("../api/logsService");
vi.mock("../context/AuthContext");

const LOG_LISTE = {
  id: 1,
  horodatage: "2026-08-06T10:00:00Z",
  type_evenement: "syn",
  niveau: "avertissement",
  ip_source: "192.168.1.10",
  ip_destination: "10.0.0.1",
  ports: "443",
  protocole: "TCP",
  alerte_id: null,
};

const LOG_DETAIL = { ...LOG_LISTE };

beforeEach(() => {
  vi.resetAllMocks();
  useAuth.mockReturnValue({ jeton: "jeton-test" });
  logsService.fetchLogs.mockResolvedValue([LOG_LISTE]);
  logsService.fetchLogDetail.mockResolvedValue(LOG_DETAIL);
});

const FILTRES_INITIAUX = {
  niveau: "",
  typeEvenement: "",
  adresseIp: "",
  dateDebut: "",
  dateFin: "",
  recherche: "",
};

describe("LogsPage", () => {
  it("affiche le chargement puis la liste des logs", async () => {
    render(<LogsPage />);

    expect(screen.getByText(/chargement des logs/i)).toBeInTheDocument();
    expect(await screen.findByText("syn")).toBeInTheDocument();
    expect(logsService.fetchLogs).toHaveBeenCalledWith("jeton-test", FILTRES_INITIAUX);
  });

  it("affiche un message d'erreur en cas d'echec reseau du chargement", async () => {
    logsService.fetchLogs.mockRejectedValue(new Error("réseau indisponible"));

    render(<LogsPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de récupérer les logs/i);
  });

  it("recharge la liste avec le filtre niveau selectionne", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<LogsPage />);
    await screen.findByText("syn");

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/^niveau$/i), "erreur");

    expect(await screen.findByText("syn")).toBeInTheDocument();
    expect(logsService.fetchLogs).toHaveBeenLastCalledWith("jeton-test", {
      ...FILTRES_INITIAUX,
      niveau: "erreur",
    });
  });

  it("recharge la liste avec le terme de recherche saisi", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<LogsPage />);
    await screen.findByText("syn");

    await utilisateurEvenement.type(screen.getByLabelText(/recherche/i), "T");

    expect(await screen.findByText("syn")).toBeInTheDocument();
    expect(logsService.fetchLogs).toHaveBeenLastCalledWith("jeton-test", {
      ...FILTRES_INITIAUX,
      recherche: "T",
    });
  });

  it("recharge la liste avec l'adresse ip saisie", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<LogsPage />);
    await screen.findByText("syn");

    await utilisateurEvenement.type(screen.getByLabelText(/adresse ip/i), "1");

    expect(logsService.fetchLogs).toHaveBeenLastCalledWith("jeton-test", {
      ...FILTRES_INITIAUX,
      adresseIp: "1",
    });
  });

  it("affiche le detail d'un log selectionne, avec son etat de chargement", async () => {
    let resoudreDetail;
    logsService.fetchLogDetail.mockReturnValue(
      new Promise((resolve) => {
        resoudreDetail = resolve;
      }),
    );
    const utilisateurEvenement = userEvent.setup();
    render(<LogsPage />);
    await screen.findByText("syn");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(screen.getByText(/chargement du détail/i)).toBeInTheDocument();

    resoudreDetail(LOG_DETAIL);

    expect(await screen.findByRole("heading", { name: /log #1/i })).toBeInTheDocument();
    expect(logsService.fetchLogDetail).toHaveBeenCalledWith("jeton-test", 1);
  });

  it("affiche un message d'erreur si la consultation du detail echoue", async () => {
    logsService.fetchLogDetail.mockRejectedValue(new Error("404"));
    const utilisateurEvenement = userEvent.setup();
    render(<LogsPage />);
    await screen.findByText("syn");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de récupérer le détail du log/i);
  });

  it("ferme le panneau de detail au clic sur Fermer le panneau", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<LogsPage />);
    await screen.findByText("syn");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /log #1/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /fermer le panneau/i }));

    expect(screen.queryByRole("heading", { name: /log #1/i })).not.toBeInTheDocument();
  });
});
