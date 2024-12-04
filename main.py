import pandas as pd
from models.data_models import Student, Choice, AssignmentProblem
from solver.optimizer import SatisfactionOptimizer
import os
from datetime import datetime

def read_file(file_path: str) -> pd.DataFrame:
    """Lit un fichier CSV ou Excel et retourne un DataFrame"""
    file_ext = os.path.splitext(file_path)[1].lower()
    try:
        if file_ext == '.csv':
            return pd.read_csv(file_path, encoding='utf-8')
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté : {file_ext}")
    except UnicodeDecodeError:
        # Si l'UTF-8 échoue, essayons avec latin-1
        if file_ext == '.csv':
            return pd.read_csv(file_path, encoding='latin-1')
        raise

def load_data(activities_file: str, choices_file: str, k: int) -> AssignmentProblem:
    """
    Charge les données depuis les fichiers CSV ou Excel.
    
    Format attendu pour le fichier des activités:
    +----+------------------+----------+
    | Id | Nom             | Capacité |
    +----+------------------+----------+
    | 1  | Football        | 15       |
    | 2  | Basket          | 12       |
    | 3  | Tennis          | 8        |
    +----+------------------+----------+
    
    Format attendu pour le fichier des choix (exemple avec k=3):
    +-------------+------------+------------+------------+
    | Nom         | Choix 1    | Choix 2    | Choix 3    |
    +-------------+------------+------------+------------+
    | Jean Dupont | 1          | 3          | 2          |
    | Marie Smith | 2          | 1          | 3          |
    +-------------+------------+------------+------------+
    
    Note: Les noms des colonnes sont flexibles, seul l'ordre est important:
    - Activités: [id, nom, capacité]
    - Choix: [nom étudiant, choix 1, choix 2, ..., choix k]
    """
    try:
        # Lecture des fichiers
        activities_df = read_file(activities_file)
        choices_df = read_file(choices_file)
        
        # Vérification du nombre de colonnes
        if len(activities_df.columns) != 3:
            raise ValueError(
                "Le fichier des activités doit avoir exactement 3 colonnes : "
                "ID, Nom, et Capacité (dans cet ordre)."
            )
        
        if len(choices_df.columns) != k + 1:
            raise ValueError(
                f"Le fichier des choix doit avoir {k + 1} colonnes : "
                f"Nom de l'étudiant suivi de {k} choix."
            )
            
        # Vérification que k ne dépasse pas le nombre d'activités
        if k > len(activities_df):
            raise ValueError(
                f"Le nombre de choix demandé ({k}) est supérieur au nombre "
                f"d'activités disponibles ({len(activities_df)})"
            )

        # Vérification des types de données dans le fichier des activités
        try:
            activities_df.iloc[:, 0] = activities_df.iloc[:, 0].astype(int)
            activities_df.iloc[:, 2] = activities_df.iloc[:, 2].astype(int)
        except ValueError as e:
            raise ValueError(
                "Erreur dans le fichier des activités : "
                "L'ID et la Capacité doivent être des nombres entiers."
            ) from e

        # Vérification des types de données dans le fichier des choix
        try:
            for i in range(1, k + 1):
                choices_df.iloc[:, i] = choices_df.iloc[:, i].astype(int)
        except ValueError as e:
            raise ValueError(
                "Erreur dans le fichier des choix : "
                "Les choix doivent être des nombres entiers correspondant aux IDs des activités."
            ) from e

        # Vérification que les IDs des choix existent dans les activités
        activity_ids = set(activities_df.iloc[:, 0])
        for i in range(1, k + 1):
            invalid_ids = set(choices_df.iloc[:, i]) - activity_ids
            if invalid_ids:
                raise ValueError(
                    f"Erreur dans les choix : les IDs suivants n'existent pas "
                    f"dans le fichier des activités : {invalid_ids}"
                )

        # Création des choix disponibles
        choices = {
            int(row.iloc[0]): Choice(
                int(row.iloc[0]),
                str(row.iloc[1]),
                int(row.iloc[2])
            )
            for _, row in activities_df.iterrows()
        }
        
        # Création des étudiants avec leurs choix
        students = []
        for idx, row in choices_df.iterrows():
            student_id = idx + 1
            try:
                choices_list = [int(row.iloc[i]) for i in range(1, k + 1)]
            except ValueError as e:
                raise ValueError(
                    f"Erreur de format pour l'étudiant {row.iloc[0]}: "
                    f"les choix doivent être des nombres entiers"
                ) from e
            student = Student(student_id, str(row.iloc[0]), choices_list)
            students.append(student)
        
        return AssignmentProblem(students, choices, k)

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Une erreur inattendue est survenue : {str(e)}")

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

