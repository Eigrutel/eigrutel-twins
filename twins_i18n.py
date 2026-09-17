# Eigrutel Lab / Twins 1.0.0 / 17-09-2026
# Simon Léturgie / Code : GNU AGPL v3.0 ou ultérieure.
"""Interface strings and bilingual user manual; filenames are never translated."""
LANGUAGE = 'fr'
EN = {
    'Choisir dossier': 'Choose folder', 'Inclure sous-dossiers': 'Include subfolders',
    'Analyser': 'Scan', 'Arrêter': 'Stop', 'Dossier': 'Folder',
    'Aucun dossier choisi': 'No folder selected', 'Détection': 'Detection',
    'Doublons exacts': 'Exact duplicates', 'Images proches': 'Similar images',
    'Tolérance visuelle (0–20)': 'Visual tolerance (0–20)',
    'Même définition • contrôle visuel nécessaire': 'Same dimensions • visual review required',
    'Dossier des doublons': 'Duplicates folder', 'Changer': 'Change', 'Ouvrir': 'Open',
    'Groupes': 'Groups', 'Images du groupe': 'Images in group',
    '◀ Précédent': '◀ Previous', 'Suivant ▶': 'Next ▶',
    'Référence': 'Reference', 'Comparaison': 'Comparison',
    'Échanger gauche / droite': 'Swap left / right',
    'Traiter les doublons exacts': 'Process exact duplicates',
    '▲ Précédente': '▲ Previous', '▼ Suivante': '▼ Next',
    'Ouvrir l’image': 'Open image', 'Emplacement': 'Location',
    'Déplacer dans Doublons': 'Move to duplicates',
    'Choisissez un dossier, puis lancez l’analyse.': 'Choose a folder, then start a scan.',
    'Aucun groupe': 'No groups', 'Aucun résultat dans ce mode': 'No results in this mode',
    'Analyse requise': 'Scan required', 'VISUEL': 'VISUAL',
    '{count} images • groupe {current}/{total}': '{count} images • group {current}/{total}',
    '{count} images indexées • {groups} groupes': '{count} indexed images • {groups} groups',
    'Nom : {name}\nDimensions : {width} × {height} px • Poids : {size}\n{path}':
        'Name: {name}\nDimensions: {width} × {height} px • Size: {size}\n{path}',
    'Aperçu indisponible\n{error}': 'Preview unavailable\n{error}',
    'Analyse en cours : {count} fichiers': 'Scanning: {count} files',
    'Recherche en cours : {count} images': 'Searching: {count} images',
    'Déplacement : {count}/{total}': 'Moving: {count}/{total}',
    'Arrêt demandé…': 'Stopping…', 'Traitement interrompu.': 'Operation stopped.',
    'Analyse terminée : {count} images • {errors} erreurs.': 'Scan complete: {count} images • {errors} errors.',
    'Déplacements terminés : {count} fichiers • {errors} erreurs.': 'Moves complete: {count} files • {errors} errors.',
    'Erreur': 'Error', 'Informations': 'Information', 'Rapport': 'Report',
    'Choisissez d’abord un dossier.': 'Choose a folder first.',
    'Lancez une analyse avant la détection.': 'Run a scan before detecting duplicates.',
    'La tolérance doit être un entier compris entre 0 et 20.': 'Tolerance must be an integer between 0 and 20.',
    'Le dossier analysé ne peut pas se trouver dans le dossier des doublons.':
        'The scanned folder cannot be inside the duplicates folder.',
    'Cette image a changé depuis l’analyse. Relancez l’analyse avant de la déplacer.':
        'This image has changed since scanning. Scan again before moving it.',
    'Cette opération déplace les fichiers ; elle ne fusionne pas leurs pixels.':
        'This operation moves files; it does not merge image pixels.',
    'Fichier à conserver dans chaque groupe': 'File to keep in each group',
    'Le plus récent (date de modification)': 'Most recent (modification time)',
    'Le nom le plus court': 'Shortest filename', 'Le nom le plus long': 'Longest filename',
    'Annuler': 'Cancel', 'Préparer': 'Prepare', 'Confirmer le déplacement': 'Confirm move',
    '{groups} groupes exacts.\n{count} fichiers seront déplacés ; un fichier restera dans chaque groupe.\n\nDestination :\n{destination}':
        '{groups} exact groups.\n{count} files will be moved; one file will remain in each group.\n\nDestination:\n{destination}',
    'Aucun doublon exact à traiter.': 'No exact duplicates to process.',
    'Le fichier conservé et chaque copie sont revérifiés avant déplacement.':
        'The retained file and each copy are checked again before moving.',
    'Twins / Manuel': 'Twins / Manual', 'Fermer': 'Close', 'Manuel complet': 'Complete manual',
    'Journal des déplacements': 'Move log', 'Afficher le rapport': 'Show report',
    'Aucune erreur signalée.': 'No errors reported.',
    'G': 'L', 'D': 'R', 'octets': 'bytes', 'Ko': 'KB', 'Mo': 'MB', 'Go': 'GB', 'To': 'TB',
    'Lecture seule pendant le traitement.': 'Read-only while processing.',
}


