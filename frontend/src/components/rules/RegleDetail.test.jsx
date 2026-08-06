import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import RegleDetail from "./RegleDetail";

function regle(surcharge = {}) {
  return {
    id: 4,
    nom: "Port Scan",
    description: "Détection de balayage de ports",
    type_menace: "port_scan",
    gravite: "moyen",
    statut: "active",
    condition_declenchement: { indicateur: "ports_distincts_par_source", seuil: 15, fenetre_secondes: 60 },
    auteur: "admin",
    date_creation: "2026-08-01T09:00:00Z",
    date_derniere_modification: null,
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

describe("RegleDetail", () => {
  it("affiche les informations essentielles de la règle", () => {
    render(<RegleDetail regle={regle()} enCours={false} erreur={null} {...callbacksParDefaut()} />);

    expect(screen.getByRole("heading", { name: /port scan/i })).toBeInTheDocument();
    expect(screen.getByText("port_scan")).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
    expect(screen.getByText(/seuil ≥ 15/)).toBeInTheDocument();
  });

  it("propose Desactiver pour une règle active et appelle onChangerStatut avec inactive", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<RegleDetail regle={regle({ statut: "active" })} enCours={false} erreur={null} {...callbacks} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(callbacks.onChangerStatut).toHaveBeenCalledWith("inactive");
  });

  it("propose Activer pour une règle inactive et appelle onChangerStatut avec active", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<RegleDetail regle={regle({ statut: "inactive" })} enCours={false} erreur={null} {...callbacks} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^activer$/i }));

    expect(callbacks.onChangerStatut).toHaveBeenCalledWith("active");
  });

  it("ouvre le formulaire de modification pre-rempli avec les parametres actuels", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<RegleDetail regle={regle()} enCours={false} erreur={null} {...callbacksParDefaut()} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^modifier$/i }));

    expect(screen.getByLabelText(/^nom$/i)).toHaveValue("Port Scan");
    expect(screen.getByLabelText(/^seuil$/i)).toHaveValue(15);
    expect(screen.getByLabelText(/fenêtre/i)).toHaveValue(60);
  });

  it("modifie la règle puis referme le formulaire apres succes", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<RegleDetail regle={regle()} enCours={false} erreur={null} {...callbacks} />);
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^modifier$/i }));

    await utilisateurEvenement.clear(screen.getByLabelText(/^seuil$/i));
    await utilisateurEvenement.type(screen.getByLabelText(/^seuil$/i), "20");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^enregistrer$/i }));

    expect(callbacks.onModifier).toHaveBeenCalledWith({
      nom: "Port Scan",
      description: "Détection de balayage de ports",
      typeMenace: "port_scan",
      gravite: "moyen",
      conditionDeclenchement: { indicateur: "ports_distincts_par_source", seuil: 20, fenetre_secondes: 60 },
    });
    expect(await screen.findByRole("button", { name: /^modifier$/i })).toBeInTheDocument();
  });

  it("appelle onFermerPanneau au clic sur Fermer le panneau", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<RegleDetail regle={regle()} enCours={false} erreur={null} {...callbacks} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /fermer le panneau/i }));

    expect(callbacks.onFermerPanneau).toHaveBeenCalledOnce();
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <RegleDetail
        regle={regle()}
        enCours={false}
        erreur="L'action a échoué. Veuillez réessayer."
        {...callbacksParDefaut()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/l'action a échoué/i);
  });
});
