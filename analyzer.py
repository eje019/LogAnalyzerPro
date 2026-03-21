import argparse

print("Bonjour je suis l'analyseur de LOGS")

analyseur = argparse.ArgumentParser()
analyseur.add_argument("--source")
args = analyseur.parse_args()

print("Le dossier a analyser est :", args.source)
