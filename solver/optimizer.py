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
        for choice in self.problem.choices.values():
            choice.assigned_students = []

    def optimize(self) -> AssignmentProblem:
        """
        Optimise les attributions pour maximiser la satisfaction
        Utilise une approche gloutonne en commençant par les premiers choix
        """
        self._reset_assignments()
        
        # Trie les étudiants par ordre aléatoire pour éviter les biais
        import random
        students = self.problem.students.copy()
        random.shuffle(students)

        # Pour chaque niveau de choix (1er choix, 2ème choix, etc.)
        for choice_level in range(self.problem.k):
            # Pour chaque étudiant non encore assigné
            unassigned = [s for s in students if s.assigned_choice is None]
            
            for student in unassigned:
                if choice_level < len(student.choices):
                    current_choice = student.choices[choice_level]
                    choice_obj = self.problem.choices[current_choice]
                    
                    # Si il reste de la place dans ce choix
                    if len(choice_obj.assigned_students) < choice_obj.capacity:
                        student.assigned_choice = current_choice
                        choice_obj.assigned_students.append(student.id)

        return self.problem

    def get_solution_summary(self) -> Dict:
        """Retourne un résumé de la solution"""
        summary = {
            "total_students": len(self.problem.students),
            "satisfaction_score": self.problem.get_satisfaction_score(),
            "choice_distribution": {},
            "unassigned": 0
        }

        for student in self.problem.students:
            if student.assigned_choice is None:
                summary["unassigned"] += 1
            else:
                choice_position = student.choices.index(student.assigned_choice) + 1
                summary["choice_distribution"][f"choice_{choice_position}"] = \
                    summary["choice_distribution"].get(f"choice_{choice_position}", 0) + 1

        return summary
