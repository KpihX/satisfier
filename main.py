import pandas as pd
from models.data_models import Student, Choice, AssignmentProblem
from solver.optimizer import SatisfactionOptimizer
import os
from datetime import datetime
import sys
import argparse

def validate_file_path(file_path: str, check_excel: bool = False) -> str:
    """Valide le chemin d'un fichier et son format si nécessaire"""
    if not os.path.exists(file_path):
        raise ValueError(f"Le fichier n'existe pas : {file_path}")
    
    if check_excel:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.xlsx', '.xls']:
            raise ValueError(f"Le fichier doit être au format Excel (.xlsx ou .xls) : {file_path}")
    
    return file_path

def validate_output_path(file_path: str) -> str:
    """Valide et crée si nécessaire le chemin de sortie"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            raise ValueError(f"Impossible de créer le dossier de sortie : {str(e)}")
    
    # Vérifier l'extension du fichier
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.xlsx', '.xls']:
        raise ValueError("Le fichier de sortie doit être au format Excel (.xlsx ou .xls)")
    
    return file_path

def read_file(file_path: str) -> pd.DataFrame:
    """Lit un fichier CSV ou Excel et retourne un DataFrame"""
    file_ext = os.path.splitext(file_path)[1].lower()
    try:
        if file_ext == '.csv':
            return pd.read_csv(file_path, encoding='utf-8', index_col=None)
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, index_col=None)
        else:
            raise ValueError(f"Format de fichier non supporté : {file_ext}")
    except UnicodeDecodeError:
        # Si l'UTF-8 échoue, essayons avec latin-1
        if file_ext == '.csv':
            return pd.read_csv(file_path, encoding='latin-1', index_col=None)
        raise

def load_data(activities_file: str, choices_file: str, k: int) -> AssignmentProblem:
    """Charge les données depuis les fichiers CSV ou Excel"""
    # Lecture des fichiers
    print("\nDébut du chargement des données...")
    
    activities_df = read_file(activities_file)
    print(f"Fichier d'activités chargé. Shape: {activities_df.shape}")
    
    choices_df = read_file(choices_file)
    print(f"Fichier de choix chargé. Shape: {choices_df.shape}")
    print("Colonnes du fichier de choix:", choices_df.columns.tolist())
    
    # Validation du nombre de colonnes pour les activités
    if len(activities_df.columns) < 3:
        raise ValueError("Le fichier des activités doit contenir 3 colonnes dans cet ordre : identifiant, nom, capacité")
    
    # Validation du nombre de colonnes pour les choix
    expected_cols = k + 1  # nom + k choix
    if len(choices_df.columns) != expected_cols:
        raise ValueError(f"Le fichier des choix doit contenir exactement {expected_cols} colonnes : nom de l'élève suivi de {k} choix. Actuellement : {len(choices_df.columns)} colonnes")
    
    # Renommer les colonnes pour correspondre à notre format interne
    activities_df.columns = ['id', 'name', 'capacity'] + list(activities_df.columns[3:])
    choices_df.columns = ['name', 'choice1', 'choice2', 'choice3']
    
    # Créer le dictionnaire des choix disponibles
    choices = {}
    for _, row in activities_df.iterrows():
        choice = Choice(id=int(row['id']), name=row['name'], capacity=int(row['capacity']))
        choices[choice.id] = choice
    
    # Filtrer les élèves qui n'ont pas fait de choix (toutes les colonnes de choix sont vides)
    has_choices = choices_df[['choice1', 'choice2', 'choice3']].notna().any(axis=1)
    students_with_choices = choices_df[has_choices].copy()
    students_no_choice = choices_df[~has_choices]['name'].tolist()
    print(f"Nombre d'élèves avec des choix: {len(students_with_choices)}")
    
    # Créer les objets Student
    students = []
    for idx, row in students_with_choices.iterrows():
        student_choices = []
        for i in range(1, k + 1):
            choice_val = row[f'choice{i}']
            if pd.notna(choice_val):
                student_choices.append(int(choice_val))
        if student_choices:  # N'ajouter l'étudiant que s'il a au moins un choix
            student = Student(id=idx, name=row['name'], choices=student_choices)
            students.append(student)
    
    return AssignmentProblem(students=students, choices=choices, k=k, students_no_choice=students_no_choice)

def print_example_formats():
    """Affiche les formats attendus des fichiers d'entrée"""
    print("\nFormat attendu pour le fichier des activités:")
    print("+----+------------------+----------+")
    print("| Id | Nom             | Capacité |")
    print("+----+------------------+----------+")
    print("| 1  | Football        | 15       |")
    print("| 2  | Basket          | 12       |")
    print("| 3  | Tennis          | 8        |")
    print("+----+------------------+----------+")
    print("\nNote: Les noms des colonnes sont flexibles, mais l'ordre doit être:")
    print("1. ID (nombre entier)")
    print("2. Nom de l'activité (texte)")
    print("3. Capacité (nombre entier)")
    
    print("\nFormat attendu pour le fichier des choix (exemple avec k=3):")
    print("+-------------+------------+------------+------------+")
    print("| Nom         | Choix 1    | Choix 2    | Choix 3    |")
    print("+-------------+------------+------------+------------+")
    print("| Jean Dupont | 1          | 3          | 2          |")
    print("| Marie Smith | 2          | 1          | 3          |")
    print("+-------------+------------+------------+------------+")
    print("\nNote: Les noms des colonnes sont flexibles, mais l'ordre doit être:")
    print("1. Nom de l'étudiant (texte)")
    print("2. Premier choix (ID de l'activité)")
    print("3. Deuxième choix (ID de l'activité)")
    print("etc. jusqu'à k choix")

