import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as authService from "../api/authService";
import { AuthProvider } from "../context/AuthContext";
import LoginPage from "./LoginPage";

vi.mock("../api/authService");

beforeEach(() => {
  localStorage.clear();
  vi.resetAllMocks();
});

function afficherPage() {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={["/connexion"]}>
        <LoginPage />
      </MemoryRouter>
    </AuthProvider>,
  );
}

describe("LoginPage", () => {
  it("appelle le service d'authentification avec les identifiants saisis", async () => {
    authService.seConnecter.mockResolvedValue({ access_token: "jeton-factice" });
    authService.consulterSession.mockResolvedValue({
      id: 1,
      nom_utilisateur: "admin",
      role: "Administrateur",
    });
    const utilisateurEvenement = userEvent.setup();
    afficherPage();

    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "admin");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "Passw0rd!");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /se connecter/i }));

    expect(authService.seConnecter).toHaveBeenCalledWith("admin", "Passw0rd!");
  });

  it("affiche un message d'erreur en cas d'identifiants invalides", async () => {
    authService.seConnecter.mockRejectedValue(new Error("401"));
    const utilisateurEvenement = userEvent.setup();
    afficherPage();

    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "admin");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "mauvais");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /se connecter/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/identifiants invalides/i);
  });

  it("desactive le bouton pendant la soumission puis le reactive apres une erreur", async () => {
    let rejeter;
    authService.seConnecter.mockReturnValue(
      new Promise((_resolve, reject) => {
        rejeter = reject;
      }),
    );
    const utilisateurEvenement = userEvent.setup();
    afficherPage();

    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "admin");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "Passw0rd!");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /se connecter/i }));

    expect(screen.getByRole("button", { name: /connexion.../i })).toBeDisabled();

    rejeter(new Error("401"));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /se connecter/i })).not.toBeDisabled();
  });
});
