"""
visualisation.py — Une vie de fourmi
=====================================

Tout ce qui se voit :

    - dessiner_graphe(...)  : la fourmilière en image (PNG), salles et tunnels ;
    - creer_animation(...)  : le déplacement des fourmis, étape par étape,
                              en GIF animé avec un mouvement fluide.

Le graphe est disposé « en profondeur » : le vestibule (surface) à gauche,
le dortoir (fond de la fourmilière) à droite, et chaque salle placée selon
sa distance au vestibule — comme une vraie coupe de fourmilière.
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle

from ants import Fourmiliere, Resultat

# --- La palette de la fourmilière -----------------------------------------
COULEUR_FOND = "#f6efe2"        # sable clair
COULEUR_TERRE = "#e8d9be"       # halo derrière les salles
COULEUR_SALLE = "#f0c987"       # salle ordinaire
COULEUR_BORD = "#8a5a2b"        # contour des salles (terre)
COULEUR_VESTIBULE = "#7fbf6b"   # vert herbe (près de la surface)
COULEUR_DORTOIR = "#4a5d8f"     # bleu nuit (le fond, le repos)
COULEUR_TUNNEL = "#b08d57"      # brun des tunnels
COULEUR_FOURMI = "#b2331f"      # rouge des fourmis... rouges
COULEUR_TEXTE = "#4a3320"


# ---------------------------------------------------------------------------
# Disposition des salles
# ---------------------------------------------------------------------------

def calculer_positions(fourmiliere: Fourmiliere) -> dict[str, tuple[float, float]]:
    """Place chaque salle : x = distance au vestibule, y = répartition
    verticale des salles d'une même « profondeur »."""
    graphe = fourmiliere.graphe()
    distances = nx.shortest_path_length(graphe, "Sv")
    profondeur_max = max(distances.values())

    # Les salles injoignables depuis Sv (rare) sont placées tout à droite.
    for nom in graphe.nodes:
        distances.setdefault(nom, profondeur_max + 1)
    distances["Sd"] = max(distances["Sd"], profondeur_max)  # Sd tout au fond

    colonnes: dict[int, list[str]] = {}
    for nom, distance in distances.items():
        colonnes.setdefault(distance, []).append(nom)

    positions: dict[str, tuple[float, float]] = {}
    for distance, noms in colonnes.items():
        noms.sort(key=_cle_tri)
        for rang, nom in enumerate(noms):
            y = (rang - (len(noms) - 1) / 2) * 1.6
            positions[nom] = (distance * 1.8, y)
    return positions


def _cle_tri(nom: str) -> tuple[int, str]:
    """Trie S2 avant S10, et garde Sv / Sd à part."""
    chiffres = "".join(c for c in nom if c.isdigit())
    return (int(chiffres) if chiffres else -1, nom)


def _rayon(fourmiliere: Fourmiliere, nom: str) -> float:
    """Rayon d'une salle : plus elle est grande, plus le cercle est large."""
    salle = fourmiliere.salles[nom]
    if salle.illimitee:
        return 0.52
    return 0.28 + 0.018 * min(salle.capacite, 10)


# ---------------------------------------------------------------------------
# Tunnels courbes : deux salles alignées verticalement seraient reliées par
# une droite qui TRAVERSE les salles intermédiaires. On courbe donc ces
# tunnels (courbe de Bézier), et les fourmis suivront la même courbe.
# ---------------------------------------------------------------------------

def calculer_courbures(fourmiliere: Fourmiliere,
                       positions: dict) -> dict[frozenset, float]:
    """Courbure de chaque tunnel « vertical » (0 = tunnel droit).
    Les courbures alternent à gauche / à droite pour rester lisibles."""
    courbures: dict[frozenset, float] = {}
    sens = 1
    for u, v in fourmiliere.tunnels:
        (x1, y1), (x2, y2) = positions[u], positions[v]
        if abs(x1 - x2) < 1e-9 and abs(y1 - y2) > 1.7:   # même colonne, non voisins
            courbures[frozenset((u, v))] = 0.38 * sens
            sens = -sens
    return courbures


