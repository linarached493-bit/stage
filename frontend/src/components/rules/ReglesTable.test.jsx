import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ReglesTable from "./ReglesTable";

const REGLE = {
  id: 9,
  nom: "Port Scan",
  type_menace: "port_scan",
  gravite: "moyen",
  statut: "active",
  condition_declenchement: { indicateur: "ports_distincts_par_source", seuil: 15, fenetre_secondes: 60 },
};

describe("ReglesTable", () => {
  it("affiche un message si aucune règle", () => {
    render(<ReglesTable regles={[]} regleSelectionneeId={null} onSelectionner={vi.fn()} />);

    expect(screen.getByText(/aucune règle/i)).toBeInTheDocument();
  });

  it("affiche les informations essentielles de chaque règle", () => {
    render(<ReglesTable regles={[REGLE]} regleSelectionneeId={null} onSelectionner={vi.fn()} />);

    expect(screen.getByText("Port Scan")).toBeInTheDocument();
    expect(screen.getByText("port_scan")).toBeInTheDocument();
    expect(screen.getByText("Moyen")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText(/seuil ≥ 15/)).toBeInTheDocument();
    expect(screen.getByText(/fenêtre 60s/)).toBeInTheDocument();
  });

  it("appelle onSelectionner avec l'identifiant au clic sur Détails", async () => {
    const onSelectionner = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<ReglesTable regles={[REGLE]} regleSelectionneeId={null} onSelectionner={onSelectionner} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(onSelectionner).toHaveBeenCalledWith(9);
  });
});
