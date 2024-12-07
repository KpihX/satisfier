# 🎯 Satisfier - Optimisation des choix d'activités 

Satisfier est un outil d'optimisation puissant conçu pour résoudre le problème d'affectation des élèves aux activités en fonction de leurs préférences. Il utilise des algorithmes d'optimisation pour maximiser la satisfaction globale tout en respectant les contraintes de capacité. ✨

## 📑 Table des matières 
- [📥 Installation](#installation)
- [📂 Structure du projet](#structure-du-projet)
- [💻 Modes d'utilisation](#modes-dutilisation)
  - [🖥️ Interface graphique (GUI)](#interface-graphique-gui)
  - [⌨️ Mode ligne de commande](#mode-ligne-de-commande)
  - [🔧 Mode script Python](#mode-script-python)
- [📋 Format des fichiers d'entrée](#format-des-fichiers-dentrée)
- [🛠️ Outils de formatage](#outils-de-formatage)
- [📊 Fichiers de sortie](#fichiers-de-sortie)
- [🔨 Compilation en exécutable](#compilation-en-exécutable)
- [💡 Exemples d'utilisation](#exemples-dutilisation)
- [📄 Licence](#licence)

## 🚀 Installation 

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/satisfier.git
cd satisfier
```

2. Créez un environnement virtuel (recommandé) 🌟 :
```bash
python -m venv env
source env/bin/activate  # Sur Linux/Mac
env\Scripts\activate     # Sur Windows
```

3. Installez les dépendances 📦 :
```bash
pip install -r requirements.txt
```

## 📂 Structure du projet 

```
satisfier/
├── data/              # 📊 Fichiers d'entrée
│   ├── activities.csv     # 📋 Exemple de fichier d'activités
│   ├── choices.csv        # 📝 Exemple de fichier de choix brut
│   ├── choices.xls        # 📑 Même contenu que choices.csv mais en Excel
│   └── choices_formatted.csv  # ✨ Fichier de choix formaté
├── format/            # 🔧 Scripts de formatage
│   ├── excel_to_csv.py    # 🔄 Conversion Excel vers CSV
│   └── format_choices.py  # 🎯 Formatage des fichiers de choix
├── models/            # 📐 Modèles de données
│   └── data_models.py     # 🏗️ Classes de base
├── solver/            # 🧮 Algorithmes d'optimisation
│   └── optimizer.py       # 🎲 Classe SatisfactionOptimizer
├── results/          # 📊 Dossier des résultats générés
├── gui.py            # 🖥️ Interface graphique
├── main.py           # ⚡ Version ligne de commande
├── satisfier.py      # 🔌 API Python simple
└── requirements.txt  # 📦 Dépendances Python
```

### 🔍 Description des composants

- **gui.py** : 🖥️ Interface graphique intuitive avec sélection de fichiers
- **main.py** : ⚡ Traitement direct des fichiers formatés
- **satisfier.py** : 🔌 Interface en ligne de commande avec options
- **models/data_models.py** : 🏗️ Classes pour la gestion des données
- **solver/optimizer.py** : 🎲 Algorithme d'optimisation
- **format/*.py** : 🔧 Outils de prétraitement des données

### 📁 Fichiers d'exemple fournis

Le dossier `data/` contient plusieurs fichiers d'exemple :
- 📋 `activities.csv` : Liste des activités disponibles avec leurs capacités
- 📝 `choices.csv` : Fichier brut des choix des élèves
- 📑 `choices.xls` : Version Excel du fichier choices.csv
- ✨ `choices_formatted.csv` : Version formatée de choices.csv

### 🔄 Processus de formatage des choix

1. Le fichier brut (`choices.csv` ou `choices.xls`) contient toutes les données 📝 :
   - En-têtes de classes
   - Lignes de totaux
   - Lignes vides
   - etc.

2. Le script `format_choices.py` nettoie ces données ✨ pour créer `choices_formatted.csv` qui contient uniquement :
   - Les noms des élèves
   - Leurs choix d'activités
   - Format exact requis pour l'optimisation

## 🖥️ Modes d'utilisation 

### 🎮 Interface graphique (GUI)

Le moyen le plus simple d'utiliser Satisfier :

```bash
python gui.py
```

Fonctionnalités :
- 📂 Sélection intuitive des fichiers
- 🎯 Configuration du nombre de choix
- 📊 Visualisation immédiate des résultats
- 💾 Sauvegarde automatique des résultats

Formats de fichiers acceptés :
- 📋 Activités : `.csv` ou `.xlsx`
- 📝 Choix : fichier brut `.csv` ou `.xlsx` (sera formaté automatiquement)

### ⌨️ Mode ligne de commande

Trois façons d'utiliser Satisfier en ligne de commande :

1. **Via satisfier.py (recommandé pour les fichiers bruts)** 🚀 :
```bash
python satisfier.py -i data/choices.xls -a data/activities.csv -o results/
```
Formats acceptés :
- 📋 Activités : `.csv` ou `.xlsx`
- 📝 Choix : fichier brut `.csv` ou `.xlsx`

2. **Via main.py (pour les fichiers déjà formatés)** ⚡ :
```bash
python main.py data/activities.csv data/choices_formatted.csv
```
Formats requis :
- 📋 Activités : `.csv`
- ✨ Choix : fichier formaté `.csv`

3. **Formatage des choix** 🔄 :
```bash
python ./format/format_choices.py ./data/choices.csv ./data/choices_formatted.csv
```
Formats :
- 📝 Entrée : fichier brut `.csv` ou `.xlsx`
- ✨ Sortie : fichier formaté `.csv`

### 🔧 Mode script Python

Pour l'intégration dans d'autres projets :

```python
from satisfier import process_assignment

process_assignment(
    activities_file="data/activities.csv",  # 📋 .csv ou .xlsx
    choices_file="data/choices.xlsx",       # 📝 fichier brut
    output_file="results/output.xlsx",      # 📊 résultats
    k=3                                     # 🎯 nombre de choix
)
```

## 📋 Format des fichiers d'entrée 

### 📊 Fichier des activités (activities.csv)

```csv
id,name,capacity
1,Poker,20
2,Football,15
3,Théâtre,12
```

### 📝 Fichier des choix (choices.xlsx)

```
Name,Choice 1,Choice 2,Choice 3
Jean Dupont,1,3,2
Marie Martin,2,1,3
```

## 🛠️ Outils de formatage 

### 🔄 excel_to_csv.py
```bash
python format/excel_to_csv.py data/fichier.xlsx
```

### ✨ format_choices.py
```bash
python format/format_choices.py data/choices.csv data/choices_formatted.csv
```

## 📊 Fichiers de sortie

Les résultats sont générés avec un timestamp précis ⏰ :
- Format : `resultats_assignation_DD-MM-YYYY_HHhMMmSS.xlsx`
- Exemple : `resultats_assignation_07-12-2023_15h30m45.xlsx`

Contenu du fichier de résultats :
- 📋 Assignations finales
- 📊 Statistiques de satisfaction
- ❌ Liste des élèves sans choix
- 📈 Taux de remplissage des activités

## 🔨 Compilation en exécutable 

1. Installation de PyInstaller 📦 :
```bash
pip install pyinstaller
```

2. Création de l'exécutable 🚀 :
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico gui.py
```

L'exécutable sera disponible dans `dist/gui.exe` ✨

## 💡 Exemples d'utilisation

### 🔄 Workflow complet
1. Préparation des données :
```bash
python ./format/format_choices.py ./data/choices.xls ./data/choices_formatted.csv
```

2. Optimisation :
```bash
python main.py data/activities.csv data/choices_formatted.csv
```

3. Résultats dans `results/resultats_assignation_[timestamp].xlsx` 📊

### ⚡ Utilisation rapide
```bash
python satisfier.py -i data/choices.xls -a data/activities.csv
```

## 📄 Licence 

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails. ⚖️

---

🚀 Développé avec ❤️ par KπX ✨
