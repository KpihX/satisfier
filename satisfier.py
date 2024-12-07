#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from datetime import datetime
from format.excel_to_csv import excel_to_csv
from format.format_choices import format_student_choices
import subprocess

def validate_output_path(file_path: str) -> str:
    """Validate and create output directory if necessary"""
    if not file_path:
        return file_path
        
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            raise ValueError(f"Impossible de créer le dossier de sortie : {str(e)}")
    
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.xlsx', '.xls']:
        raise ValueError("Le fichier de sortie doit être au format Excel (.xlsx ou .xls)")
    
    return file_path

def print_help():
    """Display detailed help message"""
    help_text = """
Satisfier - Optimisation des Assignations d'Activités

DESCRIPTION:
    Optimise l'assignation des étudiants aux activités en fonction de leurs préférences
    tout en respectant les contraintes de capacité des activités.

USAGE:
    python satisfier.py [options]

OPTIONS:
    -h, --help            Affiche ce message d'aide
    -i, --input          Chemin vers le fichier des choix (Excel ou CSV)
    -o, --output         Chemin vers le fichier de sortie (Excel)
    -a, --activities     Chemin vers le fichier des activités (Excel ou CSV)
    -k, --num-choices    Nombre de choix par étudiant (défaut: 3)
    -g, --gui           Lance l'interface graphique

FORMAT DES FICHIERS:
    Fichier des choix:
        - Doit contenir les colonnes: nom, choix1, choix2, ..., choixK
        - Les noms des étudiants ne doivent pas être vides
        - Les choix doivent référencer des IDs d'activités valides
        
    Fichier des activités:
        - Doit contenir les colonnes: ID, Nom, Capacité
        - Les IDs doivent être uniques
        - Les capacités doivent être des entiers positifs

EXEMPLES:
    # Lancer l'interface graphique
    python satisfier.py -g

    # Utilisation basique en ligne de commande
    python satisfier.py -i choix.xlsx -a activites.csv -o resultats.xlsx

    # Spécifier le nombre de choix
    python satisfier.py -i choix.xlsx -a activites.csv -o resultats.xlsx -k 4

    # Utiliser des fichiers CSV
    python satisfier.py -i choix.csv -a activites.csv -o resultats.xlsx
"""
    print(help_text)

def process_choices(input_file: str = None, output_file: str = None, 
                   activities_file: str = None, num_choices: int = 3) -> str:
    """Process choices file and run optimization"""
    try:
        # Validate input files existence
        if not input_file or not activities_file:
            raise ValueError("Les fichiers d'entrée et d'activités sont requis")
            
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Le fichier des choix n'existe pas : {input_file}")
        if not os.path.exists(activities_file):
            raise FileNotFoundError(f"Le fichier des activités n'existe pas : {activities_file}")
            
        # Set default output file if none provided
        if not output_file:
            # Create results directory in current directory if it doesn't exist
            results_dir = os.path.join(os.getcwd(), 'results')
            os.makedirs(results_dir, exist_ok=True)
            # Generate filename with timestamp including seconds
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_file = os.path.join(results_dir, f'assignment_{timestamp}.xlsx')
        
        # Validate output path
        output_file = validate_output_path(output_file)
        
        # Step 1: Process choices file
        if input_file.lower().endswith(('.xlsx', '.xls')):
            # Convert Excel to CSV in same directory
            input_dir = os.path.dirname(input_file)
            input_name = os.path.splitext(os.path.basename(input_file))[0]
            choices_csv = os.path.join(input_dir, input_name + '.csv')
            try:
                excel_to_csv(input_file, choices_csv)
                print(f"Conversion Excel réussie ! Fichier des choix converti en CSV : {choices_csv}")
            except Exception as e:
                raise Exception(f"Erreur lors de la conversion Excel vers CSV : {str(e)}")
        else:
            # If input is already CSV, use it directly
            choices_csv = input_file
        
        # Format the CSV in same directory with _formatted suffix
        input_dir = os.path.dirname(choices_csv)
        input_name = os.path.splitext(os.path.basename(choices_csv))[0]
        formatted_choices = os.path.join(input_dir, input_name + '_formatted.csv')
        try:
            format_student_choices(choices_csv, formatted_choices)
            print(f"Formatage réussi ! Fichier des choix formaté : {formatted_choices}")
        except Exception as e:
            raise Exception(f"Erreur lors du formatage des choix : {str(e)}")
        
        # Step 2: Convert activities file to CSV if needed
        final_activities = activities_file
        if activities_file.lower().endswith(('.xlsx', '.xls')):
            activities_dir = os.path.dirname(activities_file)
            activities_name = os.path.splitext(os.path.basename(activities_file))[0]
            activities_csv = os.path.join(activities_dir, activities_name + '.csv')
            try:
                excel_to_csv(activities_file, activities_csv)
                print(f"Conversion Excel réussie ! Fichier des activités converti en CSV : {activities_csv}")
                final_activities = activities_csv
            except Exception as e:
                raise Exception(f"Erreur lors de la conversion du fichier des activités : {str(e)}")
        
        # Step 3: Run main.py with the formatted files
        try:
            import main
            result_file = main.process_assignment(
                activities_file=final_activities,
                choices_file=formatted_choices,
                output_file=output_file,
                k=num_choices
            )
            print(f"Optimisation terminée ! Résultats sauvegardés dans : {result_file}")
            return result_file
        except Exception as e:
            raise Exception(f"Erreur lors de l'optimisation : {str(e)}")
        
    except Exception as e:
        raise e

def main():
    parser = argparse.ArgumentParser(
        description='Optimisation des Assignations d\'Activités',
        add_help=False
    )
    parser.add_argument('-h', '--help', action='store_true',
                       help='Affiche ce message d\'aide')
    parser.add_argument('-i', '--input',
                       help='Chemin vers le fichier des choix (Excel ou CSV)')
    parser.add_argument('-o', '--output',
                       help='Chemin vers le fichier de sortie (Excel)')
    parser.add_argument('-a', '--activities',
                       help='Chemin vers le fichier des activités (Excel ou CSV)')
    parser.add_argument('-k', '--num-choices', type=int, default=3,
                       help='Nombre de choix par étudiant')
    parser.add_argument('-g', '--gui', action='store_true',
                       help='Lance l\'interface graphique')
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return
        
    if args.gui:
        # Import and launch GUI
        from gui import launch_gui
        try:
            launch_gui()
        except Exception as e:
            print(f"\nErreur : {str(e)}", file=sys.stderr)
            print("\nPour plus d'informations sur l'utilisation :", file=sys.stderr)
            print_help()
            sys.exit(1)
        return
        
    try:
        # En mode CLI, les fichiers d'entrée sont requis
        if not args.input or not args.activities:
            raise ValueError("Les fichiers d'entrée (-i) et d'activités (-a) sont requis")
            
        result_file = process_choices(
            input_file=args.input,
            output_file=args.output,
            activities_file=args.activities,
            num_choices=args.num_choices
        )
        print(f"\nSuccès ! Résultats sauvegardés dans : {result_file}")
        
    except Exception as e:
        print(f"\nErreur : {str(e)}", file=sys.stderr)
        print("\nPour plus d'informations sur l'utilisation :", file=sys.stderr)
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
