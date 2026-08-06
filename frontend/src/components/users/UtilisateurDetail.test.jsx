import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import UtilisateurDetail from "./UtilisateurDetail";

function utilisateur(surcharge = {}) {
  return {
    id: 3,
    nom_utilisateur: "analyste1",
    role: "Analyste sécurité",
    statut_compte: "actif",
    date_creation: "2026-08-01T09:00:00Z",
    date_derniere_connexion: null,
    ...surcharge,
  };
}

function callbacksParDefaut() {
  return {
    onFermerPanneau: vi.fn(),
    onModifier: vi.fn().mockResolvedValue(true),
    onChangerStatut: vi.fn().mockResolvedValue(true),
  };
}

describe("UtilisateurDetail", () => {
  it("affiche les informations essentielles de l'utilisateur", () => {
    render(<UtilisateurDetail utilisateur={utilisateur()} enCours={false} erreur={null} {...callbacksParDefaut()} />);

    expect(screen.getByRole("heading", { name: /analyste1/i })).toBeInTheDocument();
    expect(screen.getByText("Analyste sécurité")).toBeInTheDocument();
    expect(screen.getByText("Actif")).toBeInTheDocument();
    expect(screen.getByText(/jamais connecté/i)).toBeInTheDocument();
  });

  it("affiche la date de derniere connexion quand elle existe", () => {
    render(
      <UtilisateurDetail
        utilisateur={utilisateur({ date_derniere_connexion: "2026-08-05T08:00:00Z" })}
        enCours={false}
        erreur={null}
        {...callbacksParDefaut()}
      />,
    );

    expect(screen.queryByText(/jamais connecté/i)).not.toBeInTheDocument();
  });

  it("propose Desactiver pour un utilisateur actif et appelle onChangerStatut avec desactive", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(
      <UtilisateurDetail utilisateur={utilisateur({ statut_compte: "actif" })} enCours={false} erreur={null} {...callbacks} />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(callbacks.onChangerStatut).toHaveBeenCalledWith("desactive");
  });

  it("propose Activer pour un utilisateur desactive et appelle onChangerStatut avec actif", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(
      <UtilisateurDetail
        utilisateur={utilisateur({ statut_compte: "desactive" })}
        enCours={false}
        erreur={null}
        {...callbacks}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^activer$/i }));

    expect(callbacks.onChangerStatut).toHaveBeenCalledWith("actif");
  });

  it("ouvre le formulaire de modification pre-rempli avec le role actuel", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(
      <UtilisateurDetail
        utilisateur={utilisateur({ role: "Analyste sécurité" })}
        enCours={false}
        erreur={null}
        {...callbacksParDefaut()}
      />,
    );

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^modifier$/i }));

    expect(screen.getByLabelText(/nom d'utilisateur/i)).toHaveValue("analyste1");
    expect(screen.getByLabelText(/rôle/i)).toHaveValue("2");
  });

  it("modifie l'utilisateur puis referme le formulaire apres succes", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<UtilisateurDetail utilisateur={utilisateur()} enCours={false} erreur={null} {...callbacks} />);
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^modifier$/i }));

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/rôle/i), "1");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^enregistrer$/i }));

    expect(callbacks.onModifier).toHaveBeenCalledWith({ nomUtilisateur: "analyste1", roleId: 1 });
    expect(await screen.findByRole("button", { name: /^modifier$/i })).toBeInTheDocument();
  });

  it("appelle onFermerPanneau au clic sur Fermer le panneau", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<UtilisateurDetail utilisateur={utilisateur()} enCours={false} erreur={null} {...callbacks} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /fermer le panneau/i }));

    expect(callbacks.onFermerPanneau).toHaveBeenCalledOnce();
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <UtilisateurDetail
        utilisateur={utilisateur()}
        enCours={false}
        erreur="L'action a échoué. Veuillez réessayer."
        {...callbacksParDefaut()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/l'action a échoué/i);
  });
});