def generate_results_file(solution: AssignmentProblem, summary: dict, output_dir: str) -> str:
    """Génère un fichier Excel avec les résultats de l'assignation et les statistiques"""
    # Préparation des données des étudiants pour le DataFrame
    results_data = []
    for student in solution.students:
        assigned_activity = solution.choices[student.assigned_choice] if student.assigned_choice else None
        
        # Déterminer le statut de l'attribution
        if assigned_activity is None:
            assignment_status = "Non assigné"
        elif student.forced_assignment:
            assignment_status = "Attribution aléatoire"
        else:
            choice_position = student.choices.index(student.assigned_choice) + 1
            assignment_status = f"Choix {choice_position}"

        results_data.append({
            'Nom': student.name,
            'Activité assignée': assigned_activity.name if assigned_activity else "Non assigné",
            'Statut': assignment_status
        })
    
    # Création du DataFrame des résultats
    results_df = pd.DataFrame(results_data)
    
    # Création du nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%Mmin%Ssec")
    output_file = os.path.join(output_dir, f'resultats_assignation_{timestamp}.xlsx')
    
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
    
    # Écriture dans le fichier Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Onglet des assignations individuelles
        results_df.to_excel(writer, sheet_name='Assignations', index=False)
        
        # Onglet de la répartition par activité
        activities_df.to_excel(writer, sheet_name='Répartition par activité', index=False)
        
        # Écrire les statistiques d'activités en dessous
        start_row = len(activities_df.index) + 2
        activities_stats_df.to_excel(writer, sheet_name='Répartition par activité', startrow=start_row)
        
        # Onglet des statistiques de satisfaction
        stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
        
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

def main():
    # Chemins des fichiers
    current_dir = os.path.dirname(os.path.abspath(__file__))
    activities_file = os.path.join(current_dir, 'data', 'activities.xlsx')
    choices_file = os.path.join(current_dir, 'data', 'student_choices.xlsx')
    output_dir = os.path.join(current_dir, 'resultats')
    
    # Création du dossier de résultats s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre de choix par étudiant
    k = 3
    
    # Chargement des données
    problem = load_data(activities_file, choices_file, k)
    
    # Création et exécution de l'optimiseur
    optimizer = SatisfactionOptimizer(problem)
    solution = optimizer.optimize()
    
    # Obtention du résumé
    summary = optimizer.get_solution_summary()
    
    # Génération du fichier de résultats
    results_file = generate_results_file(solution, summary, output_dir)
    
    # Affichage des résultats dans le terminal
    print("\nRésultats de l'optimisation :")
    print(f"Score de satisfaction global : {summary['satisfaction_score']:.2%}")
    print("\nDistribution des choix :")
    for choice_level, count in sorted(summary['choice_distribution'].items()):
        print(f"{choice_level}: {count} étudiants")
    if summary['unassigned'] > 0:
        print(f"Non assignés: {summary['unassigned']} étudiants")
    
    print("\nAssignations détaillées :")
    for student in solution.students:
        assigned = solution.choices[student.assigned_choice].name if student.assigned_choice else "Non assigné"
        print(f"{student.name} -> {assigned}")
    
    print(f"\nLes résultats ont été sauvegardés dans : {results_file}")

if __name__ == "__main__":
    main()
