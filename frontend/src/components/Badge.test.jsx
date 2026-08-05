import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Badge from "./Badge";

describe("Badge", () => {
  it("affiche son contenu", () => {
    render(<Badge tone="danger">Élevé</Badge>);

    expect(screen.getByText("Élevé")).toBeInTheDocument();
  });

  it("applique la classe correspondant au tone fourni", () => {
    render(<Badge tone="danger">Élevé</Badge>);

    expect(screen.getByText("Élevé")).toHaveClass("badge--danger");
  });

  it("utilise le tone neutre par defaut", () => {
    render(<Badge>Neutre</Badge>);

    expect(screen.getByText("Neutre")).toHaveClass("badge--neutre");
  });
});
