import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import AlertesFiltres from "./AlertesFiltres";

describe("AlertesFiltres", () => {
  it("appelle onChangerGravite avec la valeur selectionnee", async () => {
    const onChangerGravite = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <AlertesFiltres
        gravite=""
        statut=""
        onChangerGravite={onChangerGravite}
        onChangerStatut={vi.fn()}
      />,
    );

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/gravité/i), "eleve");

    expect(onChangerGravite).toHaveBeenCalledWith("eleve");
  });

  it("appelle onChangerStatut avec la valeur selectionnee", async () => {
    const onChangerStatut = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <AlertesFiltres
        gravite=""
        statut=""
        onChangerGravite={vi.fn()}
        onChangerStatut={onChangerStatut}
      />,
    );

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/statut/i), "nouvelle");

    expect(onChangerStatut).toHaveBeenCalledWith("nouvelle");
  });

  it("reflete les valeurs de filtre actuelles", () => {
    render(
      <AlertesFiltres
        gravite="moyen"
        statut="en_cours"
        onChangerGravite={vi.fn()}
        onChangerStatut={vi.fn()}
      />,
    );

    expect(screen.getByLabelText(/gravité/i)).toHaveValue("moyen");
    expect(screen.getByLabelText(/statut/i)).toHaveValue("en_cours");
  });
});
