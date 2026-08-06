import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import UtilisateursTable from "./UtilisateursTable";

const UTILISATEUR = {
  id: 5,
  nom_utilisateur: "admin",
  role: "Administrateur",
  statut_compte: "actif",
  date_creation: "2026-08-01T09:00:00Z",
};

describe("UtilisateursTable", () => {
  it("affiche un message si aucun utilisateur", () => {
    render(
      <UtilisateursTable utilisateurs={[]} utilisateurSelectionneId={null} onSelectionner={vi.fn()} />,
    );

    expect(screen.getByText(/aucun utilisateur/i)).toBeInTheDocument();
  });

  it("affiche les informations essentielles de chaque utilisateur", () => {
    render(
      <UtilisateursTable
        utilisateurs={[UTILISATEUR]}
        utilisateurSelectionneId={null}
        onSelectionner={vi.fn()}
      />,
    );

    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
    expect(screen.getByText("Administrateur")).toBeInTheDocument();
    expect(screen.getByText("Actif")).toBeInTheDocument();
  });

  it("affiche le statut desactive avec le bon libelle", () => {
    render(
      <UtilisateursTable
        utilisateurs={[{ ...UTILISATEUR, statut_compte: "desactive" }]}
        utilisateurSelectionneId={null}
        onSelectionner={vi.fn()}
      />,
    );

    expect(screen.getByText("Désactivé")).toBeInTheDocument();
  });

  it("appelle onSelectionner avec l'identifiant au clic sur Détails", async () => {
    const onSelectionner = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <UtilisateursTable
        utilisateurs={[UTILISATEUR]}
        utilisateurSelectionneId={null}
        onSelectionner={onSelectionner}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(onSelectionner).toHaveBeenCalledWith(5);
  });
});