def _point_courbe(a: tuple[float, float], b: tuple[float, float],
                  courbure: float, t: float) -> tuple[float, float]:
    """Point à la fraction t (0 → 1) de la courbe de Bézier reliant a à b,
    dont le sommet est décalé perpendiculairement selon `courbure`."""
    (xa, ya), (xb, yb) = a, b
    cx = (xa + xb) / 2 - courbure * (yb - ya)      # point de contrôle
    cy = (ya + yb) / 2 + courbure * (xb - xa)
    x = (1 - t) ** 2 * xa + 2 * (1 - t) * t * cx + t ** 2 * xb
    y = (1 - t) ** 2 * ya + 2 * (1 - t) * t * cy + t ** 2 * yb
    return x, y


# ---------------------------------------------------------------------------
# Dessin du décor (commun au PNG et à l'animation)
# ---------------------------------------------------------------------------

def _dessiner_decor(ax, fourmiliere: Fourmiliere,
                    positions: dict[str, tuple[float, float]],
                    courbures: dict[frozenset, float]) -> None:
    """Dessine les tunnels (droits ou courbes) puis les salles."""
    for u, v in fourmiliere.tunnels:            # tunnels d'abord (dessous)
        a, b = positions[u], positions[v]
        courbure = courbures.get(frozenset((u, v)), 0.0)
        chemin = [_point_courbe(a, b, courbure, t / 24) for t in range(25)]
        ax.plot([p[0] for p in chemin], [p[1] for p in chemin],
                color=COULEUR_TUNNEL, linewidth=3.2, alpha=0.75,
                zorder=1, solid_capstyle="round")

    for nom, (x, y) in positions.items():       # salles ensuite (dessus)
        salle = fourmiliere.salles[nom]
        rayon = _rayon(fourmiliere, nom)
        if nom == "Sv":
            couleur = COULEUR_VESTIBULE
        elif nom == "Sd":
            couleur = COULEUR_DORTOIR
        else:
            couleur = COULEUR_SALLE
        ax.add_patch(Circle((x, y), rayon * 1.18, color=COULEUR_TERRE,
                            zorder=2, linewidth=0))
        ax.add_patch(Circle((x, y), rayon, facecolor=couleur,
                            edgecolor=COULEUR_BORD, linewidth=2.0, zorder=3))

        # Nom au-dessus, capacité en dessous : les fourmis ne cachent rien.
        ax.text(x, y + rayon + 0.08, nom, ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=COULEUR_TEXTE, zorder=5)
        if not salle.illimitee and salle.capacite > 1:
            ax.text(x, y - rayon - 0.08, f"{salle.capacite} places",
                    ha="center", va="top", fontsize=7.5,
                    color=COULEUR_BORD, zorder=5)

    ax.set_aspect("equal")
    ax.axis("off")


def _cadre(positions: dict[str, tuple[float, float]]):
    """Taille de figure et limites d'axes adaptées à la fourmilière."""
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    marge = 1.1
    largeur = max(xs) - min(xs) + 2 * marge
    hauteur = max(ys) - min(ys) + 2 * marge
    echelle = 1.35
    taille = (max(6.5, largeur * echelle), max(4.5, hauteur * echelle))
    limites = (min(xs) - marge, max(xs) + marge,
               min(ys) - marge, max(ys) + marge + 0.4)
    return taille, limites


# ---------------------------------------------------------------------------
# 1) Le graphe statique de la fourmilière
# ---------------------------------------------------------------------------

def dessiner_graphe(fourmiliere: Fourmiliere, chemin_png: str) -> None:
    """Enregistre la fourmilière sous forme de graphe dans un fichier PNG."""
    positions = calculer_positions(fourmiliere)
    courbures = calculer_courbures(fourmiliere, positions)
    taille, (x0, x1, y0, y1) = _cadre(positions)

    figure, ax = plt.subplots(figsize=taille)
    figure.patch.set_facecolor(COULEUR_FOND)
    ax.set_facecolor(COULEUR_FOND)
    _dessiner_decor(ax, fourmiliere, positions, courbures)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_title(f"Fourmilière « {fourmiliere.nom} » — "
                 f"{fourmiliere.nb_fourmis} fourmis",
                 fontsize=13, fontweight="bold", color=COULEUR_TEXTE, pad=12)
    figure.tight_layout()
    figure.savefig(chemin_png, dpi=150, facecolor=COULEUR_FOND)
    plt.close(figure)


# ---------------------------------------------------------------------------
# 2) L'animation du déplacement, étape par étape
# ---------------------------------------------------------------------------

