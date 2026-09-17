# Composants tiers / Third-party components

Les dépendances conservent leurs licences ; elles sont installées depuis les fichiers requirements, pas copiées dans le dépôt. Conservez les notices des versions embarquées lors de la distribution d’un EXE.

Dependencies retain their licenses. They are installed through requirements files, not vendored in this repository. Retain notices for the versions bundled when distributing an EXE.

| Composant / Component | Usage | Référence / Reference |
| --- | --- | --- |
| Python, Tkinter, Tcl/Tk, SQLite | Exécution, interface et index / Runtime, interface and index | https://docs.python.org/3/license.html |
| Pillow | Lecture des images / Image decoding | https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| PyInstaller | Construction Windows / Windows build | https://pyinstaller.org/en/stable/license.html |
| pefile | Contrôle des icônes de l’EXE / EXE icon checking | https://github.com/erocarrera/pefile/blob/master/LICENSE |

Le constructeur et le module d’icône Windows sont adaptés de Morgue 3.1.12 et Photo 1.0.0 fournis par Simon Léturgie, sous AGPL v3 ou ultérieure. L’icône commune est réutilisée à l’identique ; marques et logos restent réservés.

The builder and Windows icon module are adapted from Morgue 3.1.12 and Photo 1.0.0 by Simon Léturgie, under AGPL v3 or later. The shared icon is reused unchanged; trademarks and logos remain reserved.