def tr(text, **values):
    result = EN.get(text, text) if LANGUAGE == 'en' else text
    return result.format(**values) if values else result


MANUAL = {
'fr': '''TWINS / 1.0.0 / 17-09-2026
Eigrutel Lab / Atelier d’outils libres pour la bande dessinée

1. CHOISIR ET ANALYSER
Choisissez un dossier et, si nécessaire, cochez « Inclure sous-dossiers ». Vérifiez le dossier des doublons affiché, puis cliquez sur Analyser. L’analyse et la recherche tournent en arrière-plan ; Arrêter ou Échap les interrompt. Pendant ces opérations, les déplacements et le changement de dossier sont bloqués. Une analyse interrompue ne remplace pas les derniers résultats complets.
Formats : JPEG, PNG, WebP, TIFF, BMP, GIF. Les images illisibles apparaissent dans le rapport. Les liens symboliques et les dossiers Doublons / _Doublons sont ignorés, ainsi que le dossier de destination choisi. Aucun fichier n’est déplacé par l’analyse.

2. DOUBLONS EXACTS ET IMAGES PROCHES
Doublons exacts : fichiers dont l’empreinte SHA-256 est identique, donc identiques octet par octet dans les limites usuelles de cette empreinte. Une différence de métadonnées produit une autre empreinte.
Images proches : comparaison de l’aspect par dHash, uniquement entre images de même largeur et hauteur après orientation EXIF. Une tolérance de 0 exige une empreinte visuelle identique ; cela ne prouve pas que les images sont identiques. Plus la tolérance est grande (jusqu’à 20), plus la recherche est large et susceptible de faux positifs. Les images unies, les différences de couleur et certains détails peuvent être mal distingués.
Les groupes visuels sont formés autour d’une image de départ ; chaque membre est proche de cette image, pas nécessairement de tous les autres. Changer l’image de référence ne recalcule pas le groupe. Les fichiers exacts peuvent également apparaître dans ce mode. Pour les GIF animés, TIFF multipages et autres formats à plusieurs images, seule la première image sert à la comparaison visuelle ; la comparaison exacte porte sur tout le fichier.

3. COMPARER
Choisissez un groupe à gauche. La référence est à gauche, l’image comparée à droite. Les boutons Précédente / Suivante font défiler les autres images du groupe. Cliquez sur un fichier de la liste pour l’afficher à droite. Échanger gauche / droite change la référence. Les aperçus suivent le redimensionnement de la fenêtre et l’orientation EXIF.
Double-cliquez sur un aperçu pour ouvrir l’image dans son application habituelle. Emplacement ouvre le dossier du fichier. Les informations indiquent son nom, ses dimensions, son poids et son chemin.

4. METTRE DE CÔTÉ UNE IMAGE
Le bouton Déplacer dans Doublons agit seulement sur l’image du panneau correspondant. Les fichiers sont copiés dans le dossier de destination sans écrasement, contrôlés, puis retirés de leur emplacement d’origine. Un suffixe numérique distingue les noms déjà présents. Les déplacements entre disques sont pris en charge.
Le contenu est comparé à celui relevé pendant l’analyse. Si le fichier a changé, il reste en place et doit être analysé à nouveau. Évitez de modifier les mêmes images dans un autre logiciel pendant le traitement.
Aucune suppression définitive n’est proposée : les fichiers écartés restent dans le dossier des doublons. Pour revenir en arrière, replacez-les manuellement à leur emplacement d’origine, indiqué dans le journal. Il n’existe pas de bouton d’annulation automatique.

5. TRAITER LES DOUBLONS EXACTS
Cette commande traite uniquement les groupes exacts, même si le mode Images proches est affiché. Choisissez le fichier à conserver : le plus récent selon sa date de modification, le nom le plus court ou le nom le plus long. Les égalités sont départagées par le chemin alphabétique. Un récapitulatif indique le nombre de groupes, les fichiers déplacés et la destination avant confirmation.
Le fichier conservé et chaque copie sont revérifiés avant le déplacement. Le traitement en série n’est jamais appliqué aux seules ressemblances visuelles. Interrompre un traitement conserve les déplacements déjà terminés ; les fichiers restants sont laissés en place. Le journal conserve les chemins pour une remise en place manuelle.

6. DESTINATION ET DONNÉES
Par défaut, le dossier proposé est Documents/Doublons pour un dossier source sur C:, et Doublons à la racine du disque pour un autre lecteur Windows. Sur les autres systèmes, il s’agit de Documents/Doublons, ou Doublons dans le dossier personnel si Documents n’existe pas. Vous pouvez changer cette destination avant tout déplacement. Le dossier n’est créé qu’au premier déplacement ; s’il n’est pas accessible en écriture, le fichier source reste en place.
Sous Windows, préférences, index et journal sont enregistrés dans %LOCALAPPDATA%/EigrutelLab/Twins. Sur les autres systèmes : ~/.local/share/EigrutelLab/Twins. L’index est un cache reconstructible : relancez une analyse à chaque démarrage. L’ancien fichier doublons_index.db n’est pas modifié ni importé. Les images d’origine ne sont ni converties ni réencodées.
Le journal moves.jsonl consigne une entrée « prepared » avant le retrait du fichier d’origine et « completed » à la fin. En cas de coupure, consultez les deux emplacements avant une remise en place. FR/EN traduit l’interface et l’aide, jamais les chemins ni les noms de vos fichiers. Aucun compte, aucune collecte ni transmission de données.

7. RACCOURCIS
Gauche / droite : groupe précédent / suivant.
Haut / bas : image comparée précédente / suivante.
Entrée : échanger les deux images.
Suppr ou 3 : déplacer l’image de droite dans Doublons.
Maj+Suppr ou 1 : déplacer l’image de gauche dans Doublons.
Échap : arrêter le traitement. Les raccourcis de déplacement sont neutralisés dans les champs de saisie et les fenêtres de dialogue.

8. CRÉDITS ET LICENCES
Programme conçu et développé par Simon Léturgie dans le cadre d’Eigrutel BD Academy.
Code : GNU AGPL v3.0 ou version ultérieure.
Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab / Eigrutel BD Academy : réservés.
''',
'en': '''TWINS / 1.0.0 / 2026-09-17
Eigrutel Lab / Open tools workshop for comics

1. CHOOSE AND SCAN
Choose a folder and optionally enable Include subfolders. Check the displayed duplicates folder, then click Scan. Scanning and searching run in the background; Stop or Escape interrupts them. Moves and folder changes are blocked while processing. An interrupted scan does not replace the last complete results.
Formats: JPEG, PNG, WebP, TIFF, BMP, GIF. Unreadable images appear in the report. Symbolic links, Doublons / _Doublons directories and the selected destination directory are excluded. Scanning never moves files.

2. EXACT DUPLICATES AND SIMILAR IMAGES
Exact duplicates: files with identical SHA-256 digests, indicating byte-for-byte equality within the usual limits of that digest. Different metadata produces a different digest.
Similar images: dHash comparison, restricted to images with the same width and height after EXIF orientation. Tolerance 0 requires an identical visual hash; this does not prove image equality. Higher tolerance (up to 20) widens the search and increases false positives. Flat images, color changes and some details may not be distinguished.
Visual groups are formed around an initial image. Each member is similar to that anchor, not necessarily to every other member. Changing the reference image does not recompute the group. Exact duplicates can also appear in this mode. For animated GIF, multipage TIFF and other multi-image formats, only the first image is used for visual matching; exact matching hashes the entire file.

3. COMPARE
Select a group on the left. The reference is shown on the left and the comparison image on the right. Previous / Next cycles through the other images in the group. Click a filename to show it on the right. Swap left / right changes the reference. Previews follow window resizing and EXIF orientation.
Double-click a preview to open the image in its default application. Location opens the file's folder. Information includes filename, dimensions, size and path.

4. SET AN IMAGE ASIDE
Move to duplicates acts only on the image in that panel. Files are copied to the destination without overwriting, checked, then removed from the original location. A numeric suffix distinguishes existing names. Moves between drives are supported.
Content is checked against the scan. If a file changed, it is left in place and must be scanned again. Avoid editing the same files in other applications during processing.
There is no permanent-delete command: removed copies remain in the duplicates folder. To undo a move, manually return the file to its original location recorded in the log. There is no automatic undo button.

5. PROCESS EXACT DUPLICATES
This command processes only exact groups, even when Similar images is displayed. Choose the file to retain: most recent by modification time, shortest filename or longest filename. Ties use alphabetical path order. Review the number of groups, files to move and destination before confirming.
The retained file and every copy are verified again before moving. Batch processing never applies to visual-only similarities. Stopping retains completed moves; remaining files stay in place. Original and destination paths are logged for manual recovery.

6. DESTINATION AND LOCAL DATA
The default destination is Documents/Doublons for a source on C:, or Doublons at the root of another Windows drive. On other systems it is Documents/Doublons, or Doublons under your home folder if Documents does not exist. Change the destination before moving if needed. It is created only on the first move. If it cannot be written, the original file stays in place.
On Windows, settings, index and journal live in %LOCALAPPDATA%/EigrutelLab/Twins. Other systems use ~/.local/share/EigrutelLab/Twins. The index is a rebuildable cache: scan again at each launch. The old doublons_index.db is neither modified nor imported. Original images are never converted or re-encoded.
The moves.jsonl journal writes a prepared entry before removing an original and a completed entry afterward. If processing is interrupted by a power failure, check both locations before restoring files. FR/EN translates the interface and help, never filenames or paths. No account, data collection or network transfers.

7. SHORTCUTS
Left / right: previous / next group.
Up / down: previous / next comparison image.
Enter: swap images.
Delete or 3: move the right image to duplicates.
Shift+Delete or 1: move the left image to duplicates.
Escape: stop processing. Move shortcuts are inactive in text fields and dialog windows.

8. CREDITS AND LICENSES
Designed and developed by Simon Léturgie as part of Eigrutel BD Academy.
Code: GNU AGPL v3.0 or later.
Documentation and templates: CC BY-SA 4.0, unless stated otherwise.
Eigrutel / Eigrutel Lab / Eigrutel BD Academy trademarks, logos and distinctive signs: reserved.
'''
}