def generate_results_file(solution: AssignmentProblem, summary: dict, output_file: str) -> str:
    """Génère un fichier Excel avec les résultats de l'assignation et les statistiques"""
    # Créer le dossier de destination s'il n'existe pas
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Préparation des données des étudiants pour le DataFrame
    results_data = []
    random_assignments = []
    for student in solution.students:
        assigned_activity = solution.choices[student.assigned_choice] if student.assigned_choice else None
        choice_position = (student.choices.index(student.assigned_choice) + 1) if student.assigned_choice in student.choices else None
        
        # Déterminer si c'est une attribution aléatoire
        is_random = student.assigned_choice is not None and student.assigned_choice not in student.choices
        
        results_data.append({
            'Nom': student.name,
            'Activité assignée': assigned_activity.name if assigned_activity else "Non assigné",
            'Choix obtenu': f"Choix {choice_position}" if choice_position else "Attribution Aléatoire" if is_random else "Non assigné"
        })
        
        if is_random:
            random_assignments.append({
                'Nom': student.name,
                'Activité assignée': assigned_activity.name
            })
    
    # Création du DataFrame des résultats
    results_df = pd.DataFrame(results_data)
    random_df = pd.DataFrame(random_assignments) if random_assignments else pd.DataFrame(columns=['Nom', 'Activité assignée'])
    
    # Création du DataFrame pour les étudiants sans choix
    no_choice_df = pd.DataFrame({'Nom': solution.students_no_choice}) if solution.students_no_choice else pd.DataFrame(columns=['Nom'])
    if not no_choice_df.empty:
        no_choice_df['Status'] = "Aucun choix fait"
    
    # Création du nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%Mm%S")
    output_file = os.path.join(output_dir, f'resultats_assignation_{timestamp}.xlsx')
    
    # Écriture dans le fichier Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Onglet des assignations
        results_df.to_excel(writer, sheet_name='Assignations', index=False, startcol=0)
        
        # Écrire les attributions aléatoires à côté
        if not random_df.empty:
            random_df.to_excel(writer, sheet_name='Assignations', index=False, startcol=5)
            worksheet = writer.sheets['Assignations']
            worksheet.cell(row=1, column=6, value="Attributions Aléatoires")
        
        # Écrire la liste des étudiants sans choix
        if not no_choice_df.empty:
            no_choice_df.to_excel(writer, sheet_name='Assignations', index=False, startcol=9)
            worksheet = writer.sheets['Assignations']
            worksheet.cell(row=1, column=10, value="Étudiants Sans Choix")
        
        # Préparation des statistiques de satisfaction
        stats_data = []
        total_students = len(solution.students)
        
        # Nombre d'étudiants par choix
        total_satisfied = 0
        for i in range(1, solution.k + 1):
            choice_key = f"choice_{i}"
            count = summary['choice_distribution'].get(choice_key, 0)
            percentage = (count / total_students) * 100
            total_satisfied += count
            stats_data.append({
                'Niveau de satisfaction': f"Choix {i}",
                'Nombre d\'étudiants': count,
                'Pourcentage': f"{percentage:.1f}%"
            })
        
        # Calcul du total des étudiants n'ayant pas eu un de leurs choix
        total_unsatisfied = summary['forced_assignments'] + summary['unassigned']
        percentage_unsatisfied = (total_unsatisfied / total_students) * 100
        
        # Ajout des attributions forcées
        if summary['forced_assignments'] > 0:
            percentage_forced = (summary['forced_assignments'] / total_students) * 100
            stats_data.append({
                'Niveau de satisfaction': "Attributions aléatoires (aucun choix satisfait)",
                'Nombre d\'étudiants': summary['forced_assignments'],
                'Pourcentage': f"{percentage_forced:.1f}%"
            })

        # Ajout des non-assignés
        if summary['unassigned'] > 0:
            percentage_unassigned = (summary['unassigned'] / total_students) * 100
            stats_data.append({
                'Niveau de satisfaction': "Non assignés (aucun choix satisfait)",
                'Nombre d\'étudiants': summary['unassigned'],
                'Pourcentage': f"{percentage_unassigned:.1f}%"
            })
        
        # Ajout du résumé global de satisfaction
        stats_data.append({
            'Niveau de satisfaction': "TOTAL - Choix satisfaits",
            'Nombre d\'étudiants': total_satisfied,
            'Pourcentage': f"{(total_satisfied / total_students) * 100:.1f}%"
        })
        stats_data.append({
            'Niveau de satisfaction': "TOTAL - Aucun choix satisfait",
            'Nombre d\'étudiants': total_unsatisfied,
            'Pourcentage': f"{percentage_unsatisfied:.1f}%"
        })
        
        # Création du DataFrame des statistiques
        stats_df = pd.DataFrame(stats_data)

        # Préparation de la répartition par activité
        activities_students = {}
        max_students = 0
        # Collecter les étudiants par activité
        for activity in solution.choices.values():
            students_in_activity = [
                student.name for student in solution.students
                if student.assigned_choice == activity.id
            ]
            activities_students[activity.name] = students_in_activity
            max_students = max(max_students, len(students_in_activity))
        
        # Créer les données pour le DataFrame
        activities_data = []
        # D'abord les lignes avec les étudiants
        for i in range(max_students):
            row_data = {}
            for activity_name in activities_students:
                students = activities_students[activity_name]
                row_data[activity_name] = students[i] if i < len(students) else ""
            activities_data.append(row_data)
        
        # Créer le DataFrame principal avec les étudiants
        activities_df = pd.DataFrame(activities_data)
        
        # Créer un DataFrame séparé pour les statistiques d'activités
        stats_rows = []
        # Ligne pour le nombre d'élèves
        num_students = {activity: len(students) for activity, students in activities_students.items()}
        stats_rows.append(num_students)
        
        # Ligne pour la capacité
        capacities = {activity.name: activity.capacity for activity in solution.choices.values()}
        stats_rows.append(capacities)
        
        # Créer le DataFrame des statistiques avec les labels
        activities_stats_df = pd.DataFrame(stats_rows, index=['Nombre d\'élèves', 'Capacité maximale'])
        
        # Onglet des statistiques de satisfaction
        stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
        
        # Onglet de la répartition par activité
        activities_df.to_excel(writer, sheet_name='Répartition par activité', index=False)
        
        # Écrire les statistiques d'activités en dessous
        start_row = len(activities_df.index) + 2
        activities_stats_df.to_excel(writer, sheet_name='Répartition par activité', startrow=start_row)
        
        # Ajustement automatique de la largeur des colonnes
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    return output_file

