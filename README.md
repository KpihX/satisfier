# Satisfier - Optimiseur de Choix

Ce programme permet d'optimiser la répartition des choix pour un groupe de personnes en maximisant la satisfaction globale.

## Description du problème

- n jeunes doivent faire k choix parmi m options possibles
- Chaque option i a une capacité maximale de mi places
- Les jeunes classent leurs choix de 1 à k par ordre de préférence
- Le programme optimise la répartition pour maximiser la satisfaction globale (priorité aux premiers choix)

## Structure du projet

- `main.py` : Point d'entrée du programme
- `models/` : Classes et structures de données
- `solver/` : Algorithmes d'optimisation
- `utils/` : Fonctions utilitaires
- `tests/` : Tests unitaires

## Installation

1. Créer un environnement virtuel :
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/MacOS
python3 -m venv env
source env/bin/activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Assurez-vous que l'environnement virtuel est activé, puis exécutez :
```bash
python main.py
```
