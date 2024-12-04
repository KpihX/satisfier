# 🎯 Satisfier - Optimiseur de Choix

## 📝 Description

Satisfier est un outil d'optimisation intelligent conçu pour résoudre le défi complexe de l'attribution d'activités aux étudiants en fonction de leurs préférences. 🎓

L'application utilise des algorithmes d'optimisation pour maximiser la satisfaction globale en tenant compte :

- 📊 Des capacités maximales de chaque activité
- 🎯 Des préférences ordonnées des étudiants
- ⚖️ De l'équité dans la distribution des choix

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Configuration de l'environnement

1. Clonez le repository :

```bash
git clone [URL_du_repo]
cd satisfier
```

2. Créez un environnement virtuel :

```bash
python -m venv venv
```

3. Activez l'environnement virtuel :

```bash
# Windows
venv\Scripts\activate
```

4. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## 📥 Fichiers d'entrée

L'application utilise deux fichiers Excel (.xlsx) ou (.csv) comme entrée qu'il faudra indiquer dans l'interface graphique :

1. `activites.xlsx` :

   - Colonnes requises : `id`, `name`, `capacity`
   - Décrit les activités disponibles et leurs capacités maximales
2. `student_choices.xlsx` :

   - Colonnes requises : `name`, `choice1`, `choice2`, `choice3`, ...
   - Liste les étudiants et leurs choix ordonnés

⚠️ Note : Vous pouvez utiliser les fichiers exemples fournis dans le dossier `data/` comme modèles. Il suffit de modifier leur contenu en gardant la même structure.

## 🎮 Utilisation

### Interface graphique

1. Lancez l'application :

```bash
python gui.py
```

2. Utilisez l'interface pour :
   - 📂 Sélectionner vos fichiers d'entrée
   - 🔢 Spécifier le nombre de choix par étudiant
   - 🚀 Lancer l'optimisation

### Création de l'exécutable

Pour créer un exécutable standalone :

```bash
# 1. Assurez-vous d'avoir toutes les dépendances
pip install -r requirements.txt

# 2. Générez l'exécutable
python build_exe.py
```

L'exécutable sera créé dans le dossier `dist/`.

## 📊 Résultats

L'application génère un fichier Excel dans le dossier `resultats/` contenant :

- 📋 Les assignations individuelles
- 📊 La répartition par activité
- 📈 Les statistiques de satisfaction

## 🛠️ Technologies utilisées

- Python 3.8+
- tkinter pour l'interface graphique
- pandas pour la manipulation des données
- openpyxl pour la gestion des fichiers Excel
- PyInstaller pour la création de l'exécutable

## ✨ Auteur

By KπX

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