def process_assignment(activities_file: str, choices_file: str, output_file: str = None, k: int = 3) -> str:
    """Traite l'assignation des activités et génère le fichier de résultats"""
    try:
        # Validation des fichiers d'entrée
        validate_file_path(activities_file)
        validate_file_path(choices_file)
        
        # Chargement et traitement des données
        problem = load_data(activities_file, choices_file, k)
        optimizer = SatisfactionOptimizer(problem)
        solution = optimizer.optimize()
        summary = optimizer.get_solution_summary()
        
        # Préparation du chemin de sortie
        if output_file is None:
            output_dir = os.path.join(os.getcwd(), 'results')
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
            output_file = os.path.join(output_dir, f'results_assignment_{timestamp}.xlsx')
        else:
            output_file = validate_output_path(output_file)
        
        # Génération du fichier de résultats
        generate_results_file(solution, summary, output_file)

        # Ouvrir le fichier avec Excel
        try:
            os.startfile(output_file)
            print(f"Le fichier a été généré et ouvert dans Excel : {output_file}")
        except Exception as e:
            print(f"Le fichier a été généré mais n'a pas pu être ouvert automatiquement. Vous pouvez le trouver ici : {output_file}")
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Erreur lors du traitement : {str(e)}")

def print_help():
    """Affiche l'aide détaillée du programme"""
    help_text = """
Satisfier - Optimisation des assignations d'activités

DESCRIPTION:
    Ce programme permet d'optimiser l'attribution d'activités aux étudiants
    en fonction de leurs préférences et des capacités disponibles.

USAGE:
    python main.py <fichier_activites> <fichier_choix> [options]

ARGUMENTS:
    fichier_activites    Chemin vers le fichier des activités (Excel ou CSV)
                        Format attendu: id,name,capacity
                        Exemple: 1,Théâtre,15

    fichier_choix       Chemin vers le fichier des choix (Excel ou CSV)
                        Format attendu: name,choice1,choice2,choice3,...
                        Exemple: "Jean Dupont",1,3,2

OPTIONS:
    -h, --help          Affiche ce message d'aide
    -o, --output        Chemin vers le fichier de sortie (Excel)
                        Par défaut: ./results/results_assignment_DATE.xlsx
    -k, --num_choices   Nombre de choix par étudiant (défaut: 3)

EXEMPLES:
    # Usage basique
    python main.py activites.xlsx choix.xlsx

    # Avec fichier de sortie personnalisé
    python main.py activites.xlsx choix.xlsx -o resultats.xlsx

    # Avec nombre de choix personnalisé
    python main.py activites.xlsx choix.xlsx -k 4

FORMATS DE FICHIERS:
    1. Fichier des activités (CSV ou Excel):
       +----+------------------+----------+
       | id | name             | capacity |
       +----+------------------+----------+
       | 1  | Football         | 15       |
       | 2  | Basket           | 12       |
       +----+------------------+----------+

    2. Fichier des choix (CSV ou Excel):
       +-------------+------------+------------+------------+
       | name        | choice1    | choice2    | choice3    |
       +-------------+------------+------------+------------+
       | Jean Dupont | 1          | 3          | 2          |
       +-------------+------------+------------+------------+
    """
    print(help_text)

