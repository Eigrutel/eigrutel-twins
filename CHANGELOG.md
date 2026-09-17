# Historique / Changelog

## 1.0.0 - 2026-09-17

### Français

- Harmonisation avec Morgue et Photo : palette, boutons, icônes, langue et aide.
- Interface et manuels français / anglais, langue et réglages persistants.
- Nettoyage : séparation interface, moteur, traductions et icônes Windows ; retrait de `ui_common.py`.
- Conservation de la comparaison côte à côte, des deux modes et des trois règles de conservation.
- Recherche visuelle par distance de Hamming en arrière-plan, sans bloquer Tkinter.
- Événements de travail transmis par file de messages ; aucun accès Tkinter depuis les workers.
- Lecture EXIF, redimensionnement des aperçus, rapports d’erreurs et raccourcis isolés des champs de saisie.
- Déplacements interdisques par copie vérifiée sans écrasement, contrôle des fichiers modifiés et journal durable.
- Résultats précédents conservés si l’analyse est interrompue ; fermeture attendant l’arrêt du travail.
- Dossier de destination configurable et données séparées dans EigrutelLab/Twins.

### English

- Aligned with Morgue and Photo: palette, buttons, icons, language and help.
- FR/EN interface and manuals; saved settings and language.
- Separate UI, engine, translations and Windows branding modules; removed `ui_common.py`.
- Retained side-by-side comparison, both detection modes and all three retention rules.
- Background Hamming-distance search; queued worker events without Tk calls from workers.
- EXIF previews, resizing, error reports and shortcuts isolated from text fields.
- Verified cross-drive moves, no overwriting, changed-file checks and a durable journal.
- Cancelled scans retain prior results; closing waits for workers to stop.
- Configurable destination and separate EigrutelLab/Twins local data.
