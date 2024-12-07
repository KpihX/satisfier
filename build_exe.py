import PyInstaller.__main__
import os
from logo import create_logo

# Créer le logo s'il n'existe pas
if not os.path.exists('assets'):
    os.makedirs('assets')
    create_logo()
elif not os.path.exists('assets/logo.png') or not os.path.exists('assets/logo.ico'):
    create_logo()

PyInstaller.__main__.run([
    'gui.py',
    '--onefile',
    '--windowed',
    '--name=Satisfier',
    '--add-data=assets/logo.png;assets',
    '--add-data=assets/logo.ico;assets',
    '--icon=assets/logo.ico',
])
