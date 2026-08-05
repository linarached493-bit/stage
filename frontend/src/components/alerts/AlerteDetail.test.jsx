import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import AlerteDetail from "./AlerteDetail";

function alerte(surcharge = {}) {
  return {
    id: 7,
    type_menace: "syn_flood",
    ip_source: "10.0.0.5",
    ip_destination: "10.0.0.1",
    gravite: "eleve",
    statut_traitement: "nouvelle",
    horodatage_detection: "2026-08-05T10:00:00Z",
    regle: "SYN Flood",
    historique: [],
    ...surcharge,
  };
}

function callbacksParDefaut() {
  return {
    onFermerPanneau: vi.fn(),
    onAcquitter: vi.fn().mockResolvedValue(true),
    onFermer: vi.fn().mockResolvedValue(true),
    onCommenter: vi.fn().mockResolvedValue(true),
  };
}

describe("AlerteDetail", () => {
  it("affiche les informations essentielles de l'alerte", () => {
    render(<AlerteDetail alerte={alerte()} enCours={false} erreur={null} {...callbacksParDefaut()} />);

    expect(screen.getByRole("heading", { name: /alerte #7/i })).toBeInTheDocument();
    expect(screen.getByText("syn_flood")).toBeInTheDocument();
    expect(screen.getByText("SYN Flood")).toBeInTheDocument();
    expect(screen.getByText("10.0.0.5")).toBeInTheDocument();
    expect(screen.getByText("10.0.0.1")).toBeInTheDocument();
  });

  it("affiche l'historique des evenements", () => {
    render(
      <AlerteDetail
        alerte={alerte({
          historique: [
            {
              statut: "en_cours",
              commentaire: "Analyse en cours",
              utilisateur: "analyste1",
              horodatage: "2026-08-05T11:00:00Z",
            },
          ],
        })}
        enCours={false}
        erreur={null}
        {...callbacksParDefaut()}
      />,
    );

    expect(screen.getByText(/analyste1/)).toBeInTheDocument();
    expect(screen.getByText(/analyse en cours/i)).toBeInTheDocument();
  });

  it("propose l'acquittement seulement pour une alerte nouvelle", () => {
    const { rerender } = render(
      <AlerteDetail
        alerte={alerte({ statut_traitement: "nouvelle" })}
        enCours={false}
        erreur={null}
        {...callbacksParDefaut()}
      />,
    );
    expect(screen.getByRole("button", { name: /^acquitter$/i })).toBeInTheDocument();

    rerender(
      <AlerteDetail
        alerte={alerte({ statut_traitement: "en_cours" })}
        enCours={false}
        erreur={null}
        {...callbacksParDefaut()}
      />,
    );
    expect(screen.queryByRole("button", { name: /^acquitter$/i })).not.toBeInTheDocument();
  });

  it("ne propose pas de fermeture pour une alerte deja fermee", () => {
    render(
      <AlerteDetail
        alerte={alerte({ statut_traitement: "traitee" })}
        enCours={false}
        erreur={null}
        {...callbacksParDefaut()}
      />,
    );

    expect(screen.queryByRole("button", { name: /^fermer$/i })).not.toBeInTheDocument();
  });

  it("acquitte l'alerte avec le commentaire saisi puis vide le champ", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(
      <AlerteDetail alerte={alerte({ statut_traitement: "nouvelle" })} enCours={false} erreur={null} {...callbacks} />,
    );

    await utilisateurEvenement.type(
      screen.getByLabelText(/commentaire \(optionnel\)/i),
      "Vérifié, rien d'anormal",
    );
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^acquitter$/i }));

    expect(callbacks.onAcquitter).toHaveBeenCalledWith("Vérifié, rien d'anormal");
    expect(await screen.findByLabelText(/commentaire \(optionnel\)/i)).toHaveValue("");
  });

  it("ferme l'alerte avec le statut final et le commentaire choisis", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(
      <AlerteDetail
        alerte={alerte({ statut_traitement: "en_cours" })}
        enCours={false}
        erreur={null}
        {...callbacks}
      />,
    );

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/statut final/i), "faux_positif");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^fermer$/i }));

    expect(callbacks.onFermer).toHaveBeenCalledWith("faux_positif", undefined);
  });

  it("ajoute un commentaire et vide le champ apres succes", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(
      <AlerteDetail alerte={alerte()} enCours={false} erreur={null} {...callbacks} />,
    );

    await utilisateurEvenement.type(screen.getByLabelText(/^commentaire$/i), "RAS");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^commenter$/i }));

    expect(callbacks.onCommenter).toHaveBeenCalledWith("RAS");
    expect(await screen.findByLabelText(/^commentaire$/i)).toHaveValue("");
  });

  it("ne vide pas le champ de commentaire si l'action echoue", async () => {
    const callbacks = { ...callbacksParDefaut(), onCommenter: vi.fn().mockResolvedValue(false) };
    const utilisateurEvenement = userEvent.setup();
    render(<AlerteDetail alerte={alerte()} enCours={false} erreur={null} {...callbacks} />);

    await utilisateurEvenement.type(screen.getByLabelText(/^commentaire$/i), "RAS");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^commenter$/i }));

    expect(await screen.findByDisplayValue("RAS")).toBeInTheDocument();
  });

  it("desactive le bouton Commenter tant que le champ est vide", () => {
    render(<AlerteDetail alerte={alerte()} enCours={false} erreur={null} {...callbacksParDefaut()} />);

    expect(screen.getByRole("button", { name: /^commenter$/i })).toBeDisabled();
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <AlerteDetail
        alerte={alerte()}
        enCours={false}
        erreur="L'action a échoué. Veuillez réessayer."
        {...callbacksParDefaut()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/l'action a échoué/i);
  });

  it("appelle onFermerPanneau au clic sur le bouton Fermer le panneau", async () => {
    const callbacks = callbacksParDefaut();
    const utilisateurEvenement = userEvent.setup();
    render(<AlerteDetail alerte={alerte()} enCours={false} erreur={null} {...callbacks} />);

    await utilisateurEvenement.click(screen.getByRole("button", { name: /fermer le panneau/i }));

    expect(callbacks.onFermerPanneau).toHaveBeenCalledOnce();
  });
});
