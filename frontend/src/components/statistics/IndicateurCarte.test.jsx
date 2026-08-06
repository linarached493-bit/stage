import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IndicateurCarte from "./IndicateurCarte";

describe("IndicateurCarte", () => {
  it("affiche la valeur et le libellé fournis", () => {
    render(<IndicateurCarte libelle="Alertes au total" valeur={12} />);

    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("Alertes au total")).toBeInTheDocument();
  });

  it("affiche correctement une valeur nulle", () => {
    render(<IndicateurCarte libelle="Règles inactives" valeur={0} />);

    expect(screen.getByText("0")).toBeInTheDocument();
  });
});
