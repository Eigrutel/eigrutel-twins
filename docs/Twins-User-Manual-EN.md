# TWINS / 1.0.0 / 2026-09-17
Eigrutel Lab / Open tools workshop for comics

## 1. CHOOSE AND SCAN
Choose a folder and optionally enable Include subfolders. Check the displayed duplicates folder, then click Scan. Scanning and searching run in the background; Stop or Escape interrupts them. Moves and folder changes are blocked while processing. An interrupted scan does not replace the last complete results.
Formats: JPEG, PNG, WebP, TIFF, BMP, GIF. Unreadable images appear in the report. Symbolic links, Doublons / _Doublons directories and the selected destination directory are excluded. Scanning never moves files.

## 2. EXACT DUPLICATES AND SIMILAR IMAGES
Exact duplicates: files with identical SHA-256 digests, indicating byte-for-byte equality within the usual limits of that digest. Different metadata produces a different digest.
Similar images: dHash comparison, restricted to images with the same width and height after EXIF orientation. Tolerance 0 requires an identical visual hash; this does not prove image equality. Higher tolerance (up to 20) widens the search and increases false positives. Flat images, color changes and some details may not be distinguished.
Visual groups are formed around an initial image. Each member is similar to that anchor, not necessarily to every other member. Changing the reference image does not recompute the group. Exact duplicates can also appear in this mode. For animated GIF, multipage TIFF and other multi-image formats, only the first image is used for visual matching; exact matching hashes the entire file.

## 3. COMPARE
Select a group on the left. The reference is shown on the left and the comparison image on the right. Previous / Next cycles through the other images in the group. Click a filename to show it on the right. Swap left / right changes the reference. Previews follow window resizing and EXIF orientation.
Double-click a preview to open the image in its default application. Location opens the file's folder. Information includes filename, dimensions, size and path.

## 4. SET AN IMAGE ASIDE
Move to duplicates acts only on the image in that panel. Files are copied to the destination without overwriting, checked, then removed from the original location. A numeric suffix distinguishes existing names. Moves between drives are supported.
Content is checked against the scan. If a file changed, it is left in place and must be scanned again. Avoid editing the same files in other applications during processing.
There is no permanent-delete command: removed copies remain in the duplicates folder. To undo a move, manually return the file to its original location recorded in the log. There is no automatic undo button.

## 5. PROCESS EXACT DUPLICATES
This command processes only exact groups, even when Similar images is displayed. Choose the file to retain: most recent by modification time, shortest filename or longest filename. Ties use alphabetical path order. Review the number of groups, files to move and destination before confirming.
The retained file and every copy are verified again before moving. Batch processing never applies to visual-only similarities. Stopping retains completed moves; remaining files stay in place. Original and destination paths are logged for manual recovery.

## 6. DESTINATION AND LOCAL DATA
The default destination is Documents/Doublons for a source on C:, or Doublons at the root of another Windows drive. On other systems it is Documents/Doublons, or Doublons under your home folder if Documents does not exist. Change the destination before moving if needed. It is created only on the first move. If it cannot be written, the original file stays in place.
On Windows, settings, index and journal live in %LOCALAPPDATA%/EigrutelLab/Twins. Other systems use ~/.local/share/EigrutelLab/Twins. The index is a rebuildable cache: scan again at each launch. The old doublons_index.db is neither modified nor imported. Original images are never converted or re-encoded.
The moves.jsonl journal writes a prepared entry before removing an original and a completed entry afterward. If processing is interrupted by a power failure, check both locations before restoring files. FR/EN translates the interface and help, never filenames or paths. No account, data collection or network transfers.

## 7. SHORTCUTS
Left / right: previous / next group.
Up / down: previous / next comparison image.
Enter: swap images.
Delete or 3: move the right image to duplicates.
Shift+Delete or 1: move the left image to duplicates.
Escape: stop processing. Move shortcuts are inactive in text fields and dialog windows.

## 8. CREDITS AND LICENSES
Designed and developed by Simon Léturgie as part of Eigrutel BD Academy.
Code: GNU AGPL v3.0 or later.
Documentation and templates: CC BY-SA 4.0, unless stated otherwise.
Eigrutel / Eigrutel Lab / Eigrutel BD Academy trademarks, logos and distinctive signs: reserved.
