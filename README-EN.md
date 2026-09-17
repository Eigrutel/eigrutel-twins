# Twins 1.0.0

**Find duplicate images, compare them and set copies aside.**

Eigrutel Lab / Open tools workshop for comics.
Designed and developed by Simon Léturgie as part of Eigrutel BD Academy.

[Français](README.md) · [User manual](docs/Twins-User-Manual-EN.md)

<img src="Twins.png" alt="Twins / Eigrutel Lab" width="96">

## The Morgue and Photo family

Twins uses the same paper background, dark blue `#1F3A44`, dark red `#7F2D30`, ochre `#C47A2C`, FR/EN controls, help panel and shared icon as Morgue and Photo. The icon is unchanged, renamed `Twins.ico` and `Twins.png`. The native Windows taskbar fix uses a Twins-specific identity.

Twins works independently and keeps its own settings. The old `ui_common.py` is not required.

## Features

- Scan folders, optionally including subfolders: JPEG, PNG, WebP, TIFF, BMP and GIF.
- SHA-256 exact duplicates and dHash visual similarities, with tolerance from 0 to 20.
- Side-by-side previews, groups, file lists, reference swapping and basic metadata.
- EXIF-oriented previews that follow window resizing.
- Double-click to open an image; access to its location.
- Move either image to a configurable duplicates folder.
- Process **exact groups only**, keeping the newest file, shortest filename or longest filename.
- Background scanning, searching and moves; Stop button and Escape cancellation.
- Revalidation, verified copies without overwriting and a local move journal.
- FR/EN interface, manuals and remembered settings.

Visual similarity does not prove equality. Visual matching is restricted to equal dimensions after EXIF orientation and may miss differences in color or details. Only the first frame of animated or multipage files is compared visually; exact matching hashes the whole file. Review the manual before batch processing.

## Run from source

Extract the entire archive into a new folder. Python 3.10+, Tkinter and Pillow are required. From a terminal in the extracted directory:

```powershell
py -3 -m pip install -r requirements.txt
py -3 EigrutelTwins.py
```

You can then use `Lancer_Twins.cmd`. In VS Code, open the extracted folder first. Keep `EigrutelTwins.py`, the four `twins_*.py` modules, both icons and `Manuel-Twins.html` together.

The old `doublons_index.db` is not modified or imported. Run a new scan; the original images remain untouched by indexing.

## Build for Windows

Double-click **Construire_Twins.cmd** on Windows with Python installed. It creates `.venv`, installs build dependencies and produces **dist/Twins-1.0.0.exe**. The initial dependency download needs Internet access; application use does not.

Modules, icons and manual are bundled. The builder verifies EXE icon resources. End users do not need Python. **No precompiled EXE is included.** Windows building and visual behavior still need local verification. Replace any pinned shortcut pointing to an older application.

## Data and moves

Discarded copies stay in the displayed duplicates folder. The default is Documents/Doublons for a source on C:, or Doublons at the root of another Windows drive. Choose another destination if needed; it is created only on the first move.

Cross-drive moves copy exclusively, verify bytes, log both paths and then remove the original. Files changed since scanning remain in place. Exact batch processing revalidates the retained file too. Interruption keeps completed moves. There is no automatic undo button; logged paths allow manual restoration.

On Windows, preferences, `twins_index.db`, `moves.jsonl`, manual copies and icon diagnostics live in `%LOCALAPPDATA%\EigrutelLab\Twins`. Other systems use `~/.local/share/EigrutelLab/Twins`. A fresh scan is required at each launch. No account or data collection; images are never uploaded. FR/EN does not alter names or paths. Files are not re-encoded. Keep backups and avoid concurrent edits in other applications.

## Checks

```powershell
py -3 -m unittest discover -v
```

**30 automated tests passed** in the preparation environment. They cover exact and visual matching, dHash limitations, distance searches, damaged files, EXIF orientation, collisions, cancellation, changed files, retention rules, journal failure, transactional indexing and icons. Windows icon APIs are mocked; actual Windows UI and executable checks remain necessary.

## Licenses

Code: [GNU AGPL v3.0 or later](LICENSE).
Documentation and templates: [CC BY-SA 4.0](LICENSE-DOCS), unless stated otherwise.
Eigrutel / Eigrutel Lab / Eigrutel BD Academy trademarks, logos and distinctive signs are reserved. Icons are branding assets excluded from the documentation license. Dependencies retain their respective licenses.

[Eigrutel Lab](https://www.stripmee.com/eigrutel-lab/) · [Tools](https://www.stripmee.com/logitheque/) · [Support](https://tipeee.com/leturgie)
