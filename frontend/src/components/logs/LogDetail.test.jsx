import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import LogDetail from "./LogDetail";

function log(surcharge = {}) {
  return {
    id: 8,
    horodatage: "2026-08-06T10:00:00Z",
    type_evenement: "icmp",
    niveau: "erreur",
    ip_source: "192.168.1.20",
    ip_destination: null,
    ports: null,
    protocole: "ICMP",
    alerte_id: null,
    ...surcharge,
  };
}

describe("LogDetail", () => {
  it("affiche les informations essentielles du log", () => {
    render(<LogDetail log={log()} onFermerPanneau={vi.fn()} />);

    expect(screen.getByRole("heading", { name: /log #8/i })).toBeInTheDocument();
    expect(screen.getByText("Erreur")).toBeInTheDocument();
    expect(screen.getByText("icmp")).toBeInTheDocument();
    expect(screen.getByText("192.168.1.20")).toBeInTheDocument();
    expect(screen.getByText("ICMP")).toBeInTheDocument();
  });

  it("affiche Aucune quand le log n'est associe a aucune alerte", () => {
    render(<LogDetail log={log({ alerte_id: null })} onFermerPanneau={vi.fn()} />);

    expect(screen.getByText("Aucune")).toBeInTheDocument();
  });

  it("affiche le numero de l'alerte associee quand elle existe", () => {
    render(<LogDetail log={log({ alerte_id: 5 })} onFermerPanneau={vi.fn()} />);

    expect(screen.getByText("#5")).toBeInTheDocument();
  });

  it("appelle onFermerPanneau au clic sur Fermer le panneau", async () => {
    const onFermerPanneau = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<LogDetail log={log()} onFermerPanneau={onFermerPanneau} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /fermer le panneau/i }));

    expect(onFermerPanneau).toHaveBeenCalledOnce();
  });
});
