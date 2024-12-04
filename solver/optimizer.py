from typing import List, Dict
from models.data_models import Student, Choice, AssignmentProblem

class SatisfactionOptimizer:
    def __init__(self, problem: AssignmentProblem):
        self.problem = problem
        self._reset_assignments()

    def _reset_assignments(self):
        """Réinitialise toutes les attributions"""
        for student in self.problem.students:
            student.assigned_choice = None
            student.forced_assignment = False  # Initialisation de l'attribut
        for choice in self.problem.choices.values():
            choice.assigned_students = []

    def optimize(self) -> AssignmentProblem:
        """
        Optimise les attributions pour maximiser la satisfaction
        Utilise une approche en deux phases:
        1. Attribution selon les choix des étudiants
        2. Attribution aléatoire pour les étudiants restants s'il reste des places
        """
        self._reset_assignments()
        
        # Trie les étudiants par ordre aléatoire pour éviter les biais
        import random
        students = self.problem.students.copy()
        random.shuffle(students)

        # Phase 1: Attribution selon les choix
        for choice_level in range(self.problem.k):
            unassigned = [s for s in students if s.assigned_choice is None]
            for student in unassigned:
                if choice_level < len(student.choices):
                    current_choice = student.choices[choice_level]
                    choice_obj = self.problem.choices[current_choice]
                    
                    if len(choice_obj.assigned_students) < choice_obj.capacity:
                        student.assigned_choice = current_choice
                        choice_obj.assigned_students.append(student.id)
                        student.forced_assignment = False

        # Phase 2: Attribution aléatoire pour les étudiants restants
        unassigned = [s for s in students if s.assigned_choice is None]
        if unassigned:
            # Trouver toutes les activités avec des places restantes
            available_choices = [
                choice_id for choice_id, choice in self.problem.choices.items()
                if len(choice.assigned_students) < choice.capacity
            ]

            for student in unassigned:
                if available_choices:  # S'il reste des places quelque part
                    # Choisir une activité au hasard parmi celles disponibles
                    random_choice = random.choice(available_choices)
                    choice_obj = self.problem.choices[random_choice]
                    
                    student.assigned_choice = random_choice
                    choice_obj.assigned_students.append(student.id)
                    student.forced_assignment = True  # Marquer que c'était une attribution forcée
                    
                    # Mettre à jour la liste des choix disponibles
                    if len(choice_obj.assigned_students) >= choice_obj.capacity:
                        available_choices.remove(random_choice)

        return self.problem

    def get_solution_summary(self) -> Dict:
        """Retourne un résumé de la solution"""
        summary = {
            "total_students": len(self.problem.students),
            "satisfaction_score": self.problem.get_satisfaction_score(),
            "choice_distribution": {},
            "unassigned": 0,
            "forced_assignments": 0
        }

        for student in self.problem.students:
            if student.assigned_choice is None:
                summary["unassigned"] += 1
            elif student.forced_assignment:  # Plus besoin de hasattr car l'attribut est toujours initialisé
                summary["forced_assignments"] += 1
            else:
                choice_position = student.choices.index(student.assigned_choice) + 1
                summary["choice_distribution"][f"choice_{choice_position}"] = \
                    summary["choice_distribution"].get(f"choice_{choice_position}", 0) + 1

        return summary
