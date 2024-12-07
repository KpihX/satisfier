#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import argparse

def print_help():
    """Display detailed help message"""
    help_text = """
Format Student Choices

DESCRIPTION:
    Formate un fichier CSV de choix d'élèves en un format standardisé :
    - Une ligne par élève
    - Colonnes : Name, Choice 1, Choice 2, Choice 3
    - Trié par ordre alphabétique des noms
    - Inclut les élèves sans choix
    - Ignore les lignes de classes (SAPVER, CAPA, etc.)

USAGE:
    python format_choices.py input_file [output_file]

ARGUMENTS:
    input_file      Fichier CSV d'entrée avec les choix des élèves
    output_file     (Optionnel) Fichier de sortie. Par défaut: input_file_formatted.csv

FORMAT D'ENTRÉE:
    Le fichier CSV doit contenir les colonnes avec les noms d'élèves et leurs choix
    Les noms de classes (SAPVER, CAPA, etc.) sont ignorés

FORMAT DE SORTIE:
    Name,Choice 1,Choice 2,Choice 3
    DUPONT Jean,1,2,3
    MARTIN Marie,,, (élève sans choix)
    """
    print(help_text)

def is_student_name(name):
    """Check if a name is a student name (not a class name)"""
    if pd.isna(name) or not isinstance(name, str) or name.strip() == '':
        return False
        
    # Liste des mots-clés à exclure
    excluded = [
        'TOTAL',         # Lignes de total
        'SAPVER',        # Classes SAPVER
        'CAPA',          # Classes CAPA
        'BP',            # Classes BP
        'SAPAT',         # Classes SAPAT
        '3EME',          # Classes 3ème
        '4EME',          # Classes 4ème
        'SECONDE',       # Classes Seconde
        'PREMIERE',      # Classes Première
        'TERMINALE',     # Classes Terminale
        'AM.PA',         # Classes Am.Pa
        'AM PA',         # Classes Am.Pa (autre écriture)
        'PR.HO',         # Classes Pr.Ho
        'PR HO',         # Classes Pr.Ho (autre écriture)
        'JP.PA',         # Classes Jp.Pa
        'JP PA'          # Classes Jp.Pa (autre écriture)
    ]
    
    # Convertir en majuscules pour la comparaison
    name_upper = name.strip().upper()
    
    # Vérifier si le nom contient un mot-clé à exclure
    for keyword in excluded:
        if keyword in name_upper:
            return False
            
    return True

def format_student_choices(input_file, output_file=None):
    """Format student choices file"""
    try:
        # Read CSV file
        df = pd.read_csv(input_file)
        
        # Create empty lists for students and their choices
        students = []
        choices = []
        
        # Process each row
        for _, row in df.iterrows():
            for col in df.columns:
                value = row[col]
                if is_student_name(value):
                    # Get the student's choices (next 3 columns if they exist)
                    col_idx = df.columns.get_loc(col)
                    student_choices = []
                    for i in range(1, 4):
                        if col_idx + i < len(df.columns):
                            choice = row[df.columns[col_idx + i]]
                            if pd.notna(choice):
                                student_choices.append(int(choice))
                            else:
                                student_choices.append(None)
                        else:
                            student_choices.append(None)
                            
                    students.append(value.strip())
                    choices.append(student_choices)
        
        # Create new dataframe with formatted data
        formatted_df = pd.DataFrame({
            'Name': students,
            'Choice 1': [c[0] if c else None for c in choices],
            'Choice 2': [c[1] if c else None for c in choices],
            'Choice 3': [c[2] if c else None for c in choices]
        })
        
        # Sort by student name
        formatted_df = formatted_df.sort_values('Name')
        
        # Set default output file if none provided
        if output_file is None:
            base = input_file.rsplit('.', 1)[0]
            output_file = f"{base}_formatted.csv"
            
        # Save to CSV
        formatted_df.to_csv(output_file, index=False)
        return output_file
        
    except Exception as e:
        raise Exception(f"Error formatting choices: {str(e)}")

def main():
    # Use add_help=False to handle help manually
    parser = argparse.ArgumentParser(description='Format student choices file', add_help=False)
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('output_file', nargs='?', help='Output CSV file')
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return
        
    try:
        result = format_student_choices(args.input_file, args.output_file)
        print(f"Fichier formaté créé : {result}")
    except Exception as e:
        print(f"Erreur : {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    main()
