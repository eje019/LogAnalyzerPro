import argparse

print("Bonjour je suis l'analyseur de LOGS")

analyseur = argparse.ArgumentParser(description="Analyse des fichiers de logs")
analyseur.add_argument("--source")
args = analyseur.parse_args()
analyseur.add_argument("--niveau", default="ALL")

print("Le dossier a analyser est :", args.source, required=True)
