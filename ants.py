"""
ants.py — Une vie de fourmi
============================

Ce module contient les classes et fonctions permettant le bon déplacement
des fourmis au sein de la fourmilière :

    - Salle       : une salle de la fourmilière (nom + capacité)
    - Fourmi      : une fourmi (numéro + position + trajet)
    - Fourmiliere : la fourmilière complète (salles, tunnels, fourmis)
                    avec le solveur qui calcule le nombre MINIMUM d'étapes.

Méthode de résolution (optimale) :
    On déplie la fourmilière dans le temps ("graphe temporel") : chaque
    salle est dupliquée pour chaque instant t = 0, 1, 2, ... T.
    Se déplacer d'une salle à une autre devient un arc entre l'instant t
    et l'instant t+1. Les capacités des salles et des tunnels deviennent
    des capacités d'arcs. Faire passer F fourmis du vestibule (t = 0)
    au dortoir (t = T) revient alors à un problème de FLOT MAXIMUM,
    résolu par NetworkX. On cherche le plus petit T pour lequel le flot
    atteint F : ce T est, par construction, le minimum d'étapes possible.

Règles respectées (cf. le brief) :
    - une salle ne contient jamais plus de fourmis que sa capacité
      (1 par défaut, X si la salle est notée S{X}) ;
    - le vestibule (Sv) et le dortoir (Sd) ont une capacité illimitée ;
    - un tunnel ne laisse passer qu'UNE fourmi par étape ;
    - une fourmi peut entrer dans une salle si celle-ci a de la place,
      ou si une fourmi qui l'occupe est en train de partir ;
    - à chaque étape, une fourmi attend ou se déplace vers une salle
      adjacente ; les tunnels sont traversés instantanément.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import networkx as nx


# ---------------------------------------------------------------------------
# Les classes du modèle
# ---------------------------------------------------------------------------

@dataclass
class Salle:
    """Une salle de la fourmilière.

    Attributs :
        nom      : identifiant de la salle ("Sv", "S1", ..., "Sd")
        capacite : nombre maximum de fourmis présentes en même temps
                   (None = capacité illimitée, cas de Sv et Sd)
    """

    nom: str
    capacite: int | None = 1

    @property
    def illimitee(self) -> bool:
        """Vrai si la salle peut accueillir un nombre illimité de fourmis."""
        return self.capacite is None

    def __str__(self) -> str:
        if self.illimitee:
            return f"{self.nom} (capacité illimitée)"
        return f"{self.nom} (capacité {self.capacite})"


@dataclass
class Fourmi:
    """Une fourmi de la colonie.

    Attributs :
        numero   : numéro de la fourmi (1, 2, ..., F) → affichée "f1", "f2"...
        position : nom de la salle où elle se trouve actuellement
        trajet   : liste des salles occupées à chaque étape (t = 0, 1, ...),
                   utilisée ensuite pour l'animation.
    """

    numero: int
    position: str = "Sv"
    trajet: list[str] = field(default_factory=list)

    @property
    def nom(self) -> str:
        """Nom affiché de la fourmi, ex. 'f3'."""
        return f"f{self.numero}"

    def deplacer(self, destination: str) -> None:
        """Déplace la fourmi vers la salle `destination`."""
        self.position = destination

    def __str__(self) -> str:
        return f"{self.nom} ({self.position})"


@dataclass
class Deplacement:
    """Un déplacement élémentaire : une fourmi passe d'une salle à une autre."""

    fourmi: str    # ex. "f1"
    origine: str   # ex. "Sv"
    arrivee: str   # ex. "S1"

    def __str__(self) -> str:
        return f"{self.fourmi} - {self.origine} - {self.arrivee}"


# ---------------------------------------------------------------------------
# La fourmilière et son solveur
# ---------------------------------------------------------------------------

