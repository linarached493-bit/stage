import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import LogsFiltres from "./LogsFiltres";

const FILTRES_VIDES = {
  niveau: "",
  typeEvenement: "",
  adresseIp: "",
  dateDebut: "",
  dateFin: "",
  recherche: "",
};

describe("LogsFiltres", () => {
  it("appelle onChangerFiltre avec la cle niveau et la valeur selectionnee", async () => {
    const onChangerFiltre = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<LogsFiltres filtres={FILTRES_VIDES} onChangerFiltre={onChangerFiltre} />);

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/^niveau$/i), "erreur");

    expect(onChangerFiltre).toHaveBeenCalledWith("niveau", "erreur");
  });

  it("appelle onChangerFiltre avec la cle typeEvenement et la valeur selectionnee", async () => {
    const onChangerFiltre = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<LogsFiltres filtres={FILTRES_VIDES} onChangerFiltre={onChangerFiltre} />);

    await utilisateurEvenement.selectOptions(screen.getByLabelText(/type d'événement/i), "syn");

    expect(onChangerFiltre).toHaveBeenCalledWith("typeEvenement", "syn");
  });

  it("appelle onChangerFiltre avec la cle recherche a chaque caractere saisi", async () => {
    const onChangerFiltre = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<LogsFiltres filtres={FILTRES_VIDES} onChangerFiltre={onChangerFiltre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/recherche/i), "TCP");

    expect(onChangerFiltre).toHaveBeenCalledWith("recherche", "T");
    expect(onChangerFiltre).toHaveBeenCalledWith("recherche", "C");
    expect(onChangerFiltre).toHaveBeenCalledWith("recherche", "P");
  });

  it("appelle onChangerFiltre avec la cle adresseIp lors de la saisie", async () => {
    const onChangerFiltre = vi.fn();
    const utilisateurEvenement = userEvent.setup();
    render(<LogsFiltres filtres={FILTRES_VIDES} onChangerFiltre={onChangerFiltre} />);

    await utilisateurEvenement.type(screen.getByLabelText(/adresse ip/i), "1");

    expect(onChangerFiltre).toHaveBeenCalledWith("adresseIp", "1");
  });

  it("reflete les valeurs de filtre actuelles", () => {
    render(
      <LogsFiltres
        filtres={{ ...FILTRES_VIDES, niveau: "info", typeEvenement: "icmp", recherche: "abc" }}
        onChangerFiltre={vi.fn()}
      />,
    );

    expect(screen.getByLabelText(/^niveau$/i)).toHaveValue("info");
    expect(screen.getByLabelText(/type d'événement/i)).toHaveValue("icmp");
    expect(screen.getByLabelText(/recherche/i)).toHaveValue("abc");
  });
});
