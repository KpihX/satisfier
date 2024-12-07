import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from main import load_data, generate_results_file
from solver.optimizer import SatisfactionOptimizer
from datetime import datetime

class SatisfierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Satisfier - Optimisation des choix")
        self.root.geometry("800x910")  # Augmentation de la hauteur
        self.root.configure(padx=20, pady=5)

        # Variables
        self.activities_path = tk.StringVar()
        self.choices_path = tk.StringVar()
        self.num_choices = tk.StringVar(value="3")
        
        # Style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10), wraplength=700)
        style.configure('Example.TLabel', font=('Courier', 9), wraplength=700)

        # Logo (uniquement si le fichier existe)
        try:
            self.logo_image = tk.PhotoImage(file='assets/logo.png')
            logo_label = ttk.Label(root, image=self.logo_image)
            logo_label.pack(pady=(0, 10))
        except:
            pass  # Si le logo ne peut pas être chargé, on continue sans

        # Titre
        ttk.Label(root, text="Optimisation des choix d'activités", style='Title.TLabel').pack(pady=(0, 20))

        # Frame pour le nombre de choix
        choices_frame = ttk.LabelFrame(root, text="Paramètres", padding=10)
        choices_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(choices_frame, text="Nombre de choix par élève (n) :").pack(side='left', padx=5)
        ttk.Entry(choices_frame, textvariable=self.num_choices, width=5).pack(side='left', padx=5)
        ttk.Label(choices_frame, text="Note : n ne doit pas dépasser le nombre d'activités disponibles.", style='Info.TLabel').pack(anchor='w', pady=(0, 5))

        # Frame pour les fichiers
        files_frame = ttk.LabelFrame(root, text="Sélection des fichiers", padding=10)
        files_frame.pack(fill='x', pady=(0, 20))

        # Section Activités
        ttk.Label(files_frame, text="Fichier des activités :", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Label(files_frame, text="Format attendu (CSV ou Excel) :", style='Info.TLabel').pack(anchor='w')
        activities_example = (
            "+------+------------------+------------+\n"
            "| Id   | Nom              | Capacité   |\n"
            "+------+------------------+------------+\n"
            "| 1    | Activité 1       | val 1      |\n"
            "| ...  |    ...           |  ...       |\n"
            "| m    | Activité m       | val m      |\n"
            "+------+------------------+------------+"
        )
        ttk.Label(files_frame, text=activities_example, style='Example.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Label(files_frame, 
                 text="Note : Les noms des colonnes sont flexibles, mais l'ordre doit être : ID, Nom, Capacité", 
                 style='Info.TLabel').pack(anchor='w', pady=(0, 10))
        
        file_select_frame = ttk.Frame(files_frame)
        file_select_frame.pack(fill='x', pady=(0, 20))
        ttk.Entry(file_select_frame, textvariable=self.activities_path).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(file_select_frame, text="Parcourir", command=self.browse_activities).pack(side='right')

        # Section Choix des élèves
        ttk.Label(files_frame, text="Fichier des choix des élèves :", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Label(files_frame, text="Format attendu (CSV ou Excel) :", style='Info.TLabel').pack(anchor='w')
        choices_example = (
            "+--------------+------------+-------+------------+\n"
            "| Nom          | Choix 1    | ...   | Choix n    |\n"
            "+--------------+------------+-------+------------+\n"
            "| Nom1         | 1          | ...   | 2          |\n"
            "| ...          | ...        | ...   | ...        |\n"
            "| Nom2         | 3          | ...   | 1          |\n"
            "+--------------+------------+-------+------------+"
        )
        ttk.Label(files_frame, text=choices_example, style='Example.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Label(files_frame, 
                 text="Note : Les noms des colonnes sont flexibles, mais l'ordre doit être : Nom de l'élève, suivi des n choix (où n est le nombre de choix défini plus haut)", 
                 style='Info.TLabel').pack(anchor='w', pady=(0, 10))
        
        file_select_frame2 = ttk.Frame(files_frame)
        file_select_frame2.pack(fill='x')
        ttk.Entry(file_select_frame2, textvariable=self.choices_path).pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(file_select_frame2, text="Parcourir", command=self.browse_choices).pack(side='right')

        # Bouton de traitement
        process_button = ttk.Button(root, text="Lancer l'optimisation", command=self.process_files)
        process_button.pack(pady=20)
        
        # Style du bouton
        style.configure('TButton', font=('Helvetica', 10))
        process_button.configure(style='TButton')

        # Ajout de la signature en bas à droite
        signature_frame = ttk.Frame(self.root)
        signature_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        signature_label = tk.Label(
            signature_frame, 
            text="By KπX",
            font=('TkDefaultFont', 10, 'bold italic'),
            foreground='#666666'
        )
        signature_label.pack(side=tk.RIGHT)

    def browse_activities(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier des activités",
            filetypes=[
                ("Fichiers supportés", "*.csv;*.xlsx;*.xls"),
                ("Fichiers CSV", "*.csv"),
                ("Fichiers Excel", "*.xlsx;*.xls"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if filename:
            self.activities_path.set(filename)

    def browse_choices(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier des choix",
            filetypes=[
                ("Fichiers supportés", "*.csv;*.xlsx;*.xls"),
                ("Fichiers CSV", "*.csv"),
                ("Fichiers Excel", "*.xlsx;*.xls"),
                ("Tous les fichiers", "*.*")
            ]
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

            # Validation des fichiers
            if not self.activities_path.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner le fichier des activités")
                return False
            
            if not self.choices_path.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner le fichier des choix")
                return False

            # Test de lecture des fichiers
            try:
                problem = load_data(self.activities_path.get(), self.choices_path.get(), k)
                return True
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                return False

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la validation des fichiers : {str(e)}")
            return False

    def process_files(self):
        if not self.validate_files():
            return

        try:
            # Chargement et traitement des données
            k = int(self.num_choices.get())
            problem = load_data(self.activities_path.get(), self.choices_path.get(), k)
            optimizer = SatisfactionOptimizer(problem)
            solution = optimizer.optimize()
            summary = optimizer.get_solution_summary()

            # Demander à l'utilisateur où sauvegarder le fichier
            timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
            default_filename = f'results_assignment_{timestamp}.xlsx'
            output_file = filedialog.asksaveasfilename(
                title="Enregistrer les résultats",
                initialfile=default_filename,
                defaultextension='.xlsx',
                filetypes=[("Fichiers Excel", "*.xlsx")]
            )
            
            if not output_file:  # Si l'utilisateur annule
                return
            
            # Créer le dossier de destination s'il n'existe pas
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Génération du fichier de résultats
            generate_results_file(solution, summary, output_file)
            
            # Ouvrir le fichier avec Excel
            try:
                os.startfile(output_file)
                messagebox.showinfo("Succès", "Le traitement est terminé et le fichier a été ouvert dans Excel.")
            except Exception as e:
                messagebox.showinfo("Succès", f"Le traitement est terminé.\nLe fichier a été enregistré dans : {output_file}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors du traitement : {str(e)}")

def launch_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = SatisfierGUI(root)
    # Définir l'icône de la fenêtre
    if os.path.exists('assets/logo.ico'):
        root.iconbitmap('assets/logo.ico')
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
