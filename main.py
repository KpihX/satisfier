from models.data_models import Student, Choice, AssignmentProblem
from solver.optimizer import SatisfactionOptimizer

def create_sample_problem():
    """Crée un problème exemple"""
    # Création des choix disponibles
    choices = {
        1: Choice(1, "Option A", capacity=2),
        2: Choice(2, "Option B", capacity=2),
        3: Choice(3, "Option C", capacity=2),
        4: Choice(4, "Option D", capacity=2),
    }

    # Création des étudiants avec leurs choix
    students = [
        Student(1, "Étudiant 1", [1, 2, 3]),
        Student(2, "Étudiant 2", [1, 3, 2]),
        Student(3, "Étudiant 3", [2, 1, 4]),
        Student(4, "Étudiant 4", [2, 3, 1]),
        Student(5, "Étudiant 5", [1, 4, 2]),
    ]

    return AssignmentProblem(students, choices, k=3)

def main():
    # Création du problème
    problem = create_sample_problem()
    
    # Création et exécution de l'optimiseur
    optimizer = SatisfactionOptimizer(problem)
    solution = optimizer.optimize()
    
    # Affichage des résultats
    summary = optimizer.get_solution_summary()
    print("\nRésultats de l'optimisation :")
    print(f"Score de satisfaction global : {summary['satisfaction_score']:.2%}")
    print("\nDistribution des choix :")
    for choice_level, count in summary['choice_distribution'].items():
        print(f"{choice_level}: {count} étudiants")
    print(f"Non assignés: {summary['unassigned']} étudiants")
    
    print("\nAssignations détaillées :")
    for student in solution.students:
        assigned = solution.choices[student.assigned_choice].name if student.assigned_choice else "Non assigné"
        print(f"{student.name} -> {assigned}")

if __name__ == "__main__":
    main()
