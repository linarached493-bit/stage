import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import AlertesTable from "./AlertesTable";

const ALERTE = {
  id: 42,
  type_menace: "port_scan",
  ip_source: "192.168.1.10",
  gravite: "eleve",
  statut_traitement: "nouvelle",
  horodatage_detection: "2026-08-05T10:00:00Z",
};

describe("AlertesTable", () => {
  it("affiche un message si aucune alerte", () => {
    render(<AlertesTable alertes={[]} alerteSelectionneeId={null} onSelectionner={vi.fn()} />);

    expect(screen.getByText(/aucune alerte/i)).toBeInTheDocument();
  });

  it("affiche les informations essentielles de chaque alerte", () => {
    render(
      <AlertesTable alertes={[ALERTE]} alerteSelectionneeId={null} onSelectionner={vi.fn()} />,
    );

    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("port_scan")).toBeInTheDocument();
    expect(screen.getByText("Élevé")).toBeInTheDocument();
    expect(screen.getByText("Nouvelle")).toBeInTheDocument();
    expect(screen.getByText("192.168.1.10")).toBeInTheDocument();
  });

  it("appelle onSelectionner avec l'identifiant de l'alerte au clic sur Détails", async () => {
    const onSelectionner = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <AlertesTable
        alertes={[ALERTE]}
        alerteSelectionneeId={null}
        onSelectionner={onSelectionner}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(onSelectionner).toHaveBeenCalledWith(42);
  });
});
