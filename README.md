# LogAnalyzer Pro — Pipeline d'Analyse et d'Archivage de Logs


**LogAnalyzer Pro** : outil CLI robuste conçu pour automatiser la supervision des logs applicatifs. 
Développé entièrement avec la bibliothèque standard Python, cette pipeline permet de filtrer les entrées, générer des statistiques détaillées, d'archiver les données et de gérer la rétention des fichiers pour optimiser l'espace disque.
**Objectif** : Supposons qu'on aie des serveurs qui produisent chacun 500 fichiers de logs /jour ; une semaine -> 35 000 à lire si on veux vérifier que tout va bien. On veut coder un *assistant automatique* qui vas analyser tous ces fichiers de logs; fournir des rapports et archiver apres analyse




## Prérequis et Installation
- **Langage :** Python 3.8+ 
- **Dépendances :** Bibliotheque standard (aucune externe) : `os`, `sys`, `json`, `shutil`, `argparse`, `tarfile`, `subprocess`, `platform`, `glob`.
**Installation :**
git clone https://github.com/eje019/LogAnalyzerPro.git

cd LogAnalyzerPro

chmod +x main.py




## Utilisation et commandes :

Toutes les commandes s'exécutent depuis le terminal, à la racine du projet.

### 1- Analyse simple de tous les logs dans le dossier de test :
python main.py --source logs_test

**Explication** : Analyse tous les fichiers .log du dossier `logs_test` sans filtrage. Les rapports sont sauvegardés dans `rapports/` et les archives dans `backups/`.


### 2- Analyse en filtrant uniquement les erreurs
python main.py --source logs_test --niveau ERROR

**Explication** : Ne compte et n'affiche que les lignes contenant "ERROR". Utile pour voir rapidement les problèmes.


### 3- Analyse avec dossier de destination personnalisé pour les archives
python main.py --source logs_test --dest mes_archives

**Explication** : L'archive compressée (.tar.gz) sera déplacée dans le dossier `mes_archives` au lieu de `backups/`.


### 4- Nettoyage automatique des anciens rapports
python main.py --source logs_test --retention 7

**Explication** : Supprime automatiquement les rapports JSON de plus de 7 jours. Par défaut, la rétention est de 30 jours.


### 5- Combinaison de tous les arguments
python main.py --source logs_test --niveau ERROR --dest archives_erreurs --retention 15

**Explication** : Analyse uniquement les erreurs, déplace l'archive dans `archives_erreurs/` et conserve les rapports pendant 15 jours seulement.





## Description des modules

Le projet est découpé en 4 fichiers indépendants, chacun ayant une responsabilité précise.

### analyser.py — Ingestion et analyse
**Rôle** : C'est le moteur d'analyse. Il lit les fichiers .log, filtre selon le niveau choisi (INFO, WARN, ERROR, ALL), et calcule les statistiques :
- Nombre total de lignes
- Répartition par niveau
- Top 5 des messages d'erreur les plus fréquents

**Comment il fonctionne** : Il utilise `glob` pour trouver tous les fichiers .log, puis parcourt chaque ligne. Pour chaque erreur, il stocke le message dans un dictionnaire pour compter ses occurrences. À la fin, il trie les erreurs pour garder les 5 plus fréquentes.

### rapport.py — Génération du rapport JSON
**Rôle** : Il transforme les statistiques en un fichier JSON structuré et lisible.

**Comment il fonctionne** : Il prend les données fournies par `analyser.py` (total lignes, compteurs, Top 5) et les associe à des métadonnées (date, utilisateur, système d'exploitation). Le fichier est nommé `rapport_YYYY-MM-DD.json` et sauvegardé dans le dossier `rapports/`.

### archiver.py — Archivage et nettoyage
**Rôle** : Il gère la compression des logs et la suppression des anciens rapports pour économiser de l'espace disque.

**Comment il fonctionne** :
- **Archivage** : Compresse tous les fichiers .log dans une archive `backup_YYYY-MM-DD.tar.gz` avec la bibliothèque `tarfile`.
- **Déplacement** : Déplace l'archive vers le dossier spécifié par `--dest` (ou `backups/` par défaut).
- **Nettoyage** : Parcourt le dossier `rapports/` et supprime les fichiers JSON plus vieux que le nombre de jours défini par `--retention`.
- **Vérification** : Avant d'archiver, il vérifie l'espace disque disponible via la commande système `df` (Linux/Mac) ou `wmic` (Windows).

### main.py — Orchestration
**Rôle** : C'est le chef d'orchestre. Il appelle les trois autres modules dans le bon ordre et gère les erreurs.

**Comment il fonctionne** :
1. Il récupère les arguments de l'utilisateur (`--source`, `--niveau`, `--dest`, `--retention`)
2. Il lance `analyser.py` dans un sous-processus
3. Il appelle `archiver.py` pour compresser les logs et nettoyer les anciens rapports
4. Si une étape échoue, il affiche un message clair et termine avec `sys.exit(1)`



## Planification automatique avec Cron

Cron est un outil qui permet d'exécuter des programmes automatiquement à des heures précises, sans intervention humaine.

*la ligne :*
0 3 * * 0 /usr/bin/python3 /chemin/vers/loganalyzer/main.py --source /chemin/vers/logs --retention 30


### Explication de la ligne

| Élément | Signification |
|---------|---------------|
| `0 3 * * 0` | **Quand exécuter** : Tous les dimanches à 3h00 du matin |
| `/usr/bin/python3` | **Quoi** : L'interpréteur Python |
| `/chemin/vers/loganalyzer/main.py` | **Quel programme** : Notre orchestrateur |
| `--source /chemin/vers/logs` | **Quel dossier** : L'emplacement des fichiers logs à analyser |
| `--retention 30` | **Conservation** : Garder les rapports 30 jours |

### Comment installer cette planification
1. Ouvre le terminal
2. Tape `crontab -e` (ouvre l'éditeur de Cron)
3. Ajoute la ligne ci-dessus en adaptant les chemins
4. Sauvegarde et quitte

### Vérifier que Cron fonctionne
Cette commande affiche la liste des tâches planifiées.

### Remarque importante
- Sur Windows, on utilise le **Planificateur de tâches** (Task Scheduler) à la place de Cron
- Le chemin vers Python peut varier : utilise `which python3` pour le trouver sur Linux/Mac




## Architecture et Répartition des Rôles 

*main.py* (AMOUZOU-ADOUN Nelson – Intégrateur) : Responsable de l'orchestration principale du programme. Il gère le flux logique entre les modules et implémente une gestion robuste des erreurs fatales via sys.exit(1).

*analyser.py* (N'DAYAKE Jean-Paul – Logs & Analyse) : Gère l'ingestion des fichiers, le filtrage par criticité (ERROR, WARN, INFO) et le calcul des statistiques (notamment le Top 5 des erreurs). Responsable également de la création des jeux de données de test.

*rapport.py* (HESSOUH Floriane – Données & Rapports) : Dédié à la génération du rapport JSON structuré. Il assure la précision des métadonnées (OS, utilisateur, date) et le respect strict du format imposé.

*archiver.py* (YERIMA Thierry – Spécialiste Système) : S'occupe de la compression des logs en .tar.gz, du déplacement des archives et de l'implémentation de la politique de rétention. Il effectue le contrôle de l'espace disque avant toute opération.

*README.md* (AGNILLA Max – Documentation & QA) : Garant de la qualité finale et de la documentation technique. Responsable des tests d'intégration, de la validation des normes de codage (docstrings, shebang) et de la démonstration du projet.