def _places_dans_salle(centre: tuple[float, float], rayon: float,
                       nombre: int) -> list[tuple[float, float]]:
    """Répartit `nombre` fourmis à l'intérieur d'une salle, en spirale
    régulière (angle d'or) pour qu'elles ne se chevauchent jamais."""
    cx, cy = centre
    places = []
    for i in range(nombre):
        r = rayon * 0.72 * math.sqrt((i + 0.5) / max(nombre, 1))
        angle = i * 2.399963                    # angle d'or (radians)
        places.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return places


def _positions_fourmis(fourmiliere: Fourmiliere, instant: int,
                       positions: dict) -> dict[str, tuple[float, float]]:
    """Coordonnées (x, y) de chaque fourmi à un instant donné."""
    par_salle: dict[str, list[str]] = {}
    for fourmi in fourmiliere.fourmis:
        salle = fourmi.trajet[instant]
        par_salle.setdefault(salle, []).append(fourmi.nom)

    coordonnees: dict[str, tuple[float, float]] = {}
    for salle, noms in par_salle.items():
        noms.sort(key=lambda n: int(n[1:]))
        places = _places_dans_salle(positions[salle],
                                    _rayon(fourmiliere, salle), len(noms))
        for nom, place in zip(noms, places):
            coordonnees[nom] = place
    return coordonnees


def creer_animation(resultat: Resultat, chemin_gif: str,
                    images_par_etape: int | None = None) -> None:
    """Crée le GIF animé : les fourmis glissent de salle en salle,
    étape par étape, avec compteur d'étapes et de fourmis arrivées."""
    fourmiliere = resultat.fourmiliere
    nb_etapes = resultat.nb_etapes
    positions = calculer_positions(fourmiliere)
    courbures = calculer_courbures(fourmiliere, positions)
    taille, (x0, x1, y0, y1) = _cadre(positions)

    if images_par_etape is None:                # fluide, mais raisonnable
        images_par_etape = 10 if nb_etapes <= 12 else 6

    # Coordonnées de chaque fourmi à chaque instant t = 0 .. nb_etapes.
    instants = [_positions_fourmis(fourmiliere, t, positions)
                for t in range(nb_etapes + 1)]
    pause = images_par_etape                    # arrêt sur image au début/fin
    total_images = pause + nb_etapes * images_par_etape + pause

    figure, ax = plt.subplots(figsize=taille)
    figure.patch.set_facecolor(COULEUR_FOND)
    ax.set_facecolor(COULEUR_FOND)
    _dessiner_decor(ax, fourmiliere, positions, courbures)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)

    points = ax.scatter([], [], s=42, color=COULEUR_FOURMI,
                        edgecolors="#3d1208", linewidths=0.6, zorder=6)
    titre = ax.set_title("", fontsize=13, fontweight="bold",
                         color=COULEUR_TEXTE, pad=12)

    def _lisser(x: float) -> float:
        """Adoucit le mouvement (départ et arrivée en douceur)."""
        return x * x * (3 - 2 * x)

    def _image(numero_image: int):
        # À quel moment de la solution correspond cette image ?
        avancement = (numero_image - pause) / images_par_etape
        avancement = min(max(avancement, 0.0), float(nb_etapes))
        etape = min(int(avancement), nb_etapes - 1)
        fraction = _lisser(avancement - etape)

        avant, apres = instants[etape], instants[etape + 1]
        coordonnees = []
        arrivees = 0
        for fourmi in fourmiliere.fourmis:
            salle_avant = fourmi.trajet[etape]
            salle_apres = fourmi.trajet[etape + 1]
            courbure = courbures.get(frozenset((salle_avant, salle_apres)), 0.0)
            coordonnees.append(_point_courbe(avant[fourmi.nom],
                                             apres[fourmi.nom],
                                             courbure, fraction))
            if fourmi.trajet[etape + 1] == "Sd" and fraction >= 0.5:
                arrivees += 1
            elif fourmi.trajet[etape] == "Sd":
                arrivees += 1

        points.set_offsets(coordonnees)
        titre.set_text(
            f"« {fourmiliere.nom} » — Étape {etape + 1}/{nb_etapes}   "
            f"|   Fourmis au dortoir : {arrivees}/{fourmiliere.nb_fourmis}")
        return points, titre

    animation = FuncAnimation(figure, _image, frames=total_images,
                              interval=1000 // 12, blit=False)
    animation.save(chemin_gif, writer=PillowWriter(fps=12),
                   savefig_kwargs={"facecolor": COULEUR_FOND})
    plt.close(figure)