class Fourmiliere:
    """La fourmilière : ses salles, ses tunnels, ses fourmis, et le solveur."""

    # Motifs de lecture des fichiers .txt
    _MOTIF_FOURMIS = re.compile(r"^[fF]\s*=\s*(\d+)$")
    _MOTIF_SALLE = re.compile(r"^(\w+)\s*\{\s*(\d+)\s*\}$")
    _MOTIF_TUNNEL = re.compile(r"^(\w+)\s*-\s*(\w+)$")

    def __init__(self, nom: str, nb_fourmis: int) -> None:
        self.nom = nom
        self.nb_fourmis = nb_fourmis
        # Sv et Sd existent toujours, avec une capacité illimitée.
        self.salles: dict[str, Salle] = {
            "Sv": Salle("Sv", capacite=None),
            "Sd": Salle("Sd", capacite=None),
        }
        self.tunnels: list[tuple[str, str]] = []
        self.fourmis: list[Fourmi] = [
            Fourmi(numero=i + 1) for i in range(nb_fourmis)
        ]

    # ------------------------------------------------------------------
    # Lecture d'un fichier fourmilière
    # ------------------------------------------------------------------

    @classmethod
    def depuis_fichier(cls, chemin: str) -> "Fourmiliere":
        """Construit une Fourmiliere à partir d'un fichier .txt du brief."""
        nom = chemin.replace("\\", "/").split("/")[-1].removesuffix(".txt")
        nb_fourmis: int | None = None
        salles: list[Salle] = []
        tunnels: list[tuple[str, str]] = []

        with open(chemin, encoding="utf-8") as fichier:
            for ligne in fichier:
                ligne = ligne.strip()          # espaces, \r et \n éventuels
                if not ligne:
                    continue
                if (m := cls._MOTIF_FOURMIS.match(ligne)):
                    nb_fourmis = int(m.group(1))
                elif (m := cls._MOTIF_TUNNEL.match(ligne)):
                    tunnels.append((m.group(1), m.group(2)))
                elif (m := cls._MOTIF_SALLE.match(ligne)):
                    salles.append(Salle(m.group(1), int(m.group(2))))
                else:                          # salle simple, ex. "S9"
                    salles.append(Salle(ligne, 1))

        if nb_fourmis is None:
            raise ValueError(f"{chemin} : nombre de fourmis introuvable (f=...)")

        fourmiliere = cls(nom, nb_fourmis)
        for salle in salles:
            fourmiliere.ajouter_salle(salle)
        for u, v in tunnels:
            fourmiliere.ajouter_tunnel(u, v)
        return fourmiliere

    def ajouter_salle(self, salle: Salle) -> None:
        """Ajoute une salle (Sv et Sd sont déjà présentes)."""
        if salle.nom not in ("Sv", "Sd"):
            self.salles[salle.nom] = salle

    def ajouter_tunnel(self, u: str, v: str) -> None:
        """Ajoute un tunnel entre les salles u et v (sans doublon)."""
        for nom in (u, v):
            if nom not in self.salles:      # salle citée mais non déclarée
                self.salles[nom] = Salle(nom, 1)
        if (u, v) not in self.tunnels and (v, u) not in self.tunnels:
            self.tunnels.append((u, v))

    # ------------------------------------------------------------------
    # Représentation en graphe (NetworkX)
    # ------------------------------------------------------------------

    def graphe(self) -> nx.Graph:
        """La fourmilière sous forme de graphe : salles = sommets,
        tunnels = arêtes."""
        g = nx.Graph()
        for salle in self.salles.values():
            g.add_node(salle.nom, capacite=salle.capacite)
        g.add_edges_from(self.tunnels)
        return g

    # ------------------------------------------------------------------
    # Le solveur : graphe temporel + flot maximum
    # ------------------------------------------------------------------

    def _construire_reseau_temporel(self, horizon: int) -> nx.DiGraph:
        """Construit le graphe temporel pour `horizon` étapes.

        Chaque salle S est dupliquée en deux sommets par instant t :
        (S, 'e', t) = entrée et (S, 's', t) = sortie, reliés par un arc
        dont la capacité est celle de la salle : c'est ce qui limite le
        nombre de fourmis présentes en même temps.

        Chaque tunnel devient, pour chaque instant, un petit sommet
        intermédiaire de capacité 1 : c'est ce qui impose la règle
        « une seule fourmi par tunnel et par étape », dans un sens
        comme dans l'autre.

        Attendre dans une salle = un arc (S, 's', t) → (S, 'e', t+1).
        Le dortoir est absorbant : on y entre, on n'en sort plus.
        """
        F = self.nb_fourmis        # F joue le rôle de « capacité infinie »
        reseau = nx.DiGraph()

        # Les F fourmis sont injectées dans le vestibule à l'instant 0.
        reseau.add_edge("SOURCE", ("Sv", "e", 0), capacity=F)

        for t in range(horizon + 1):
            for salle in self.salles.values():
                if salle.nom == "Sd":
                    # Toute fourmi entrée au dortoir a atteint l'objectif.
                    reseau.add_edge(("Sd", "e", t), "PUITS", capacity=F)
                    continue
                capacite = F if salle.illimitee else salle.capacite
                reseau.add_edge((salle.nom, "e", t), (salle.nom, "s", t),
                                capacity=capacite)
                if t < horizon:    # attendre sur place jusqu'à l'instant t+1
                    reseau.add_edge((salle.nom, "s", t),
                                    (salle.nom, "e", t + 1), capacity=F)

        for t in range(horizon):
            for u, v in self.tunnels:
                # Le « sas » du tunnel : une seule fourmi par étape.
                sas_e = ("tunnel", u, v, t, "e")
                sas_s = ("tunnel", u, v, t, "s")
                reseau.add_edge(sas_e, sas_s, capacity=1)
                for depart, arrivee in ((u, v), (v, u)):
                    if depart != "Sd":               # on ne quitte pas le dortoir
                        reseau.add_edge((depart, "s", t), sas_e, capacity=1)
                    reseau.add_edge(sas_s, (arrivee, "e", t + 1), capacity=1)

        return reseau

    def _flot_maximum(self, horizon: int):
        """Valeur et détail du flot maximum pour un horizon donné."""
        reseau = self._construire_reseau_temporel(horizon)
        return nx.maximum_flow(reseau, "SOURCE", "PUITS")

    def resoudre(self) -> "Resultat":
        """Calcule le déplacement optimal de toutes les fourmis.

        1. borne basse : la longueur du plus court chemin Sv → Sd ;
        2. on augmente l'horizon T tant que le flot maximum < F ;
        3. le premier T qui fait passer F fourmis est LE minimum d'étapes ;
        4. on traduit le flot en déplacements individuels de fourmis.
        """
        graphe = self.graphe()
        if not nx.has_path(graphe, "Sv", "Sd"):
            raise ValueError(f"{self.nom} : aucun chemin entre Sv et Sd !")

        horizon = nx.shortest_path_length(graphe, "Sv", "Sd")
        limite = horizon + 2 * self.nb_fourmis + len(self.salles)

        while horizon <= limite:
            valeur, flot = self._flot_maximum(horizon)
            if valeur >= self.nb_fourmis:
                etapes = self._traduire_flot(flot, horizon)
                return Resultat(self, etapes)
            horizon += 1

        raise RuntimeError(f"{self.nom} : aucune solution trouvée "
                           f"(horizon exploré jusqu'à {limite}).")

    # ------------------------------------------------------------------
    # Traduction du flot en déplacements de fourmis
    # ------------------------------------------------------------------

    def _mouvements_par_etape(self, flot: dict,
                              horizon: int) -> list[list[tuple[str, str]]]:
        """Extrait du flot, pour chaque étape, la liste des mouvements
        (salle de départ, salle d'arrivée)."""
        mouvements: list[list[tuple[str, str]]] = [[] for _ in range(horizon)]
        for t in range(horizon):
            for u, v in self.tunnels:
                sas_e = ("tunnel", u, v, t, "e")
                sas_s = ("tunnel", u, v, t, "s")
                if flot.get(sas_e, {}).get(sas_s, 0) < 1:
                    continue                    # tunnel inutilisé à l'étape t
                origine = next(dep for dep in (u, v)
                               if flot.get((dep, "s", t), {}).get(sas_e, 0) > 0)
                arrivee = next(arr for arr in (u, v)
                               if flot[sas_s].get((arr, "e", t + 1), 0) > 0)
                if origine != arrivee:          # sinon : simple attente
                    mouvements[t].append((origine, arrivee))
        return mouvements

    def _traduire_flot(self, flot: dict, horizon: int) -> list[list[Deplacement]]:
        """Attribue chaque mouvement du flot à une fourmi précise.

        À chaque étape, si k fourmis doivent quitter une salle, on choisit
        les k fourmis de plus petit numéro présentes dans cette salle :
        le résultat est déterministe et facile à suivre.
        """
        for fourmi in self.fourmis:             # position de départ
            fourmi.position = "Sv"
            fourmi.trajet = ["Sv"]

        etapes: list[list[Deplacement]] = []
        for mouvements in self._mouvements_par_etape(flot, horizon):
            deplacements: list[Deplacement] = []

            # Regrouper les mouvements par salle de départ.
            par_origine: dict[str, list[str]] = {}
            for origine, arrivee in mouvements:
                par_origine.setdefault(origine, []).append(arrivee)

            # Choisir les fourmis qui partent (plus petits numéros d'abord).
            affectations: list[tuple[Fourmi, str]] = []
            for origine, arrivees in par_origine.items():
                presentes = sorted(
                    (f for f in self.fourmis if f.position == origine),
                    key=lambda f: f.numero,
                )
                for fourmi, arrivee in zip(presentes, sorted(arrivees)):
                    affectations.append((fourmi, arrivee))

            # Tous les déplacements d'une étape sont simultanés.
            for fourmi, arrivee in affectations:
                deplacements.append(
                    Deplacement(fourmi.nom, fourmi.position, arrivee))
                fourmi.deplacer(arrivee)

            for fourmi in self.fourmis:         # mémoriser pour l'animation
                fourmi.trajet.append(fourmi.position)

            deplacements.sort(key=lambda d: int(d.fourmi[1:]))
            etapes.append(deplacements)

        return etapes

    def __str__(self) -> str:
        return (f"Fourmilière « {self.nom} » : {self.nb_fourmis} fourmis, "
                f"{len(self.salles)} salles, {len(self.tunnels)} tunnels")