def main():
    # Vérifier si le script est exécuté directement (non importé)
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            description='Optimisation des assignations d\'activités',
            add_help=False  # Désactive l'aide automatique
        )
        parser.add_argument('activities', nargs='?', help='Chemin vers le fichier des activités (Excel ou CSV)')
        parser.add_argument('choices', nargs='?', help='Chemin vers le fichier des choix (Excel ou CSV)')
        parser.add_argument('-o', '--output', help='Chemin vers le fichier de sortie (Excel)')
        parser.add_argument('-k', '--num_choices', type=int, default=3, 
                          help='Nombre de choix par étudiant (défaut: 3)')
        parser.add_argument('-h', '--help', action='store_true', help='Affiche ce message d\'aide')
        
        try:
            args = parser.parse_args()
            
            # Afficher l'aide si demandé ou si les arguments obligatoires manquent
            if args.help or not (args.activities and args.choices):
                print_help()
                sys.exit(0)
            
            results_file = process_assignment(
                args.activities, 
                args.choices, 
                args.output, 
                args.num_choices
            )
            
            # Affichage des résultats dans le terminal
            print("\nRésultats de l'optimisation :")
            problem = load_data(args.activities, args.choices, args.num_choices)
            optimizer = SatisfactionOptimizer(problem)
            solution = optimizer.optimize()
            summary = optimizer.get_solution_summary()
            
            print(f"Score de satisfaction global : {summary['satisfaction_score']:.2%}")
            print("\nDistribution des choix :")
            for choice_level, count in sorted(summary['choice_distribution'].items()):
                print(f"{choice_level}: {count} étudiants")
            if summary['unassigned'] > 0:
                print(f"Non assignés: {summary['unassigned']} étudiants")
            
            print("\nAssignations détaillées :")
            for student in solution.students:
                assigned = solution.choices[student.assigned_choice].name if student.assigned_choice else "Non assigné"
                chosen_from_preferences = student.assigned_choice in student.choices
                choice_status = " (choix aléatoire)" if not chosen_from_preferences else ""
                print(f"{student.name} -> {assigned}{choice_status}")
            
            print(f"\nLes résultats ont été sauvegardés dans : {results_file}")
            
        except Exception as e:
            print(f"Erreur : {str(e)}", file=sys.stderr)
            print("\nPour plus d'informations sur l'utilisation du programme :", file=sys.stderr)
            print_help()
            sys.exit(1)
            
if __name__ == "__main__":
    main()
