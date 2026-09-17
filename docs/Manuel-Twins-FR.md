# TWINS / 1.0.0 / 17-09-2026
Eigrutel Lab / Atelier d’outils libres pour la bande dessinée

## 1. CHOISIR ET ANALYSER
Choisissez un dossier et, si nécessaire, cochez « Inclure sous-dossiers ». Vérifiez le dossier des doublons affiché, puis cliquez sur Analyser. L’analyse et la recherche tournent en arrière-plan ; Arrêter ou Échap les interrompt. Pendant ces opérations, les déplacements et le changement de dossier sont bloqués. Une analyse interrompue ne remplace pas les derniers résultats complets.
Formats : JPEG, PNG, WebP, TIFF, BMP, GIF. Les images illisibles apparaissent dans le rapport. Les liens symboliques et les dossiers Doublons / _Doublons sont ignorés, ainsi que le dossier de destination choisi. Aucun fichier n’est déplacé par l’analyse.

## 2. DOUBLONS EXACTS ET IMAGES PROCHES
Doublons exacts : fichiers dont l’empreinte SHA-256 est identique, donc identiques octet par octet dans les limites usuelles de cette empreinte. Une différence de métadonnées produit une autre empreinte.
Images proches : comparaison de l’aspect par dHash, uniquement entre images de même largeur et hauteur après orientation EXIF. Une tolérance de 0 exige une empreinte visuelle identique ; cela ne prouve pas que les images sont identiques. Plus la tolérance est grande (jusqu’à 20), plus la recherche est large et susceptible de faux positifs. Les images unies, les différences de couleur et certains détails peuvent être mal distingués.
Les groupes visuels sont formés autour d’une image de départ ; chaque membre est proche de cette image, pas nécessairement de tous les autres. Changer l’image de référence ne recalcule pas le groupe. Les fichiers exacts peuvent également apparaître dans ce mode. Pour les GIF animés, TIFF multipages et autres formats à plusieurs images, seule la première image sert à la comparaison visuelle ; la comparaison exacte porte sur tout le fichier.

## 3. COMPARER
Choisissez un groupe à gauche. La référence est à gauche, l’image comparée à droite. Les boutons Précédente / Suivante font défiler les autres images du groupe. Cliquez sur un fichier de la liste pour l’afficher à droite. Échanger gauche / droite change la référence. Les aperçus suivent le redimensionnement de la fenêtre et l’orientation EXIF.
Double-cliquez sur un aperçu pour ouvrir l’image dans son application habituelle. Emplacement ouvre le dossier du fichier. Les informations indiquent son nom, ses dimensions, son poids et son chemin.

## 4. METTRE DE CÔTÉ UNE IMAGE
Le bouton Déplacer dans Doublons agit seulement sur l’image du panneau correspondant. Les fichiers sont copiés dans le dossier de destination sans écrasement, contrôlés, puis retirés de leur emplacement d’origine. Un suffixe numérique distingue les noms déjà présents. Les déplacements entre disques sont pris en charge.
Le contenu est comparé à celui relevé pendant l’analyse. Si le fichier a changé, il reste en place et doit être analysé à nouveau. Évitez de modifier les mêmes images dans un autre logiciel pendant le traitement.
Aucune suppression définitive n’est proposée : les fichiers écartés restent dans le dossier des doublons. Pour revenir en arrière, replacez-les manuellement à leur emplacement d’origine, indiqué dans le journal. Il n’existe pas de bouton d’annulation automatique.

## 5. TRAITER LES DOUBLONS EXACTS
Cette commande traite uniquement les groupes exacts, même si le mode Images proches est affiché. Choisissez le fichier à conserver : le plus récent selon sa date de modification, le nom le plus court ou le nom le plus long. Les égalités sont départagées par le chemin alphabétique. Un récapitulatif indique le nombre de groupes, les fichiers déplacés et la destination avant confirmation.
Le fichier conservé et chaque copie sont revérifiés avant le déplacement. Le traitement en série n’est jamais appliqué aux seules ressemblances visuelles. Interrompre un traitement conserve les déplacements déjà terminés ; les fichiers restants sont laissés en place. Le journal conserve les chemins pour une remise en place manuelle.

## 6. DESTINATION ET DONNÉES
Par défaut, le dossier proposé est Documents/Doublons pour un dossier source sur C:, et Doublons à la racine du disque pour un autre lecteur Windows. Sur les autres systèmes, il s’agit de Documents/Doublons, ou Doublons dans le dossier personnel si Documents n’existe pas. Vous pouvez changer cette destination avant tout déplacement. Le dossier n’est créé qu’au premier déplacement ; s’il n’est pas accessible en écriture, le fichier source reste en place.
Sous Windows, préférences, index et journal sont enregistrés dans %LOCALAPPDATA%/EigrutelLab/Twins. Sur les autres systèmes : ~/.local/share/EigrutelLab/Twins. L’index est un cache reconstructible : relancez une analyse à chaque démarrage. L’ancien fichier doublons_index.db n’est pas modifié ni importé. Les images d’origine ne sont ni converties ni réencodées.
Le journal moves.jsonl consigne une entrée « prepared » avant le retrait du fichier d’origine et « completed » à la fin. En cas de coupure, consultez les deux emplacements avant une remise en place. FR/EN traduit l’interface et l’aide, jamais les chemins ni les noms de vos fichiers. Aucun compte, aucune collecte ni transmission de données.

## 7. RACCOURCIS
Gauche / droite : groupe précédent / suivant.
Haut / bas : image comparée précédente / suivante.
Entrée : échanger les deux images.
Suppr ou 3 : déplacer l’image de droite dans Doublons.
Maj+Suppr ou 1 : déplacer l’image de gauche dans Doublons.
Échap : arrêter le traitement. Les raccourcis de déplacement sont neutralisés dans les champs de saisie et les fenêtres de dialogue.

## 8. CRÉDITS ET LICENCES
Programme conçu et développé par Simon Léturgie dans le cadre d’Eigrutel BD Academy.
Code : GNU AGPL v3.0 ou version ultérieure.
Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab / Eigrutel BD Academy : réservés.
