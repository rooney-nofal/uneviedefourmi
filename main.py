"""
main.py — Une vie de fourmi
============================

La résolution des fourmilières.

Pour chaque fourmilière du dossier `fourmilieres/`, ce script :
    1. lit le fichier et construit la fourmilière ;
    2. calcule le déplacement optimal (nombre MINIMUM d'étapes) ;
    3. vérifie que la solution respecte toutes les règles du brief ;
    4. affiche les étapes au format demandé (+++ E1 +++, f1 - Sv - S1...) ;
    5. enregistre le graphe de la fourmilière (PNG) ;
    6. enregistre l'animation du déplacement, étape par étape (GIF).

Utilisation :
    python main.py                                    # tout résoudre
    python main.py --fichier fourmilieres/fourmiliere_un.txt
    python main.py --sans-animation                   # plus rapide
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from ants import Fourmiliere, Resultat
from visualisation import creer_animation, dessiner_graphe

DOSSIER_FOURMILIERES = Path("fourmilieres")
DOSSIER_RESULTATS = Path("resultats")

# Ordre de traitement : de la plus simple à la plus redoutable.
ORDRE = [
    "fourmiliere_zero", "fourmiliere_un", "fourmiliere_deux",
    "fourmiliere_trois", "fourmiliere_quatre", "fourmiliere_cinq",
    "fourmiliere_3D", "salle_d_at-ant", "La_hormiguera_de_la_muerte",
]


def lister_fichiers(chemin_unique: str | None) -> list[Path]:
    """Les fichiers à résoudre, dans l'ordre croissant de difficulté."""
    if chemin_unique:
        return [Path(chemin_unique)]
    fichiers = {f.stem: f for f in DOSSIER_FOURMILIERES.glob("*.txt")}
    ordonnes = [fichiers.pop(nom) for nom in ORDRE if nom in fichiers]
    return ordonnes + sorted(fichiers.values())    # + éventuels inconnus


def resoudre_fourmiliere(fichier: Path, avec_animation: bool) -> Resultat:
    """Résout une fourmilière et produit tous ses livrables."""
    fourmiliere = Fourmiliere.depuis_fichier(str(fichier))

    largeur = 64
    print("=" * largeur)
    print(fourmiliere)
    print("=" * largeur)

    depart = time.perf_counter()
    resultat = fourmiliere.resoudre()
    duree = time.perf_counter() - depart
    resultat.verifier()                    # filet de sécurité : règles OK ?

    print(resultat.texte())
    print("-" * largeur)
    print(f"Les fourmis ont donc rejoint le dortoir en "
          f"{resultat.nb_etapes} étapes.  (résolu en {duree:.2f} s)\n")

    # Livrables : texte des étapes, graphe PNG, animation GIF.
    (DOSSIER_RESULTATS / "etapes").mkdir(parents=True, exist_ok=True)
    (DOSSIER_RESULTATS / "graphes").mkdir(parents=True, exist_ok=True)
    (DOSSIER_RESULTATS / "animations").mkdir(parents=True, exist_ok=True)

    nom = fourmiliere.nom
    chemin_etapes = DOSSIER_RESULTATS / "etapes" / f"{nom}.txt"
    chemin_etapes.write_text(resultat.texte() + "\n", encoding="utf-8")

    dessiner_graphe(fourmiliere, str(DOSSIER_RESULTATS / "graphes" / f"{nom}.png"))

    if avec_animation:
        creer_animation(resultat,
                        str(DOSSIER_RESULTATS / "animations" / f"{nom}.gif"))

    return resultat


def principal() -> None:
    """Point d'entrée du programme."""
    analyseur = argparse.ArgumentParser(
        description="Une vie de fourmi — résolution optimale des fourmilières.")
    analyseur.add_argument(
        "--fichier", help="ne résoudre qu'une seule fourmilière (chemin du .txt)")
    analyseur.add_argument(
        "--sans-animation", action="store_true",
        help="ne pas générer les GIF animés (exécution plus rapide)")
    arguments = analyseur.parse_args()

    resultats: list[Resultat] = []
    for fichier in lister_fichiers(arguments.fichier):
        resultats.append(
            resoudre_fourmiliere(fichier, not arguments.sans_animation))

    if len(resultats) > 1:                 # petit bilan final
        print("=" * 64)
        print("BILAN")
        print("=" * 64)
        for resultat in resultats:
            f = resultat.fourmiliere
            print(f"  {f.nom:<28} {f.nb_fourmis:>3} fourmis  →  "
                  f"{resultat.nb_etapes:>2} étapes")
        print()
        print("Graphes    : resultats/graphes/    (PNG)")
        print("Étapes     : resultats/etapes/     (TXT)")
        print("Animations : resultats/animations/ (GIF)")


if __name__ == "__main__":
    principal()
