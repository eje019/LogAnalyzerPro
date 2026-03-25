#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée et orchestration du pipeline LogAnalyzer Pro.

Orchestre:
1) Ingestion et analyse (via analyzer.py)
2) Génération du rapport JSON (via rapport.py, appelée par analyzer.py)
3) Archivage et nettoyage (via archiver.py)
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
from typing import List, Optional


def get_project_dir() -> str:
    """
    Retourne le dossier du projet (chemin absolu basé sur __file__).

    Returns:
        str: Chemin absolu du dossier contenant main.py.
    """

    return os.path.dirname(os.path.abspath(__file__))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse les arguments CLI de l'orchestrateur.

    Args:
        argv (Optional[List[str]]): Arguments à parser (par défaut: sys.argv).

    Returns:
        argparse.Namespace: Structure contenant les arguments parsés.
    """

    parser = argparse.ArgumentParser(
        description="LogAnalyzer Pro - orchestration analyse/rapport/archivage"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Chemin du dossier contenant les fichiers logs (.log) à analyser.",
    )
    parser.add_argument(
        "--niveau",
        default="ALL",
        help="Niveau de filtrage: ERROR, WARN, INFO, ALL (défaut: ALL).",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Dossier de destination pour déplacer l'archive (.tar.gz).",
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=30,
        help="Nombre de jours de rétention pour supprimer les anciens rapports (défaut: 30).",
    )
    return parser.parse_args(argv)


def get_log_files(source_dir: str) -> List[str]:
    """
    Récupère la liste des fichiers .log (chemins absolus) dans le dossier source.

    Args:
        source_dir (str): Dossier source (chemin absolu).

    Returns:
        List[str]: Liste des chemins absolus des fichiers .log.
    """

    pattern = os.path.join(source_dir, "*.log")
    return sorted(glob.glob(pattern))


def run_analyzer(analyzer_script: str, source_dir: str, niveau: str) -> None:
    """
    Lance analyzer.py dans un sous-processus.

    Pourquoi un sous-processus:
    - analyzer.py utilise parse_args() au chargement (donc un import direct serait problématique).

    Args:
        analyzer_script (str): Chemin absolu vers analyzer.py.
        source_dir (str): Dossier source (chemin absolu).
        niveau (str): Niveau de filtrage.

    Raises:
        RuntimeError: Si l'exécution échoue.
    """

    cmd = [
        sys.executable,
        analyzer_script,
        "--source",
        source_dir,
        "--niveau",
        niveau,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.CalledProcessError as e:
        # Message explicite pour faciliter le diagnostic.
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        detail = stderr or stdout or str(e)
        raise RuntimeError(f"Echec execution analyzer.py: {detail}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Execution analyzer.py timeout: {e}") from e
    except FileNotFoundError as e:
        raise RuntimeError(f"Execution impossible (script introuvable): {e}") from e


def archive_and_cleanup(
    log_files: List[str],
    dest_dir: Optional[str],
    retention_jours: int,
) -> None:
    """
    Archive les fichiers .log puis nettoie les anciens rapports JSON.

    Args:
        log_files (List[str]): Liste des fichiers .log traités (chemins absolus).
        dest_dir (Optional[str]): Dossier destination pour l'archive (chemin absolu) ou None.
        retention_jours (int): Rétention des rapports en jours.

    Raises:
        RuntimeError: Si archivage ou nettoyage échoue.
    """

    # import local pour mieux encapsuler la gestion d'erreurs.
    try:
        from archiver import creer_archive, nettoyer_anciens_rapports
    except ImportError as e:
        raise RuntimeError(f"Import archiver.py impossible: {e}") from e

    try:
        creer_archive(log_files, dest_dir)
    except Exception as e:  # noqa: BLE001 - pipeline applicatif, message explicite voulu
        raise RuntimeError(f"Echec archivage des logs: {e}") from e

    try:
        nettoyer_anciens_rapports(retention_jours=retention_jours)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Echec nettoyage des anciens rapports: {e}") from e


def main(argv: Optional[List[str]] = None) -> int:
    """
    Point d'entrée principal.

    Args:
        argv (Optional[List[str]]): Arguments CLI (par défaut sys.argv).

    Returns:
        int: Code de sortie (0 succès, 1 erreur fatale).
    """

    project_dir = get_project_dir()
    args = parse_args(argv)

    # Normalisation en chemins absolus.
    source_dir = os.path.abspath(args.source)
    dest_dir = os.path.abspath(args.dest) if args.dest else None

    if not os.path.isdir(source_dir):
        print(f"[ERROR] Le dossier --source n'existe pas ou n'est pas un répertoire: {source_dir}", file=sys.stderr)
        return 1

    analyzer_script = os.path.join(project_dir, "analyzer.py")
    if not os.path.isfile(analyzer_script):
        print(f"[ERROR] analyzer.py introuvable dans le projet: {analyzer_script}", file=sys.stderr)
        return 1

    # Pré-calcul pour l'étape archivage (fichiers réellement présents).
    log_files = get_log_files(source_dir)
    if not log_files:
        print(f"[ERROR] Aucun fichier .log trouvé dans: {source_dir}", file=sys.stderr)
        return 1

    # Etape 1: analyse (et génération du JSON par rapport.py appelé depuis analyzer.py)
    try:
        print("[INFO] Démarrage analyse...")
        run_analyzer(analyzer_script, source_dir=source_dir, niveau=args.niveau)
        print("[INFO] Analyse terminée.")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    # Etape 2 & 3: archivage + nettoyage
    try:
        print("[INFO] Archivage et nettoyage...")
        archive_and_cleanup(
            log_files=log_files,
            dest_dir=dest_dir,
            retention_jours=args.retention,
        )
        print("[INFO] Archivage et nettoyage terminés.")
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    # Conformité: en cas d'erreur fatale -> sys.exit(1).
    sys.exit(main())
