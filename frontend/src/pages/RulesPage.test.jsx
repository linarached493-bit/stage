import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as rulesService from "../api/rulesService";
import { useAuth } from "../context/AuthContext";
import RulesPage from "./RulesPage";

vi.mock("../api/rulesService");
vi.mock("../context/AuthContext");

const REGLE_LISTE = {
  id: 1,
  nom: "Port Scan",
  type_menace: "port_scan",
  gravite: "moyen",
  statut: "active",
  condition_declenchement: { indicateur: "ports_distincts_par_source", seuil: 15, fenetre_secondes: 60 },
};

const REGLE_DETAIL = {
  id: 1,
  nom: "Port Scan",
  description: "Détection de balayage de ports",
  type_menace: "port_scan",
  gravite: "moyen",
  statut: "active",
  condition_declenchement: { indicateur: "ports_distincts_par_source", seuil: 15, fenetre_secondes: 60 },
  auteur: "admin",
  date_creation: "2026-08-01T09:00:00Z",
  date_derniere_modification: null,
};

beforeEach(() => {
  vi.resetAllMocks();
  useAuth.mockReturnValue({ jeton: "jeton-test" });
  rulesService.fetchRegles.mockResolvedValue([REGLE_LISTE]);
  rulesService.fetchRegleDetail.mockResolvedValue(REGLE_DETAIL);
});

describe("RulesPage", () => {
  it("affiche le chargement puis la liste des règles", async () => {
    render(<RulesPage />);

    expect(screen.getByText(/chargement des règles/i)).toBeInTheDocument();
    expect(await screen.findByText("Port Scan")).toBeInTheDocument();
    expect(rulesService.fetchRegles).toHaveBeenCalledWith("jeton-test");
  });

  it("affiche un message d'erreur en cas d'echec reseau du chargement", async () => {
    rulesService.fetchRegles.mockRejectedValue(new Error("réseau indisponible"));

    render(<RulesPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de récupérer les règles/i);
  });

  it("cree une règle puis referme le formulaire et rafraichit la liste", async () => {
    rulesService.creerRegle.mockResolvedValue({ ...REGLE_DETAIL, id: 2 });
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer une règle/i }));
    await utilisateurEvenement.type(screen.getByLabelText(/^nom$/i), "SYN Flood");
    await utilisateurEvenement.type(screen.getByLabelText(/^menace$/i), "syn_flood");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^créer$/i }));

    expect(rulesService.creerRegle).toHaveBeenCalledWith("jeton-test", {
      nom: "SYN Flood",
      description: null,
      typeMenace: "syn_flood",
      gravite: "moyen",
      conditionDeclenchement: { indicateur: "ports_distincts_par_source", seuil: 1 },
    });
    expect(rulesService.fetchRegles).toHaveBeenCalledTimes(2);
    expect(await screen.findByRole("button", { name: /créer une règle/i })).toBeInTheDocument();
  });

  it("affiche un message d'erreur si la creation echoue et laisse le formulaire ouvert", async () => {
    rulesService.creerRegle.mockRejectedValue(new Error("409"));
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer une règle/i }));
    await utilisateurEvenement.type(screen.getByLabelText(/^nom$/i), "Port Scan");
    await utilisateurEvenement.type(screen.getByLabelText(/^menace$/i), "port_scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^créer$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de créer cette règle/i);
    expect(screen.getByLabelText(/^nom$/i)).toBeInTheDocument();
  });

  it("affiche le detail d'une règle selectionnee", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(await screen.findByRole("heading", { name: /port scan/i })).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
    expect(rulesService.fetchRegleDetail).toHaveBeenCalledWith("jeton-test", 1);
  });

  it("modifie la règle selectionnee et rafraichit la liste", async () => {
    rulesService.modifierRegle.mockResolvedValue({ ...REGLE_DETAIL, gravite: "eleve" });
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /port scan/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^modifier$/i }));
    await utilisateurEvenement.selectOptions(screen.getByLabelText(/gravité/i), "eleve");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^enregistrer$/i }));

    expect(rulesService.modifierRegle).toHaveBeenCalledWith("jeton-test", 1, {
      nom: "Port Scan",
      description: "Détection de balayage de ports",
      typeMenace: "port_scan",
      gravite: "eleve",
      conditionDeclenchement: { indicateur: "ports_distincts_par_source", seuil: 15, fenetre_secondes: 60 },
    });
    expect(rulesService.fetchRegles).toHaveBeenCalledTimes(2);
  });

  it("desactive la règle selectionnee", async () => {
    rulesService.changerStatutRegle.mockResolvedValue({ ...REGLE_DETAIL, statut: "inactive" });
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /port scan/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(rulesService.changerStatutRegle).toHaveBeenCalledWith("jeton-test", 1, "inactive");
    expect(await screen.findByRole("button", { name: /^activer$/i })).toBeInTheDocument();
  });

  it("active une règle inactive selectionnee", async () => {
    rulesService.fetchRegleDetail.mockResolvedValue({ ...REGLE_DETAIL, statut: "inactive" });
    rulesService.changerStatutRegle.mockResolvedValue({ ...REGLE_DETAIL, statut: "active" });
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /port scan/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^activer$/i }));

    expect(rulesService.changerStatutRegle).toHaveBeenCalledWith("jeton-test", 1, "active");
  });

  it("affiche un message d'erreur si une action de traitement echoue", async () => {
    rulesService.changerStatutRegle.mockRejectedValue(new Error("500"));
    const utilisateurEvenement = userEvent.setup();
    render(<RulesPage />);
    await screen.findByText("Port Scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /port scan/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/l'action a échoué/i);
  });
});
