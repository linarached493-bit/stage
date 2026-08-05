import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useAuth } from "../context/AuthContext";
import DashboardPage from "./DashboardPage";

vi.mock("../context/AuthContext");

describe("DashboardPage", () => {
  it("affiche le message de bienvenue avec le nom et le role de l'utilisateur connecte", () => {
    useAuth.mockReturnValue({
      utilisateur: { id: 1, nom_utilisateur: "admin", role: "Administrateur" },
    });

    render(<DashboardPage />);

    expect(screen.getByRole("heading", { name: /bienvenue, admin/i })).toBeInTheDocument();
    expect(screen.getByText("Administrateur")).toBeInTheDocument();
  });

  it("affiche les informations d'un autre utilisateur connecte", () => {
    useAuth.mockReturnValue({
      utilisateur: { id: 2, nom_utilisateur: "analyste1", role: "Analyste sécurité" },
    });

    render(<DashboardPage />);

    expect(screen.getByRole("heading", { name: /bienvenue, analyste1/i })).toBeInTheDocument();
    expect(screen.getByText("Analyste sécurité")).toBeInTheDocument();
  });
});
