# Exemple imaginaire
import argparse

# On crée le "menu"
analyseur = argparse.ArgumentParser(description="Outil d'analyse de logs")
analyseur.add_argument("--couleur", help="La couleur préférée")

# L'utilisateur tape : python script.py --couleur rouge
args = analyseur.parse_args()
print(args.couleur)  # Affiche "rouge"