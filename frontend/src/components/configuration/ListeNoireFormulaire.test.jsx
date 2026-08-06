import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ListeNoireFormulaire from "./ListeNoireFormulaire";

describe("ListeNoireFormulaire", () => {
  it("soumet l'adresse IP et le motif saisis", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(<ListeNoireFormulaire enCours={false} erreur={null} onSoumettre={onSoumettre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/adresse ip/i), "203.0.113.66");
    await utilisateurEvenement.type(screen.getByLabelText(/motif/i), "Scan detecte");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /ajouter/i }));

    expect(onSoumettre).toHaveBeenCalledWith({
      adresseIp: "203.0.113.66",
      motifSource: "Scan detecte",
    });
  });

  it("vide les champs apres un ajout reussi", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(<ListeNoireFormulaire enCours={false} erreur={null} onSoumettre={onSoumettre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/adresse ip/i), "203.0.113.66");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /ajouter/i }));

    expect(await screen.findByLabelText(/adresse ip/i)).toHaveValue("");
  });

  it("ne vide pas les champs si l'ajout echoue", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(false);
    const utilisateurEvenement = userEvent.setup();
    render(<ListeNoireFormulaire enCours={false} erreur={null} onSoumettre={onSoumettre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/adresse ip/i), "203.0.113.66");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /ajouter/i }));

    expect(await screen.findByDisplayValue("203.0.113.66")).toBeInTheDocument();
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <ListeNoireFormulaire
        enCours={false}
        erreur="Impossible d'ajouter cette adresse."
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/impossible d'ajouter cette adresse/i);
  });
});