# ---------------------------------------------------------------------------
# Le résultat d'une résolution
# ---------------------------------------------------------------------------

class Resultat:
    """Le déplacement complet des fourmis, étape par étape."""

    def __init__(self, fourmiliere: Fourmiliere,
                 etapes: list[list[Deplacement]]) -> None:
        self.fourmiliere = fourmiliere
        self.etapes = etapes

    @property
    def nb_etapes(self) -> int:
        """Nombre total d'étapes de la solution (le minimum possible)."""
        return len(self.etapes)

    def texte(self) -> str:
        """Les étapes au format du brief : +++ E1 +++, f1 - Sv - S1, ..."""
        lignes: list[str] = []
        for numero, deplacements in enumerate(self.etapes, start=1):
            lignes.append(f"+++ E{numero} +++")
            lignes.extend(str(d) for d in deplacements)
        return "\n".join(lignes)

    def verifier(self) -> None:
        """Contrôle que la solution respecte TOUTES les règles du brief.

        Lève une AssertionError si une règle est violée. Cette fonction est
        notre filet de sécurité : le solveur est optimal par construction,
        mais on re-vérifie chaque règle, étape par étape, par prudence.
        """
        f = self.fourmiliere
        tunnels = {frozenset(t) for t in f.tunnels}
        positions = {fourmi.nom: "Sv" for fourmi in f.fourmis}

        for numero, deplacements in enumerate(self.etapes, start=1):
            tunnels_occupes: set[frozenset] = set()
            for d in deplacements:
                assert positions[d.fourmi] == d.origine, \
                    f"E{numero} : {d.fourmi} n'est pas dans {d.origine}"
                assert frozenset((d.origine, d.arrivee)) in tunnels, \
                    f"E{numero} : aucun tunnel {d.origine} - {d.arrivee}"
                assert frozenset((d.origine, d.arrivee)) not in tunnels_occupes, \
                    f"E{numero} : tunnel {d.origine} - {d.arrivee} déjà utilisé"
                tunnels_occupes.add(frozenset((d.origine, d.arrivee)))
                positions[d.fourmi] = d.arrivee

            for salle in f.salles.values():     # capacités respectées ?
                if salle.illimitee:
                    continue
                occupants = sum(1 for p in positions.values() if p == salle.nom)
                assert occupants <= salle.capacite, \
                    f"E{numero} : {salle.nom} dépasse sa capacité"

        assert all(p == "Sd" for p in positions.values()), \
            "Toutes les fourmis ne sont pas au dortoir !"

    def __str__(self) -> str:
        return (f"{self.fourmiliere.nom} : {self.fourmiliere.nb_fourmis} "
                f"fourmis au dortoir en {self.nb_etapes} étapes")
