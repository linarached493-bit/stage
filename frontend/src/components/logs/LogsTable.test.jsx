import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import LogsTable from "./LogsTable";

const LOG = {
  id: 12,
  horodatage: "2026-08-06T10:00:00Z",
  type_evenement: "syn",
  niveau: "avertissement",
  ip_source: "192.168.1.10",
  ip_destination: "10.0.0.1",
  ports: "443",
  protocole: "TCP",
  alerte_id: 3,
};

describe("LogsTable", () => {
  it("affiche un message si aucun log", () => {
    render(<LogsTable logs={[]} logSelectionneId={null} onSelectionner={vi.fn()} />);

    expect(screen.getByText(/aucun log/i)).toBeInTheDocument();
  });

  it("affiche les informations essentielles de chaque log", () => {
    render(<LogsTable logs={[LOG]} logSelectionneId={null} onSelectionner={vi.fn()} />);

    expect(screen.getByText("syn")).toBeInTheDocument();
    expect(screen.getByText("Avertissement")).toBeInTheDocument();
    expect(screen.getByText("192.168.1.10")).toBeInTheDocument();
    expect(screen.getByText(/vers 10\.0\.0\.1:443/)).toBeInTheDocument();
  });

  it("appelle onSelectionner avec l'identifiant au clic sur Détails", async () => {
    const onSelectionner = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<LogsTable logs={[LOG]} logSelectionneId={null} onSelectionner={onSelectionner} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(onSelectionner).toHaveBeenCalledWith(12);
  });
});
