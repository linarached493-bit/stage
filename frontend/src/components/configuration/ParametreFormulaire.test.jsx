import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ParametreFormulaire from "./ParametreFormulaire";

describe("ParametreFormulaire", () => {
  it("pre-remplit la valeur et la description actuelles", () => {
    render(
      <ParametreFormulaire
        nomParametre="ports_interdits"
        valeursInitiales={{ valeur: "[22, 23]", description: "Ports sensibles" }}
        enCours={false}
        erreur={null}
        onAnnuler={vi.fn()}
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByLabelText(/valeur/i)).toHaveValue("[22, 23]");
    expect(screen.getByLabelText(/description/i)).toHaveValue("Ports sensibles");
  });

  it("soumet la nouvelle valeur et description saisies", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(
      <ParametreFormulaire
        nomParametre="ports_interdits"
        valeursInitiales={{ valeur: "", description: "" }}
        enCours={false}
        erreur={null}
        onAnnuler={vi.fn()}
        onSoumettre={onSoumettre}
      />,
    );

    await utilisateurEvenement.type(screen.getByLabelText(/valeur/i), "[80, 443]");
    await utilisateurEvenement.type(screen.getByLabelText(/description/i), "Ports web");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /enregistrer/i }));

    expect(onSoumettre).toHaveBeenCalledWith({ valeur: "[80, 443]", description: "Ports web" });
  });

  it("appelle onAnnuler au clic sur Fermer le panneau", async () => {
    const onAnnuler = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(
      <ParametreFormulaire
        nomParametre="ports_interdits"
        valeursInitiales={{ valeur: "", description: "" }}
        enCours={false}
        erreur={null}
        onAnnuler={onAnnuler}
        onSoumettre={vi.fn()}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /fermer le panneau/i }));

    expect(onAnnuler).toHaveBeenCalledOnce();
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <ParametreFormulaire
        nomParametre="ports_interdits"
        valeursInitiales={{ valeur: "", description: "" }}
        enCours={false}
        erreur="Impossible de modifier ce paramètre."
        onAnnuler={vi.fn()}
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/impossible de modifier/i);
  });

  it("desactive le bouton Enregistrer quand enCours est vrai", () => {
    render(
      <ParametreFormulaire
        nomParametre="ports_interdits"
        valeursInitiales={{ valeur: "", description: "" }}
        enCours
        erreur={null}
        onAnnuler={vi.fn()}
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /enregistrer/i })).toBeDisabled();
  });
});
