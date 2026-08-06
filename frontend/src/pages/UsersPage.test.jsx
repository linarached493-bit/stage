import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as usersService from "../api/usersService";
import { useAuth } from "../context/AuthContext";
import UsersPage from "./UsersPage";

vi.mock("../api/usersService");
vi.mock("../context/AuthContext");

const UTILISATEUR_LISTE = {
  id: 1,
  nom_utilisateur: "admin",
  role: "Administrateur",
  statut_compte: "actif",
  date_creation: "2026-08-01T09:00:00Z",
};

const UTILISATEUR_DETAIL = {
  id: 1,
  nom_utilisateur: "admin",
  role: "Administrateur",
  statut_compte: "actif",
  date_creation: "2026-08-01T09:00:00Z",
  date_derniere_connexion: null,
};

beforeEach(() => {
  vi.resetAllMocks();
  useAuth.mockReturnValue({ jeton: "jeton-test" });
  usersService.fetchUtilisateurs.mockResolvedValue([UTILISATEUR_LISTE]);
  usersService.fetchUtilisateurDetail.mockResolvedValue(UTILISATEUR_DETAIL);
});

describe("UsersPage", () => {
  it("affiche le chargement puis la liste des utilisateurs", async () => {
    render(<UsersPage />);

    expect(screen.getByText(/chargement des utilisateurs/i)).toBeInTheDocument();
    expect(await screen.findByText("admin")).toBeInTheDocument();
    expect(usersService.fetchUtilisateurs).toHaveBeenCalledWith("jeton-test");
  });

  it("affiche un message d'erreur en cas d'echec reseau du chargement", async () => {
    usersService.fetchUtilisateurs.mockRejectedValue(new Error("réseau indisponible"));

    render(<UsersPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /impossible de récupérer les utilisateurs/i,
    );
  });

  it("cree un utilisateur puis referme le formulaire et rafraichit la liste", async () => {
    usersService.creerUtilisateur.mockResolvedValue({ ...UTILISATEUR_DETAIL, id: 2 });
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer un utilisateur/i }));
    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "analyste1");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "MotDePasse1!");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^créer$/i }));

    expect(usersService.creerUtilisateur).toHaveBeenCalledWith("jeton-test", {
      nomUtilisateur: "analyste1",
      motDePasse: "MotDePasse1!",
      roleId: 1,
    });
    expect(usersService.fetchUtilisateurs).toHaveBeenCalledTimes(2);
    expect(await screen.findByRole("button", { name: /créer un utilisateur/i })).toBeInTheDocument();
  });

  it("affiche un message d'erreur si la creation echoue et laisse le formulaire ouvert", async () => {
    usersService.creerUtilisateur.mockRejectedValue(new Error("409"));
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /créer un utilisateur/i }));
    await utilisateurEvenement.type(screen.getByLabelText(/nom d'utilisateur/i), "admin");
    await utilisateurEvenement.type(screen.getByLabelText(/mot de passe/i), "MotDePasse1!");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^créer$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossible de créer cet utilisateur/i);
    expect(screen.getByLabelText(/nom d'utilisateur/i)).toBeInTheDocument();
  });

  it("affiche le detail d'un utilisateur selectionne", async () => {
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");

    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));

    expect(await screen.findByRole("heading", { name: /^admin$/i })).toBeInTheDocument();
    expect(usersService.fetchUtilisateurDetail).toHaveBeenCalledWith("jeton-test", 1);
  });

  it("modifie l'utilisateur selectionne et rafraichit la liste", async () => {
    usersService.modifierUtilisateur.mockResolvedValue({
      ...UTILISATEUR_DETAIL,
      role: "Lecture seule",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /^admin$/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^modifier$/i }));
    await utilisateurEvenement.selectOptions(screen.getByLabelText(/rôle/i), "3");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /^enregistrer$/i }));

    expect(usersService.modifierUtilisateur).toHaveBeenCalledWith("jeton-test", 1, {
      nomUtilisateur: "admin",
      roleId: 3,
    });
    expect(usersService.fetchUtilisateurs).toHaveBeenCalledTimes(2);
  });

  it("desactive l'utilisateur selectionne", async () => {
    usersService.changerStatutUtilisateur.mockResolvedValue({
      ...UTILISATEUR_DETAIL,
      statut_compte: "desactive",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /^admin$/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(usersService.changerStatutUtilisateur).toHaveBeenCalledWith("jeton-test", 1, "desactive");
    expect(await screen.findByRole("button", { name: /^activer$/i })).toBeInTheDocument();
  });

  it("active un utilisateur desactive selectionne", async () => {
    usersService.fetchUtilisateurDetail.mockResolvedValue({
      ...UTILISATEUR_DETAIL,
      statut_compte: "desactive",
    });
    usersService.changerStatutUtilisateur.mockResolvedValue({
      ...UTILISATEUR_DETAIL,
      statut_compte: "actif",
    });
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /^admin$/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /^activer$/i }));

    expect(usersService.changerStatutUtilisateur).toHaveBeenCalledWith("jeton-test", 1, "actif");
  });

  it("affiche un message d'erreur si une action de traitement echoue", async () => {
    usersService.changerStatutUtilisateur.mockRejectedValue(new Error("500"));
    const utilisateurEvenement = userEvent.setup();
    render(<UsersPage />);
    await screen.findByText("admin");
    await utilisateurEvenement.click(screen.getByRole("button", { name: /détails/i }));
    await screen.findByRole("heading", { name: /^admin$/i });

    await utilisateurEvenement.click(screen.getByRole("button", { name: /désactiver/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/l'action a échoué/i);
  });
});
