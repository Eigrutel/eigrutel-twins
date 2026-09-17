# Eigrutel Lab - Atelier d'outils libres pour la bande dessinée
# Programme conçu et développé par Simon Léturgie dans le cadre d'Eigrutel BD Academy.
# Nom : Twins | Version : 1.0.0 | Date : 17-09-2026
# Code : GNU AGPL v3.0 ou version ultérieure.
# Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
# Marques et logos Eigrutel / Eigrutel Lab / Eigrutel BD Academy : réservés.

"""Build one Twins.exe on Windows with the current Python environment."""
from pathlib import Path
import subprocess
import sys
import struct


BUILD_NAME = 'Twins-1.0.0'


def read_ico_payloads(path):
    data = Path(path).read_bytes()
    reserved, kind, count = struct.unpack_from('<HHH', data)
    if (reserved, kind) != (0, 1) or not count:
        raise ValueError('Fichier ICO invalide')
    payloads = []
    for i in range(count):
        size, offset = struct.unpack_from('<II', data, 6+16*i+8)
        payload = data[offset:offset+size]
        if not size or len(payload) != size:
            raise ValueError('Image ICO incomplete')
        payloads.append(payload)
    return payloads


def matching_icon_group(expected, icons, groups):
    """Require every supplied image in an actual Windows icon resource group."""
    for group in groups:
        if len(group) < 6:
            continue
        reserved, kind, count = struct.unpack_from('<HHH', group)
        if reserved or kind != 1 or count != len(expected) or len(group) < 6+14*count:
            continue
        actual = []
        for index in range(count):
            size, resource_id = struct.unpack_from('<IH', group, 6+14*index+8)
            payload = icons.get(resource_id)
            if payload is None or len(payload) != size:
                break
            actual.append(payload)
        if actual == expected:
            return True
    return False


def verify_executable_icon(executable, icon):
    import pefile
    expected = read_ico_payloads(icon)
    pe = pefile.PE(str(executable))
    icons, groups = {}, []
    try:
        directory = getattr(pe, 'DIRECTORY_ENTRY_RESOURCE', None)
        for resource_type in directory.entries if directory else []:
            if resource_type.id not in (3,14):
                continue
            for resource in resource_type.directory.entries:
                for locale in resource.directory.entries:
                    entry = locale.data.struct
                    payload = pe.get_data(entry.OffsetToData, entry.Size)
                    if resource_type.id == 3:
                        icons[resource.id] = payload
                    else:
                        groups.append(payload)
    finally:
        pe.close()
    if not matching_icon_group(expected, icons, groups):
        raise RuntimeError('Controle echoue : l’icone Twins est absente ou incomplete dans l’executable.')


def main():
    if sys.platform != 'win32':
        raise SystemExit('Construisez Twins.exe sur Windows.')
    folder = Path(__file__).resolve().parent
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
               '--onefile', '--windowed', '--version-file', str(folder / 'windows-version.txt'), '--name', BUILD_NAME]
    icon = folder / 'Twins.ico'
    if not icon.is_file():
        raise SystemExit('Twins.ico manquant : extrayez toute l’archive avant de construire.')
    command += ['--icon', str(icon)]
    manual = folder / 'Manuel-Twins.html'
    if not manual.is_file():
        raise SystemExit('Manuel-Twins.html manquant : extrayez toute l’archive avant de construire.')
    command += ['--add-data', f'{manual}:.']
    for name in ('Twins.ico', 'Twins.png'):
        asset = folder / name
        if asset.is_file():
            command += ['--add-data', f'{asset}:.']
    command.append(str(folder / 'EigrutelTwins.py'))
    subprocess.run(command, cwd=folder, check=True)
    executable = folder / 'dist' / (BUILD_NAME+'.exe')
    verify_executable_icon(executable, icon)
    print('Icone integree et verifiee. Executable cree :', executable)


if __name__ == '__main__':
    main()
