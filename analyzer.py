import argparse
import glob
print("\n")
print("Bonjour je suis l'analyseur de LOGS")

#creartion de l'analyseur d'arguments
analyseur = argparse.ArgumentParser(description="Analyse des fichiers de logs")

#argument source pour specifier le dossier a analyser obligatoirement sinon erreur
analyseur.add_argument("--source", required=True)

#argument niveau pour specifier le miveau de filtrage, ALL par defaut
analyseur.add_argument("--niveau", default="ALL")

# recuperation des arguments tapés par user; stockees dans l'objet args
# acces via args.source et args.niveau
args = analyseur.parse_args()

# recherche de tous les fichiers .log dans le dossier source
fichiers_log = glob.glob(args.source + "/*.log")



# print(f"Le dossier a analyser est :",args.source, "au niveau :" ,args.niveau)
niveau = args.niveau 

print("Dossier : ", args.source)
print("Niveau : ", niveau)
print("Fichiers trouvés :", fichiers_log)


total_lignes = 0
compte_INFO = 0
compte_WARN = 0
compte_ERROR = 0
erreurs = {} #dictionnaire pour compter chaque message d'erreur 

for fichier in fichiers_log:
    # ouverture du fichier en mode lecturee seule
    with open(fichier, "r", encoding="utf-8") as f:
        # lignes = f.readlines() #on lit toutes les lignes du fichier
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

                morceaux = ligne.split() #la ligne est decoupee

                message = " ".join(morceaux[3:])
                
                if message in erreurs:
                    erreurs[message] = erreurs[message] + 1
                else:
                    erreurs[message] = 1




#5 des erreurs les plus frequentes

#copie du dictionaire des erreurs pour pouvoir supprimer les erreurs au fur et à mesure sans perdre l'original
erreurs_restantes = dict(erreurs)

top5 = [] #tableau qui va contenir les 5 meilleures erreurs
# chaque element sera un tuple (message, nombre)

for i in range(5):
    if not erreurs_restantes:
        break
    
    message_max = None
    nombre_max = -1 # -1 car on n'a encore rien trouve
    
    for message, nombre in erreurs_restantes.items():

        #on parcourt toutes les erreurs pour trouver le plus grand nombre        if nombre > nombre_max:
            nombre_max = nombre
            message_max = message
        
    # on a l'erreur avec le plus grand nombre
    # pn l'ajoute dans le tableau top5 sous forme de couple (message, nombre)
    top5.append((message_max, nombre_max))

    # on supprime cette erreur du dictionnaire et on le retire pour le prochain tour
    del erreurs_restantes[message_max]
print("\n")
print("----Resultats----")
print("Total de toutes les lignes :", total_lignes) #on affiche le nombre total en general
# print("INFO :", compte_INFO)
# print("ERROR :", compte_ERROR)
# print("WARN :", compte_WARN)

if niveau == "ALL" or niveau == "INFO":
    print("INFO :", compte_INFO)
if niveau == "ALL" or niveau == "WARN":
    print("WARN :", compte_WARN)
if niveau == "ALL" or niveau == "ERROR":
    print("ERROR :", compte_ERROR)


print("\n----Top 5 des messages derreur----")
if top5:
    for i, (message, count) in enumerate(top5, 1):
        print(f"{i}. {message} ({count} fois)")
else:
    print("Aucune erreur trouvée")

import rapport
contenu_rapport = rapport.construire_rapport(
    total_lignes, compte_INFO, compte_WARN, compte_ERROR,
    top5, fichiers_log, args.source
)
rapport.generer_rapport_json(contenu_rapport, dossier_rapports="rapports")