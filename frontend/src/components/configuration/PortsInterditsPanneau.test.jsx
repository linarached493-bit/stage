import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import PortsInterditsPanneau from "./PortsInterditsPanneau";

describe("PortsInterditsPanneau", () => {
  it("affiche les ports interdits actuels", () => {
    render(<PortsInterditsPanneau ports={[22, 23, 3389]} enCours={false} erreur={null} onSoumettre={vi.fn()} />);

    expect(screen.getByLabelText(/ports interdits/i)).toHaveValue("22, 23, 3389");
  });

  it("soumet la liste de ports saisie, convertie en entiers", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(<PortsInterditsPanneau ports={[]} enCours={false} erreur={null} onSoumettre={onSoumettre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/ports interdits/i), "80, 443, 8080");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /enregistrer/i }));

    expect(onSoumettre).toHaveBeenCalledWith([80, 443, 8080]);
  });

  it("ignore les espaces et les valeurs vides lors de la conversion", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(<PortsInterditsPanneau ports={[]} enCours={false} erreur={null} onSoumettre={onSoumettre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/ports interdits/i), "21,, 22 ,");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /enregistrer/i }));

    expect(onSoumettre).toHaveBeenCalledWith([21, 22]);
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <PortsInterditsPanneau
        ports={[]}
        enCours={false}
        erreur="Impossible de modifier les ports interdits."
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/impossible de modifier les ports interdits/i);
  });
});
