import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as alertsService from "../api/alertsService";
import { useAuth } from "../context/AuthContext";
import AlertsPage from "./AlertsPage";

vi.mock("../api/alertsService");
vi.mock("../context/AuthContext");

const ALERTE_LISTE = {
  id: 1,
  type_menace: "port_scan",
  ip_source: "192.168.1.10",
  gravite: "eleve",
  statut_traitement: "nouvelle",
  horodatage_detection: "2026-08-05T10:00:00Z",
};

const ALERTE_DETAIL = {
  id: 1,
  type_menace: "port_scan",
  ip_source: "192.168.1.10",
  ip_destination: "10.0.0.1",
  gravite: "eleve",
  statut_traitement: "nouvelle",
  horodatage_detection: "2026-08-05T10:00:00Z",
  regle: "Port Scan",
  historique: [],
};

beforeEach(() => {
  vi.resetAllMocks();
  useAuth.mockReturnValue({ jeton: "jeton-test" });
  alertsService.fetchAlertes.mockResolvedValue([ALERTE_LISTE]);
  alertsService.fetchAlerteDetail.mockResolvedValue(ALERTE_DETAIL);
});

describe("AlertsPage", () => {
  it("affiche le chargement puis la liste des alertes", async () => {
    render(<AlertsPage />);

    expect(screen.getByText(/chargement des alertes/i)).toBeInTheDocument();
    expect(await screen.findByText("port_scan")).toBeInTheDocument();
    expect(alertsService.fetchAlertes).toHaveBeenCalledWith("jeton-test", { gravite: "", statut: "" });
  });

  it("affiche un message d'erreur en cas d'echec reseau du chargement", async () => {
    alertsService.fetchAlertes.mockRejectedValue(new Error("réseau indisponible"));

    render(<AlertsPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de récupérer les alertes/i);
  });

  it("recharge la liste avec le filtre gravite selectionne", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<AlertsPage />);
    await screen.findByText("port_scan");

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/gravité/i), "eleve");

    expect(await screen.findByText("port_scan")).toBeInTheDocument();
    expect(alertsService.fetchAlertes).toHaveBeenLastCalledWith("jeton-test", {
      gravite: "eleve",
      statut: "",
    });
  });

  it("affiche le detail d'une alerte selectionnee, avec son etat de chargement", async () => {
    let resoudreDetail;
    alertsService.fetchAlerteDetail.mockReturnValue(
      new Promise((resolve) => {
        resoudreDetail = resolve;
      }),
    );
    const utilisateurEvenement = userEvent.setup();
    render(<AlertsPage />);
    await screen.findByText("port_scan");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(screen.getByText(/chargement du détail/i)).toBeInTheDocument();

    resoudreDetail(ALERTE_DETAIL);

    expect(await screen.findByRole("heading", { name: /alerte #1/i })).toBeInTheDocument();
    expect(screen.getByText("Port Scan")).toBeInTheDocument();
    expect(alertsService.fetchAlerteDetail).toHaveBeenCalledWith("jeton-test", 1);
  });

  it("acquitte l'alerte selectionnee et rafraichit la liste", async () => {
    alertsService.acquitterAlerte.mockResolvedValue({
      ...ALERTE_DETAIL,
      statut_traitement: "en_cours",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<AlertsPage />);
    await screen.findByText("port_scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /alerte #1/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^acquitter$/i }));

    expect(alertsService.acquitterAlerte).toHaveBeenCalledWith("jeton-test", 1, undefined);
    expect(alertsService.fetchAlertes).toHaveBeenCalledTimes(2);
  });

  it("ferme l'alerte selectionnee avec le statut choisi", async () => {
    alertsService.fermerAlerte.mockResolvedValue({
      ...ALERTE_DETAIL,
      statut_traitement: "traitee",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<AlertsPage />);
    await screen.findByText("port_scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /alerte #1/i });

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/statut final/i), "traitee");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^fermer$/i }));

    expect(alertsService.fermerAlerte).toHaveBeenCalledWith("jeton-test", 1, "traitee", undefined);
    expect(alertsService.fetchAlertes).toHaveBeenCalledTimes(2);
  });

  it("ajoute un commentaire a l'alerte selectionnee", async () => {
    alertsService.ajouterCommentaire.mockResolvedValue({
      ...ALERTE_DETAIL,
      historique: [
        { statut: "nouvelle", commentaire: "RAS", utilisateur: "admin", horodatage: "2026-08-05T11:00:00Z" },
      ],
    });
    const utilisateurEvenement = userEvent.setup();
    render(<AlertsPage />);
    await screen.findByText("port_scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /alerte #1/i });

    await utilisateurEvenement.type(screen.getByLabelText(/^commentaire$/i), "RAS");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^commenter$/i }));

    expect(alertsService.ajouterCommentaire).toHaveBeenCalledWith("jeton-test", 1, "RAS");
    expect(await screen.findByText(/ras/i)).toBeInTheDocument();
  });

  it("affiche un message d'erreur si une action de traitement echoue", async () => {
    alertsService.acquitterAlerte.mockRejectedValue(new Error("409"));
    const utilisateurEvenement = userEvent.setup();
    render(<AlertsPage />);
    await screen.findByText("port_scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /alerte #1/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^acquitter$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/l'action a échoué/i);
  });
});
