import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ParametresTable from "./ParametresTable";

const PARAMETRE = {
  nom_parametre: "ports_interdits",
  valeur: "[22, 23]",
  description: "Ports interdits par la politique de sécurité du CCM.",
  date_derniere_modification: "2026-08-01T09:00:00Z",
};

describe("ParametresTable", () => {
  it("affiche un message si aucun paramètre", () => {
    render(<ParametresTable parametres={[]} parametreSelectionneNom={null} onSelectionner={vi.fn()} />);

    expect(screen.getByText(/aucun paramètre/i)).toBeInTheDocument();
  });

  it("affiche les informations essentielles de chaque paramètre", () => {
    render(
      <ParametresTable parametres={[PARAMETRE]} parametreSelectionneNom={null} onSelectionner={vi.fn()} />,
    );

    expect(screen.getByText("ports_interdits")).toBeInTheDocument();
    expect(screen.getByText("[22, 23]")).toBeInTheDocument();
    expect(screen.getByText(/politique de sécurité/i)).toBeInTheDocument();
  });

  it("appelle onSelectionner avec le nom du paramètre au clic sur Modifier", async () => {
    const onSelectionner = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <ParametresTable
        parametres={[PARAMETRE]}
        parametreSelectionneNom={null}
        onSelectionner={onSelectionner}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /modifier/i }));

    expect(onSelectionner).toHaveBeenCalledWith("ports_interdits");
  });
});
