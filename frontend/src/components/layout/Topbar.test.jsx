import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { useAuth } from "../../context/AuthContext";
import Topbar from "./Topbar";

vi.mock("../../context/AuthContext");

describe("Topbar", () => {
  it("affiche le nom d'utilisateur connecte", () => {
    useAuth.mockReturnValue({
      utilisateur: { nom_utilisateur: "admin", role: "Administrateur" },
      deconnecter: vi.fn(),
    });

    render(<Topbar />);

    expect(screen.getByText(/admin/)).toBeInTheDocument();
  });

  it("appelle deconnecter lors du clic sur le bouton de deconnexion", async () => {
    const deconnecter = vi.fn();
    useAuth.mockReturnValue({
      utilisateur: { nom_utilisateur: "admin", role: "Administrateur" },
      deconnecter,
    });
    const utilisateurEvenement = userEvent.setup();

    render(<Topbar />);
    await utilisateurEvenement.click(screen.getByRole("button", { name: /se déconnecter/i }));

    expect(deconnecter).toHaveBeenCalledOnce();
  });
});
