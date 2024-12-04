import PyInstaller.__main__

PyInstaller.__main__.run([
    'gui.py',
    '--onefile',
    '--windowed',
    '--name=Satisfier',
    '--add-data=README.md;.',
    '--icon=NONE',
])
