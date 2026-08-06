import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import UtilisateurFormulaire from "./UtilisateurFormulaire";

describe("UtilisateurFormulaire", () => {
  it("demande un mot de passe uniquement si demanderMotDePasse est vrai", () => {
    const { rerender } = render(
      <UtilisateurFormulaire
        idPrefix="creation"
        demanderMotDePasse
        libelleSoumission="Créer"
        enCours={false}
        erreur={null}
        onSoumettre={vi.fn().mockResolvedValue(true)}
      />,
    );
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();

    rerender(
      <UtilisateurFormulaire
        idPrefix="modification"
        demanderMotDePasse={false}
        libelleSoumission="Enregistrer"
        enCours={false}
        erreur={null}
        onSoumettre={vi.fn().mockResolvedValue(true)}
      />,
    );
    expect(screen.queryByLabelText(/mot de passe/i)).not.toBeInTheDocument();
  });

  it("soumet le nom d'utilisateur, le mot de passe et le role_id saisis", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(
      <UtilisateurFormulaire
        idPrefix="creation"
        demanderMotDePasse
        libelleSoumission="Créer"
        enCours={false}
        erreur={null}
        onSoumettre={onSoumettre}
      />,
    );

    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "analyste1");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "MotDePasse1!");
    await utilisateurEvenement.selectOptions(screen.getByLabelText(/rôle/i), "2");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer/i }));

    expect(onSoumettre).toHaveBeenCalledWith({
      nomUtilisateur: "analyste1",
      motDePasse: "MotDePasse1!",
      roleId: 2,
    });
  });

  it("vide le mot de passe apres une creation reussie", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(
      <UtilisateurFormulaire
        idPrefix="creation"
        demanderMotDePasse
        libelleSoumission="Créer"
        enCours={false}
        erreur={null}
        onSoumettre={onSoumettre}
      />,
    );

    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "analyste1");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "MotDePasse1!");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer/i }));

    expect(await screen.findByLabelText(/mot de passe/i)).toHaveValue("");
  });

  it("pre-remplit les valeurs initiales fournies (mode modification)", () => {
    render(
      <UtilisateurFormulaire
        idPrefix="modification"
        valeursInitiales={{ nomUtilisateur: "admin", roleId: 1 }}
        demanderMotDePasse={false}
        libelleSoumission="Enregistrer"
        enCours={false}
        erreur={null}
        onSoumettre={vi.fn().mockResolvedValue(true)}
      />,
    );

    expect(screen.getByLabelText(/nom d'utilisateur/i)).toHaveValue("admin");
    expect(screen.getByLabelText(/rôle/i)).toHaveValue("1");
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <UtilisateurFormulaire
        idPrefix="creation"
        demanderMotDePasse
        libelleSoumission="Créer"
        enCours={false}
        erreur="Impossible de créer cet utilisateur."
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/impossible de créer/i);
  });

  it("desactive le bouton de soumission quand enCours est vrai", () => {
    render(
      <UtilisateurFormulaire
        idPrefix="creation"
        demanderMotDePasse
        libelleSoumission="Créer"
        enCours
        erreur={null}
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /créer/i })).toBeDisabled();
  });
});
