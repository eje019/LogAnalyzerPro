
#Module 2 — Génération du Rapport JSON.
#Ce module prend les statistiques calculées par analyser.py
#et les écrit dans un fichier rapport_YYYY-MM-DD.json horodaté.

#horodaté -->

import json
import os
import platform
from datetime import datetime


def construire_rapport(total_lignes, compte_INFO, compte_WARN, compte_ERROR, top5, fichiers_log, dossier_source):
    """
    Construit le dictionnaire Python qui représente le rapport complet.
    S'adapte aux variables produites directement par analyser.py.

    Arguments:
        total_lignes (int)  : Nombre total de lignes lues dans tous les fichiers.
        compte_INFO (int)   : Nombre de lignes de niveau INFO.
        compte_WARN (int)   : Nombre de lignes de niveau WARN.
        compte_ERROR (int)  : Nombre de lignes de niveau ERROR.
        top5 (list)         : Liste de tuples (message, count) — les 5 erreurs les + fréquentes.
        fichiers_log (list) : Liste des chemins des fichiers .log analysés.
        dossier_source (str): Chemin du dossier source analysé.

    Retourne:
        dict: Le rapport complet structuré, prêt à être converti en JSON.
    """
    # datetime.now() donne la date et l'heure actuelles
    # strftime() formate la date dans le format souhaité
    date_generation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Récupération de l'utilisateur courant (USER sur Linux, USERNAME sur Windows)
    utilisateur = os.environ.get("USER") or os.environ.get("USERNAME") or "inconnu"

    # Détection du système d'exploitation
    systeme = platform.system() + " " + platform.release()

    # Conversion du top5 (liste de tuples) en liste de dicts pour le JSON
    # Avant : [("message", 5), ...]  ->  Après : [{"message": "...", "occurrences": 5}, ...]
    top5_formate = [
        {"message": message, "occurrences": count}
        for message, count in top5
    ]

    # On construit le dictionnaire en respectant EXACTEMENT la structure imposée
    rapport = {
        "metadata": {
            "date": date_generation,
            "utilisateur": utilisateur,
            "os": systeme,
            "source": os.path.abspath(dossier_source),
        },
        "statistiques": {
            "total_lignes": total_lignes,
            "par_niveau": {
                "ERROR": compte_ERROR,
                "WARN": compte_WARN,
                "INFO": compte_INFO,
            },
            "top5_erreurs": top5_formate,
        },
        "fichiers_traites": fichiers_log,
    }

    return rapport


def generer_rapport_json(rapport, dossier_rapports):
    """
    Écrit le rapport dans un fichier JSON horodaté.
    Le fichier est créé dans le dossier 'rapports/' avec un nom unique par date.

    Arguments:
        rapport (dict): Le dictionnaire du rapport à sauvegarder.
        dossier_rapports (str): Chemin absolu vers le dossier où écrire le rapport.

    Retourne:
        str: Chemin absolu du fichier rapport créé.

    Lève:
        OSError: Si le dossier ne peut pas être créé ou le fichier écrit.
    """
    # On génère le nom du fichier avec la date du jour
    # Ex : rapport_2024-04-01.json
    date_du_jour = datetime.now().strftime("%Y-%m-%d")
    nom_fichier = f"rapport_{date_du_jour}.json"

    # os.path.abspath(__file__) donne le chemin absolu de CE fichier (rapport.py)
    # os.path.dirname() remonte au dossier du projet
    # Ainsi les chemins sont toujours absolus, peu importe d'où on lance le script
    dossier_projet = os.path.dirname(os.path.abspath(__file__))
    dossier_rapports_abs = os.path.join(dossier_projet, os.path.basename(dossier_rapports))
    os.makedirs(dossier_rapports_abs, exist_ok=True)
    chemin_rapport = os.path.join(dossier_rapports_abs, nom_fichier)

    # On écrit le dictionnaire Python dans le fichier JSON
    # indent=4 rend le fichier lisible (avec indentation)
    # ensure_ascii=False permet d'écrire les accents correctement
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=4, ensure_ascii=False)

    print(f"[OK] Rapport généré : {chemin_rapport}")
    return chemin_rapport