import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as authService from "../api/authService";
import { AuthProvider } from "../context/AuthContext";
import ProtectedRoute from "./ProtectedRoute";

vi.mock("../api/authService");

beforeEach(() => {
  localStorage.clear();
  vi.resetAllMocks();
});

function afficherAvecRoutes(cheminInitial) {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={[cheminInitial]}>
        <Routes>
          <Route path="/connexion" element={<p>Page de connexion</p>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<p>Contenu protege</p>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthProvider>,
  );
}

describe("ProtectedRoute", () => {
  it("redirige vers la page de connexion si aucune session n'est active", async () => {
    afficherAvecRoutes("/");

    expect(await screen.findByText("Page de connexion")).toBeInTheDocument();
    expect(screen.queryByText("Contenu protege")).not.toBeInTheDocument();
  });

  it("affiche le contenu protege si une session valide est active", async () => {
    localStorage.setItem("ccm_ids_jeton", "jeton-existant");
    authService.consulterSession.mockResolvedValue({
      id: 1,
      nom_utilisateur: "admin",
      role: "Administrateur",
    });

    afficherAvecRoutes("/");

    expect(await screen.findByText("Contenu protege")).toBeInTheDocument();
  });

  it("redirige vers la connexion si le jeton stocke est invalide", async () => {
    localStorage.setItem("ccm_ids_jeton", "jeton-expire");
    authService.consulterSession.mockRejectedValue(new Error("401"));

    afficherAvecRoutes("/");

    expect(await screen.findByText("Page de connexion")).toBeInTheDocument();
  });
});
