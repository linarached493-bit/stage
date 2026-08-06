import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RepartitionTable from "./RepartitionTable";

describe("RepartitionTable", () => {
  it("affiche un message si la répartition est vide", () => {
    render(
      <RepartitionTable titre="Alertes par gravité" repartition={{}} libelleColonneCle="Gravité" />,
    );

    expect(screen.getByRole("heading", { name: /alertes par gravité/i })).toBeInTheDocument();
    expect(screen.getByText(/aucune donnée/i)).toBeInTheDocument();
  });

  it("affiche une ligne par entrée de la répartition, avec sa valeur", () => {
    render(
      <RepartitionTable
        titre="Alertes par type de menace"
        repartition={{ port_scan: 3, syn_flood: 2 }}
        libelleColonneCle="Type de menace"
      />,
    );

    expect(screen.getByText("port_scan")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("syn_flood")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("utilise rendreCle pour personnaliser l'affichage d'une clé", () => {
    render(
      <RepartitionTable
        titre="Alertes par gravité"
        repartition={{ eleve: 1 }}
        libelleColonneCle="Gravité"
        rendreCle={(cle) => <span data-testid="cle-personnalisee">{cle.toUpperCase()}</span>}
      />,
    );

    expect(screen.getByTestId("cle-personnalisee")).toHaveTextContent("ELEVE");
  });
});
