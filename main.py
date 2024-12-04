import pandas as pd
from models.data_models import Student, Choice, AssignmentProblem
from solver.optimizer import SatisfactionOptimizer
import os
from datetime import datetime

def load_data(activities_file: str, choices_file: str) -> AssignmentProblem:
    """Charge les données depuis les fichiers CSV"""
    # Lecture des fichiers CSV
    activities_df = pd.read_csv(activities_file)
    choices_df = pd.read_csv(choices_file)
    
    # Création des choix disponibles
    choices = {
        row['id']: Choice(row['id'], row['name'], row['capacity'])
        for _, row in activities_df.iterrows()
    }
    
    # Création des étudiants avec leurs choix (ID auto-générés)
    students = []
    for idx, row in choices_df.iterrows():
        student_id = idx + 1  # ID auto-généré
        choices_list = [row['choice1'], row['choice2'], row['choice3']]
        student = Student(student_id, row['name'], choices_list)
        students.append(student)
    
    # Nombre de choix par étudiant (déduit des données)
    k = len([col for col in choices_df.columns if col.startswith('choice')])
    
    return AssignmentProblem(students, choices, k)

def generate_results_file(solution: AssignmentProblem, summary: dict, output_dir: str) -> str:
    """Génère un fichier Excel avec les résultats de l'assignation et les statistiques"""
    # Préparation des données des étudiants pour le DataFrame
    results_data = []
    for student in solution.students:
        assigned_activity = solution.choices[student.assigned_choice] if student.assigned_choice else None
        choice_position = (student.choices.index(student.assigned_choice) + 1) if student.assigned_choice else None
        
        results_data.append({
            'Nom': student.name,
            'Activité assignée': assigned_activity.name if assigned_activity else "Non assigné",
            'Choix obtenu': f"Choix {choice_position}" if choice_position else "Non assigné"
        })
    
    # Création du DataFrame des résultats
    results_df = pd.DataFrame(results_data)
    
    # Création du nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%M")
    output_file = os.path.join(output_dir, f'resultats_assignation_{timestamp}.xlsx')
    
    # Préparation des statistiques de satisfaction
    stats_data = []
    total_students = len(solution.students)
    
    # Nombre d'étudiants par choix
    for i in range(1, solution.k + 1):
        choice_key = f"choice_{i}"
        count = summary['choice_distribution'].get(choice_key, 0)
        percentage = (count / total_students) * 100
        stats_data.append({
            'Niveau de satisfaction': f"Choix {i}",
            'Nombre d\'étudiants': count,
            'Pourcentage': f"{percentage:.1f}%"
        })
    
    # Ajout des non-assignés si présents
    if summary['unassigned'] > 0:
        percentage_unassigned = (summary['unassigned'] / total_students) * 100
        stats_data.append({
            'Niveau de satisfaction': "Non assignés",
            'Nombre d\'étudiants': summary['unassigned'],
            'Pourcentage': f"{percentage_unassigned:.1f}%"
        })
    
    # Score global
    stats_data.append({
        'Niveau de satisfaction': "Score global de satisfaction",
        'Nombre d\'étudiants': total_students,
        'Pourcentage': f"{summary['satisfaction_score']:.1%}"
    })
    
    stats_df_satisfaction = pd.DataFrame(stats_data)
    
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
    
    # Créer un DataFrame séparé pour les statistiques
    stats_rows = []
    # Ligne pour le nombre d'élèves
    num_students = {activity: len(students) for activity, students in activities_students.items()}
    stats_rows.append(num_students)
    
    # Ligne pour la capacité
    capacities = {activity.name: activity.capacity for activity in solution.choices.values()}
    stats_rows.append(capacities)
    
    # Créer le DataFrame des statistiques avec les labels
    stats_df = pd.DataFrame(stats_rows, index=['Nombre d\'élèves', 'Capacité maximale'])
    
    # Écriture dans le fichier Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Onglet des assignations individuelles
        results_df.to_excel(writer, sheet_name='Assignations', index=False)
        
        # Onglet de la répartition par activité
        # Écrire le DataFrame principal
        activities_df.to_excel(writer, sheet_name='Répartition par activité', index=False)
        
        # Calculer la position pour les statistiques (2 lignes après la fin des données)
        start_row = len(activities_df.index) + 2
        
        # Écrire les statistiques
        stats_df.to_excel(writer, sheet_name='Répartition par activité', startrow=start_row)
        
        # Onglet des statistiques
        stats_df_satisfaction.to_excel(writer, sheet_name='Statistiques', index=False)
        
        # Ajustement automatique de la largeur des colonnes pour chaque feuille
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
    activities_file = os.path.join(current_dir, 'data', 'activities.csv')
    choices_file = os.path.join(current_dir, 'data', 'student_choices.csv')
    output_dir = os.path.join(current_dir, 'resultats')
    
    # Création du dossier de résultats s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Chargement des données
    problem = load_data(activities_file, choices_file)
    
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
