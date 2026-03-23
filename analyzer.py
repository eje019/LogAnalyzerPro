import argparse
import glob

print("Bonjour je suis l'analyseur de LOGS")

analyseur = argparse.ArgumentParser(description="Analyse des fichiers de logs")
analyseur.add_argument("--source", required=True)

analyseur.add_argument("--niveau", default="ALL")

args = analyseur.parse_args()

fichiers_log = glob.glob(args.source + "/*.log")

# print(f"Le dossier a analyser est :",args.source, "au niveau :" ,args.niveau)

print("Dossier : ", args.source)
print("Niveau : ", args.niveau)
print("Fichiers trouvés :", fichiers_log)


total_lignes = 0
compte_INFO = 0
compte_WARN = 0
compte_ERROR = 0

for fichier in fichiers_log:
    # ouverture du fichier en mode lecturee seule
    with open(fichier, "r", encoding="utf-8") as f:
        lignes = f.readlines() #on lit toutes les lignes du fichier
        # total_lignes = total_lignes + len(lignes) #on ajoute le nombre de lignes au total


        # gestion des filtres pour les niveaux
        for ligne in f:
            total_lignes = total_lignes + 1

            # on check ce que la ligne contient 
            if "INFO" in ligne:
                compte_INFO = compte_INFO + 1
            elif "WARN" in ligne:
                compte_WARN = compte_WARN + 1
            elif "ERROR" in ligne:
                compte_ERROR = compte_ERROR + 1
        # print(fichier, "contient", len(lignes), "lignes") #on dit ce fichier contient combien de lignes d'abord

print("----Resultats----")
print("Total de toutes les lignes :", total_lignes) #on affiche le nombre total en general
print("INFO :", compte_INFO)
print("ERROR :", compte_ERROR)
print("WARN :", compte_WARN)
