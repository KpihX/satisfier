import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Création d'une image 128x128 avec fond transparent
    img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs
    primary_color = "#2E86C1"  # Bleu
    secondary_color = "#3498DB"  # Bleu clair
    
    # Dessiner un cercle extérieur
    draw.ellipse([4, 4, 124, 124], outline=primary_color, width=3)
    
    # Dessiner le "S" stylisé
    points = [
        (44, 40),   # Début du S
        (84, 40),   # Haut droite
        (84, 55),   # Milieu haut droite
        (44, 55),   # Milieu haut gauche
        (44, 73),   # Milieu bas gauche
        (84, 73),   # Milieu bas droite
        (84, 88),   # Bas droite
        (44, 88),   # Bas gauche
    ]
    
    # Dessiner le S avec un dégradé
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill=primary_color, width=8)
    
    # Sauvegarder en PNG et ICO
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    img.save('assets/logo.png', 'PNG')
    img.save('assets/logo.ico', format='ICO', sizes=[(128, 128)])

if __name__ == "__main__":
    create_logo()
