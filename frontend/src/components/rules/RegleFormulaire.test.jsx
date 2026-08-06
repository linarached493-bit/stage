import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import RegleFormulaire from "./RegleFormulaire";

const VALEURS_VIDES = {
  nom: "",
  description: "",
  typeMenace: "",
  gravite: "moyen",
  indicateur: "ports_distincts_par_source",
  seuil: 1,
  fenetreSecondes: "",
  typeEvenement: "",
};

describe("RegleFormulaire", () => {
  it("soumet les champs saisis, avec la condition de declenchement construite", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(
      <RegleFormulaire
        idPrefix="creation"
        valeursInitiales={VALEURS_VIDES}
        libelleSoumission="Créer"
        enCours={false}
        erreur={null}
        onSoumettre={onSoumettre}
      />,
    );

    await utilisateurEvenement.type(screen.getByLabelText(/^nom$/i), "SYN Flood");
    await utilisateurEvenement.type(screen.getByLabelText(/^menace$/i), "syn_flood");
    await utilisateurEvenement.selectOptions(screen.getByLabelText(/gravité/i), "eleve");
    await utilisateurEvenement.selectOptions(
      screen.getByLabelText(/indicateur/i),
      "nombre_evenements_par_source",
    );
    await utilisateurEvenement.clear(screen.getByLabelText(/^seuil$/i));
    await utilisateurEvenement.type(screen.getByLabelText(/^seuil$/i), "100");
    await utilisateurEvenement.type(screen.getByLabelText(/fenêtre/i), "10");
    await utilisateurEvenement.type(screen.getByLabelText(/type d'événement/i), "syn");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer/i }));

    expect(onSoumettre).toHaveBeenCalledWith({
      nom: "SYN Flood",
      description: null,
      typeMenace: "syn_flood",
      gravite: "eleve",
      conditionDeclenchement: {
        indicateur: "nombre_evenements_par_source",
        seuil: 100,
        fenetre_secondes: 10,
        type_evenement: "syn",
      },
    });
  });

  it("omet fenetre_secondes et type_evenement de la condition si laisses vides", async () => {
    const onSoumettre = vi.fn().mockResolvedValue(true);
    const utilisateurEvenement = userEvent.setup();
    render(
      <RegleFormulaire
        idPrefix="creation"
        valeursInitiales={VALEURS_VIDES}
        libelleSoumission="Créer"
        enCours={false}
        erreur={null}
        onSoumettre={onSoumettre}
      />,
    );

    await utilisateurEvenement.type(screen.getByLabelText(/^nom$/i), "Port Scan");
    await utilisateurEvenement.type(screen.getByLabelText(/^menace$/i), "port_scan");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer/i }));

    expect(onSoumettre).toHaveBeenCalledWith({
      nom: "Port Scan",
      description: null,
      typeMenace: "port_scan",
      gravite: "moyen",
      conditionDeclenchement: { indicateur: "ports_distincts_par_source", seuil: 1 },
    });
  });

  it("pre-remplit les valeurs initiales fournies (mode modification)", () => {
    render(
      <RegleFormulaire
        idPrefix="modification"
        valeursInitiales={{
          nom: "Port Scan",
          description: "Détection de balayage de ports",
          typeMenace: "port_scan",
          gravite: "moyen",
          indicateur: "ports_distincts_par_source",
          seuil: 15,
          fenetreSecondes: 60,
          typeEvenement: "",
        }}
        libelleSoumission="Enregistrer"
        enCours={false}
        erreur={null}
        onSoumettre={vi.fn().mockResolvedValue(true)}
      />,
    );

    expect(screen.getByLabelText(/^nom$/i)).toHaveValue("Port Scan");
    expect(screen.getByLabelText(/description/i)).toHaveValue("Détection de balayage de ports");
    expect(screen.getByLabelText(/^seuil$/i)).toHaveValue(15);
    expect(screen.getByLabelText(/fenêtre/i)).toHaveValue(60);
  });

  it("affiche le message d'erreur fourni", () => {
    render(
      <RegleFormulaire
        idPrefix="creation"
        valeursInitiales={VALEURS_VIDES}
        libelleSoumission="Créer"
        enCours={false}
        erreur="Impossible de créer cette règle."
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/impossible de créer/i);
  });

  it("desactive le bouton de soumission quand enCours est vrai", () => {
    render(
      <RegleFormulaire
        idPrefix="creation"
        valeursInitiales={VALEURS_VIDES}
        libelleSoumission="Créer"
        enCours
        erreur={null}
        onSoumettre={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /créer/i })).toBeDisabled();
  });
});
