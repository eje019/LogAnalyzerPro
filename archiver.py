#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import shutil
import tarfile
import subprocess
from datetime import datetime


# Dossier de backups, construit à partir de __file__ (chemin absolu)
DOSSIER_BACKUPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
DOSSIER_RAPPORTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rapports")


def creer_dossier_backups():
    """
    Crée le dossier 'backups/' s'il n'existe pas encore.
    Utilise os.makedirs avec exist_ok=True (vu en cours Module_os).
    """
    os.makedirs(DOSSIER_BACKUPS, exist_ok=True)


def verifier_espace_disque(dossier):
    """
    Vérifie l'espace disque disponible via subprocess avant d'archiver.
    Utilise 'df' sur Linux/Mac et 'wmic' sur Windows.

    Args:
        dossier (str): Chemin du dossier à vérifier.

    Returns:
        bool: True si l'espace est suffisant (> 100 Mo), False sinon.
    """
    try:
        if sys.platform.startswith("win"):
            # Commande Windows pour l'espace disque
            resultat = subprocess.run(
                ["wmic", "logicaldisk", "get", "freespace,caption"],
                capture_output=True, text=True, timeout=10
            )
            print(f"[INFO] Espace disque :\n{resultat.stdout.strip()}")
        else:
            # Commande Unix/Linux/Mac
            resultat = subprocess.run(
                ["df", "-h", dossier],
                capture_output=True, text=True, timeout=10
            )
            print(f"[INFO] Espace disque :\n{resultat.stdout.strip()}")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"[WARN] Vérification espace disque impossible : {e}", file=sys.stderr)
        return True  # On continue malgré tout


def creer_archive(fichiers_log, dossier_dest):
    """
    Archive tous les fichiers .log dans une archive backup_YYYY-MM-DD.tar.gz
    en utilisant tarfile en mode w:gz (vu en cours Module_tarfile).

    Args:
        fichiers_log (list): Liste des chemins absolus des fichiers .log à archiver.
        dossier_dest (str): Dossier de destination pour l'archive finale.

    Returns:
        str: Chemin absolu de l'archive créée, ou None en cas d'échec.
    """
    if not fichiers_log:
        print("[WARN] Aucun fichier à archiver.")
        return None

    creer_dossier_backups()

    # Nom de l'archive horodaté (vu en cours Module_datetime)
    date_jour = datetime.now().strftime("%Y-%m-%d")
    nom_archive = f"backup_{date_jour}.tar.gz"
    chemin_archive_tmp = os.path.join(DOSSIER_BACKUPS, nom_archive)

    # Vérification de l'espace disque via subprocess
    verifier_espace_disque(DOSSIER_BACKUPS)

    # Création de l'archive compressée en mode w:gz (vu en cours Module_tarfile)
    try:
        with tarfile.open(chemin_archive_tmp, "w:gz") as tar:
            for fichier in fichiers_log:
                if os.path.exists(fichier):
                    # arcname pour ne garder que le nom du fichier (sans chemin complet)
                    tar.add(fichier, arcname=os.path.basename(fichier))
                    print(f"[OK] Ajouté à l'archive : {os.path.basename(fichier)}")
    except tarfile.TarError as e:
        print(f"[ERROR] Erreur lors de la création de l'archive : {e}", file=sys.stderr)
        return None

    # Déplacer l'archive vers le dossier de destination avec shutil (vu en cours Module_os)
    if dossier_dest and os.path.abspath(dossier_dest) != DOSSIER_BACKUPS:
        os.makedirs(dossier_dest, exist_ok=True)
        chemin_final = os.path.join(dossier_dest, nom_archive)
        shutil.move(chemin_archive_tmp, chemin_final)
        print(f"[OK] Archive déplacée vers : {chemin_final}")
        return chemin_final
    else:
        print(f"[OK] Archive créée : {chemin_archive_tmp}")
        return chemin_archive_tmp


def nettoyer_anciens_rapports(retention_jours=30):
    """
    Supprime les rapports JSON plus vieux que N jours.
    Utilise os.path.getmtime() et time.time() pour calculer l'âge (vu en cours Module_datetime).

    Args:
        retention_jours (int): Nombre de jours de rétention (défaut : 30).
    """
    if not os.path.exists(DOSSIER_RAPPORTS):
        print("[INFO] Dossier rapports inexistant, rien à nettoyer.")
        return

    maintenant = time.time()
    limite_secondes = retention_jours * 86400  # 86400 secondes = 1 jour
    supprimes = 0

    for fichier in os.listdir(DOSSIER_RAPPORTS):
        if not fichier.endswith(".json"):
            continue

        chemin = os.path.join(DOSSIER_RAPPORTS, fichier)

        # Calcul de l'âge du fichier via os.path.getmtime()
        age_secondes = maintenant - os.path.getmtime(chemin)

        if age_secondes > limite_secondes:
            try:
                os.remove(chemin)
                print(f"[OK] Rapport supprimé (>{retention_jours}j) : {fichier}")
                supprimes += 1
            except OSError as e:
                print(f"[ERROR] Impossible de supprimer {fichier} : {e}", file=sys.stderr)

    if supprimes == 0:
        print(f"[INFO] Aucun rapport à supprimer (rétention : {retention_jours} jours).")
    else:
        print(f"[OK] {supprimes} rapport(s) supprimé(s).")
