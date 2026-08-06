import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ListeNoireTable from "./ListeNoireTable";

const ENTREE = {
  id: 7,
  adresse_ip: "203.0.113.66",
  motif_source: "Scan detecte",
  date_ajout: "2026-08-01T09:00:00Z",
  statut: "active",
};

describe("ListeNoireTable", () => {
  it("affiche un message si la liste noire est vide", () => {
    render(
      <ListeNoireTable entrees={[]} changementStatutEnCoursId={null} onChangerStatut={vi.fn()} />,
    );

    expect(screen.getByText(/aucune adresse/i)).toBeInTheDocument();
  });

  it("affiche les informations essentielles de chaque entree", () => {
    render(
      <ListeNoireTable entrees={[ENTREE]} changementStatutEnCoursId={null} onChangerStatut={vi.fn()} />,
    );

    expect(screen.getByText("203.0.113.66")).toBeInTheDocument();
    expect(screen.getByText("Scan detecte")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("propose Desactiver pour une adresse active et appelle onChangerStatut avec inactive", async () => {
    const onChangerStatut = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <ListeNoireTable
        entrees={[ENTREE]}
        changementStatutEnCoursId={null}
        onChangerStatut={onChangerStatut}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(onChangerStatut).toHaveBeenCalledWith(7, "inactive");
  });

  it("propose Activer pour une adresse inactive et appelle onChangerStatut avec active", async () => {
    const onChangerStatut = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <ListeNoireTable
        entrees={[{ ...ENTREE, statut: "inactive" }]}
        changementStatutEnCoursId={null}
        onChangerStatut={onChangerStatut}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^activer$/i }));

    expect(onChangerStatut).toHaveBeenCalledWith(7, "active");
  });

  it("desactive le bouton de l'entree en cours de modification", () => {
    render(
      <ListeNoireTable entrees={[ENTREE]} changementStatutEnCoursId={7} onChangerStatut={vi.fn()} />,
    );

    expect(screen.getByRole("button", { name: /désactiver/i })).toBeDisabled();
  });
});
