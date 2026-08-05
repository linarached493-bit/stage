import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as authService from "../api/authService";
import { AuthProvider, useAuth } from "./AuthContext";

vi.mock("../api/authService");

function ComposantDeTest() {
  const { estAuthentifie, utilisateur, verificationSessionEnCours, connecter, deconnecter } =
    useAuth();
  if (verificationSessionEnCours) return <p>Chargement...</p>;
  return (
    <div>
      <p>{estAuthentifie ? "connecte" : "deconnecte"}</p>
      {utilisateur && <p>{utilisateur.nom_utilisateur}</p>}
      <button onClick={() => connecter("admin", "Passw0rd!").catch(() => {})}>Connexion</button>
      <button onClick={deconnecter}>Deconnexion</button>
    </div>
  );
}

function afficher() {
  return render(
    <AuthProvider>
      <ComposantDeTest />
    </AuthProvider>,
  );
}

beforeEach(() => {
  localStorage.clear();
  vi.resetAllMocks();
});

describe("AuthContext", () => {
  it("demarre deconnecte quand aucun jeton n'est stocke", async () => {
    afficher();

    expect(await screen.findByText("deconnecte")).toBeInTheDocument();
  });

  it("connecte l'utilisateur avec des identifiants valides et memorise le jeton", async () => {
    authService.seConnecter.mockResolvedValue({ access_token: "jeton-factice" });
    authService.consulterSession.mockResolvedValue({
      id: 1,
      nom_utilisateur: "admin",
      role: "Administrateur",
    });
    const utilisateurEvenement = userEvent.setup();
    afficher();

    await utilisateurEvenement.click(screen.getByText("Connexion"));

    expect(await screen.findByText("connecte")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
    expect(localStorage.getItem("ccm_ids_jeton")).toBe("jeton-factice");
  });

  it("ne connecte pas l'utilisateur si les identifiants sont invalides", async () => {
    authService.seConnecter.mockRejectedValue(new Error("401"));
    const utilisateurEvenement = userEvent.setup();
    afficher();

    await utilisateurEvenement.click(screen.getByText("Connexion"));

    expect(await screen.findByText("deconnecte")).toBeInTheDocument();
    expect(localStorage.getItem("ccm_ids_jeton")).toBeNull();
  });

  it("restaure la session a partir du jeton deja stocke (persistance)", async () => {
    localStorage.setItem("ccm_ids_jeton", "jeton-existant");
    authService.consulterSession.mockResolvedValue({
      id: 1,
      nom_utilisateur: "admin",
      role: "Administrateur",
    });

    afficher();

    expect(await screen.findByText("connecte")).toBeInTheDocument();
    expect(authService.consulterSession).toHaveBeenCalledWith("jeton-existant");
  });

  it("efface la session locale si le jeton stocke est invalide ou expire", async () => {
    localStorage.setItem("ccm_ids_jeton", "jeton-expire");
    authService.consulterSession.mockRejectedValue(new Error("401"));

    afficher();

    expect(await screen.findByText("deconnecte")).toBeInTheDocument();
    expect(localStorage.getItem("ccm_ids_jeton")).toBeNull();
  });

  it("deconnecte l'utilisateur et efface le jeton stocke", async () => {
    authService.seConnecter.mockResolvedValue({ access_token: "jeton-factice" });
    authService.consulterSession.mockResolvedValue({
      id: 1,
      nom_utilisateur: "admin",
      role: "Administrateur",
    });
    const utilisateurEvenement = userEvent.setup();
    afficher();
    await utilisateurEvenement.click(screen.getByText("Connexion"));
    await screen.findByText("connecte");

    await utilisateurEvenement.click(screen.getByText("Deconnexion"));

    expect(await screen.findByText("deconnecte")).toBeInTheDocument();
    expect(localStorage.getItem("ccm_ids_jeton")).toBeNull();
  });
});
