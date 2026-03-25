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
# Analyse simple de tous les logs dans le dossier de test
python main.py --source ./logs_test

# Analyse filtrée sur les erreurs avec nettoyage des rapports de plus de 7 jours
python3 main.py --source ./logs_test --niveau ERROR --retention 7

## 
Le script s'exécute via la console. Voici les arguments supportés :

--source (Obligatoire) : Spécifie le chemin vers le dossier contenant les fichiers .log à analyser.

--niveau (Optionnel) : Définit le niveau de filtrage des logs. Les options acceptées sont ERROR, WARN, INFO ou ALL. Par défaut, le script analyse tous les niveaux (ALL).

--dest (Optionnel) : Indique le dossier de destination pour le stockage des archives .tar.gz. Par défaut, les archives sont placées dans le dossier ./backups.

--retention (Optionnel) : Détermine la politique de conservation en nombre de jours avant la suppression automatique des anciens rapports JSON. La valeur par défaut est fixée à 30 jours.


# Structure du Répertoire

loganalyzer/
├── main.py             # Point d'entrée principal
├── analyser.py         # Module d'ingestion et analyse (Stats & Filtres)
├── rapport.py          # Module de génération JSON
├── archiver.py         # Module d'archivage et de nettoyage
├── logs_test/          # 3 fichiers de logs (min. 20 lignes chacun)
├── rapports/           # Dossier cible des rapports JSON (auto-généré)
├── backups/            # Dossier cible des archives .tar.gz (auto-généré)
└── README.md           # Documentation technique



## 6. Planification Automatique (Cron)
Pour automatiser l'analyse chaque **dimanche à 03h00**, ajoutez cette ligne à votre configuration Cron (`crontab -e`) :
00 03 * * 0 /usr/bin/python3 /votre/chemin/LogAnalyzerPro/main.py --source /votre/chemin logs--retention 30       



## 5. Spécifications Techniques

# Structure du Rapport JSON
Chaque analyse génère un fichier `rapport_YYYY-MM-DD.json` contenant :
* **metadata** : Date/heure, utilisateur (`os.environ`), OS (`platform`) et chemin source absolu.
* **statistiques** : Total de lignes, décompte par niveau (`ERROR`, `WARN`, `INFO`) et Top 5 des messages d'erreurs uniques.
* **fichiers_traites** : Liste exhaustive des fichiers `.log` analysés.

# Sécurité et Robustesse
* **Espace Disque :** Vérification via la commande système `df` (via `subprocess`) avant tout archivage pour prévenir la saturation.
* **Chemins Absolus :** Utilisation systématique de `os.path.abspath(__file__)` pour garantir la portabilité du script.
* **Gestion d'Erreurs :** Utilisation de blocs `try/except` et de `sys.exit(1)` avec messages explicites en cas d'échec critique.




## Architecture et Répartition des Rôles (Groupe 4)
Le projet est structuré en modules indépendants pour garantir une maintenance facile et une séparation des responsabilités :

main.py (Étudiant A – Intégrateur) : Responsable de l'orchestration principale du programme. Il gère le flux logique entre les modules et implémente une gestion robuste des erreurs fatales via sys.exit(1).

analyser.py (Étudiant B – Logs & Analyse) : Gère l'ingestion des fichiers, le filtrage par criticité (ERROR, WARN, INFO) et le calcul des statistiques (notamment le Top 5 des erreurs). Responsable également de la création des jeux de données de test.

rapport.py (Étudiant C – Données & Rapports) : Dédié à la génération du rapport JSON structuré. Il assure la précision des métadonnées (OS, utilisateur, date) et le respect strict du format imposé.

archiver.py (Étudiant D – Spécialiste Système) : S'occupe de la compression des logs en .tar.gz, du déplacement des archives et de l'implémentation de la politique de rétention. Il effectue le contrôle de l'espace disque avant toute opération.

README.md (Étudiant E – Documentation & QA) : Garant de la qualité finale et de la documentation technique. Responsable des tests d'intégration, de la validation des normes de codage (docstrings, shebang) et de la démonstration du projet.
