from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Choice:
    """Représente une option disponible"""
    id: int
    name: str
    capacity: int
    assigned_students: List[int] = None

    def __post_init__(self):
        if self.assigned_students is None:
            self.assigned_students = []

@dataclass
class Student:
    """Représente un étudiant et ses choix"""
    id: int
    name: str
    choices: List[int]  # Liste ordonnée des IDs des choix
    assigned_choice: int = None
    forced_assignment: bool = False  # Ajout de l'attribut forced_assignment avec une valeur par défaut

@dataclass
class AssignmentProblem:
    """Représente le problème complet d'attribution"""
    students: List[Student]
    choices: Dict[int, Choice]
    k: int  # Nombre de choix par étudiant

    def get_satisfaction_score(self) -> float:
        """Calcule le score de satisfaction global"""
        if not any(s.assigned_choice is not None for s in self.students):
            return 0.0
        
        total_score = 0
        total_students = len(self.students)
        
        for student in self.students:
            if student.assigned_choice is None:
                continue
                
            if student.forced_assignment:
                # Pour une attribution forcée, on donne un score minimal
                total_score += 0.1
            else:
                # Le score est inversement proportionnel à la position du choix
                try:
                    choice_position = student.choices.index(student.assigned_choice) + 1
                    total_score += (self.k - choice_position + 1) / self.k
                except ValueError:
                    # Si le choix n'est pas dans la liste (ne devrait pas arriver)
                    total_score += 0.1
                
        return total_score / total_students
