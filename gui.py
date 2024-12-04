import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from main import load_data, generate_results_file
from solver.optimizer import SatisfactionOptimizer

class SatisfierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Satisfier - Optimisation des choix")
        self.root.geometry("800x600")
        self.root.configure(padx=20, pady=20)

        # Variables
        self.activities_path = tk.StringVar()
        self.choices_path = tk.StringVar()
        self.num_choices = tk.StringVar(value="3")
        
        # Style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10), wraplength=700)

        # Titre
        ttk.Label(root, text="Optimisation des choix d'activités", style='Title.TLabel').pack(pady=(0, 20))

        # Frame pour le nombre de choix
        choices_frame = ttk.LabelFrame(root, text="Paramètres", padding=10)
        choices_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(choices_frame, text="Nombre de choix par élève :").pack(side='left', padx=5)
        ttk.Entry(choices_frame, textvariable=self.num_choices, width=5).pack(side='left', padx=5)

        # Frame pour les fichiers
        files_frame = ttk.LabelFrame(root, text="Sélection des fichiers", padding=10)
        files_frame.pack(fill='x', pady=(0, 20))

        # Section Activités
        ttk.Label(files_frame, text="Fichier des activités :", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Label(files_frame, text="Format attendu (CSV) :", style='Info.TLabel').pack(anchor='w')
        ttk.Label(files_frame, text="id,name,capacity\n1,Théâtre,3\n2,Musique,2\n...", font=('Courier', 9)).pack(anchor='w', pady=(0, 10))
        
        file_select_frame = ttk.Frame(files_frame)
        file_select_frame.pack(fill='x', pady=(0, 20))
        ttk.Entry(file_select_frame, textvariable=self.activities_path).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(file_select_frame, text="Parcourir", command=self.browse_activities).pack(side='right')

        # Section Choix des élèves
        ttk.Label(files_frame, text="Fichier des choix des élèves :", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Label(files_frame, text="Format attendu (CSV) :", style='Info.TLabel').pack(anchor='w')
        ttk.Label(files_frame, text="name,choice1,choice2,choice3\nEmma Martin,1,3,5\nLucas Dubois,2,1,4\n...", 
                 font=('Courier', 9)).pack(anchor='w', pady=(0, 10))
        
        file_select_frame2 = ttk.Frame(files_frame)
        file_select_frame2.pack(fill='x')
        ttk.Entry(file_select_frame2, textvariable=self.choices_path).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(file_select_frame2, text="Parcourir", command=self.browse_choices).pack(side='right')

        # Bouton de traitement
        ttk.Button(root, text="Lancer l'optimisation", command=self.process_files).pack(pady=20)

    def browse_activities(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier des activités",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.activities_path.set(filename)

    def browse_choices(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier des choix",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.choices_path.set(filename)

    def validate_files(self):
        try:
            # Validation du nombre de choix
            try:
                k = int(self.num_choices.get())
                if k <= 0:
                    raise ValueError("Le nombre de choix doit être positif")
            except ValueError:
                messagebox.showerror("Erreur", "Le nombre de choix doit être un nombre entier positif")
                return False

            # Validation du fichier des activités
            if not self.activities_path.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner le fichier des activités")
                return False
            
            activities_df = pd.read_csv(self.activities_path.get())
            required_columns = {'id', 'name', 'capacity'}
            if not all(col in activities_df.columns for col in required_columns):
                messagebox.showerror("Erreur", 
                    "Le fichier des activités doit contenir les colonnes : id, name, capacity")
                return False

            # Validation du fichier des choix
            if not self.choices_path.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner le fichier des choix")
                return False
            
            choices_df = pd.read_csv(self.choices_path.get())
            required_columns = {'name'} | {f'choice{i}' for i in range(1, k + 1)}
            if not all(col in choices_df.columns for col in required_columns):
                messagebox.showerror("Erreur", 
                    f"Le fichier des choix doit contenir les colonnes : name, choice1, choice2, ..., choice{k}")
                return False

            return True
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la validation des fichiers : {str(e)}")
            return False

    def process_files(self):
        if not self.validate_files():
            return

        try:
            # Création du dossier resultats si nécessaire
            output_dir = os.path.join(os.getcwd(), 'resultats')
            os.makedirs(output_dir, exist_ok=True)

            # Chargement et traitement des données
            k = int(self.num_choices.get())
            problem = load_data(self.activities_path.get(), self.choices_path.get(), k)
            optimizer = SatisfactionOptimizer(problem)
            solution = optimizer.optimize()
            summary = optimizer.get_solution_summary()

            # Génération du fichier de résultats
            results_file = generate_results_file(solution, summary, output_dir)

            messagebox.showinfo("Succès", 
                f"L'optimisation est terminée !\nLes résultats ont été sauvegardés dans :\n{results_file}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

def main():
    root = tk.Tk()
    app = SatisfierGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
