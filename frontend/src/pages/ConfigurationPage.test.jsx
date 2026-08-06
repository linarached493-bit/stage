import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as configurationService from "../api/configurationService";
import { useAuth } from "../context/AuthContext";
import ConfigurationPage from "./ConfigurationPage";

vi.mock("../api/configurationService");
vi.mock("../context/AuthContext");

const PARAMETRE = {
  nom_parametre: "seuil_alerte",
  valeur: "10",
  description: "Seuil générique",
  date_derniere_modification: "2026-08-01T09:00:00Z",
};

const ENTREE_LISTE_NOIRE = {
  id: 1,
  adresse_ip: "203.0.113.66",
  motif_source: "Scan detecte",
  date_ajout: "2026-08-01T09:00:00Z",
  statut: "active",
};

beforeEach(() => {
  vi.resetAllMocks();
  useAuth.mockReturnValue({ jeton: "jeton-test" });
  configurationService.fetchParametres.mockResolvedValue([PARAMETRE]);
  configurationService.fetchPortsInterdits.mockResolvedValue({ ports: [22, 23] });
  configurationService.fetchListeNoire.mockResolvedValue([ENTREE_LISTE_NOIRE]);
});

describe("ConfigurationPage", () => {
  it("affiche le chargement puis la liste des paramètres", async () => {
    render(<ConfigurationPage />);

    expect(screen.getByText(/chargement des paramètres/i)).toBeInTheDocument();
    expect(await screen.findByText("seuil_alerte")).toBeInTheDocument();
    expect(configurationService.fetchParametres).toHaveBeenCalledWith("jeton-test");
  });

  it("affiche un message d'erreur si le chargement des paramètres echoue", async () => {
    configurationService.fetchParametres.mockRejectedValue(new Error("réseau indisponible"));

    render(<ConfigurationPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de récupérer les paramètres/i);
  });

  it("modifie un paramètre puis referme le panneau et rafraichit la liste", async () => {
    configurationService.modifierParametre.mockResolvedValue({ ...PARAMETRE, valeur: "20" });
    const utilisateurEvenement = userEvent.setup();
    render(<ConfigurationPage />);
    await screen.findByText("seuil_alerte");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /modifier/i }));
    const champValeur = screen.getByLabelText(/valeur/i);
    await utilisateurEvenement.clear(champValeur);
    await utilisateurEvenement.type(champValeur, "20");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /enregistrer le paramètre/i }));

    expect(configurationService.modifierParametre).toHaveBeenCalledWith(
      "jeton-test",
      "seuil_alerte",
      "20",
      "Seuil générique",
    );
    expect(configurationService.fetchParametres).toHaveBeenCalledTimes(2);
    expect(
      screen.queryByRole("button", { name: /enregistrer le paramètre/i }),
    ).not.toBeInTheDocument();
  });

  it("affiche les ports interdits actuels", async () => {
    render(<ConfigurationPage />);

    expect(await screen.findByLabelText(/ports interdits/i)).toHaveValue("22, 23");
    expect(configurationService.fetchPortsInterdits).toHaveBeenCalledWith("jeton-test");
  });

  it("modifie les ports interdits", async () => {
    configurationService.modifierPortsInterdits.mockResolvedValue({ ports: [22, 23, 3389] });
    const utilisateurEvenement = userEvent.setup();
    render(<ConfigurationPage />);
    const champPorts = await screen.findByLabelText(/ports interdits/i);

    await utilisateurEvenement.type(champPorts, ", 3389");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /enregistrer les ports interdits/i }));

    expect(configurationService.modifierPortsInterdits).toHaveBeenCalledWith("jeton-test", [
      22, 23, 3389,
    ]);
  });

  it("affiche la liste noire", async () => {
    render(<ConfigurationPage />);

    expect(await screen.findByText("203.0.113.66")).toBeInTheDocument();
    expect(configurationService.fetchListeNoire).toHaveBeenCalledWith("jeton-test");
  });

  it("ajoute une adresse a la liste noire et rafraichit la liste", async () => {
    configurationService.ajouterAdresseListeNoire.mockResolvedValue({
      id: 2,
      adresse_ip: "198.51.100.20",
      motif_source: null,
      date_ajout: "2026-08-06T09:00:00Z",
      statut: "active",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<ConfigurationPage />);
    await screen.findByText("203.0.113.66");

    await utilisateurEvenement.type(screen.getByLabelText(/adresse ip/i), "198.51.100.20");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /ajouter/i }));

    expect(configurationService.ajouterAdresseListeNoire).toHaveBeenCalledWith(
      "jeton-test",
      "198.51.100.20",
      null,
    );
    expect(configurationService.fetchListeNoire).toHaveBeenCalledTimes(2);
  });

  it("desactive une adresse de la liste noire", async () => {
    configurationService.changerStatutListeNoire.mockResolvedValue({
      ...ENTREE_LISTE_NOIRE,
      statut: "inactive",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<ConfigurationPage />);
    await screen.findByText("203.0.113.66");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(configurationService.changerStatutListeNoire).toHaveBeenCalledWith(
      "jeton-test",
      1,
      "inactive",
    );
    expect(await screen.findByRole("button", { name: /^activer$/i })).toBeInTheDocument();
  });

  it("active une adresse desactivee de la liste noire", async () => {
    configurationService.fetchListeNoire.mockResolvedValue([
      { ...ENTREE_LISTE_NOIRE, statut: "inactive" },
    ]);
    configurationService.changerStatutListeNoire.mockResolvedValue({
      ...ENTREE_LISTE_NOIRE,
      statut: "active",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<ConfigurationPage />);
    await screen.findByText("203.0.113.66");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^activer$/i }));

    expect(configurationService.changerStatutListeNoire).toHaveBeenCalledWith(
      "jeton-test",
      1,
      "active",
    );
  });

  it("affiche un message d'erreur si le changement de statut echoue", async () => {
    configurationService.changerStatutListeNoire.mockRejectedValue(new Error("500"));
    const utilisateurEvenement = userEvent.setup();
    render(<ConfigurationPage />);
    await screen.findByText("203.0.113.66");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /impossible de modifier le statut de cette adresse/i,
    );
  });
});
