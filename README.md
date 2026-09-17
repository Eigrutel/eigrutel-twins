# Twins 1.0.0

**Repérer les doublons d’images, les comparer et mettre les copies de côté.**

Eigrutel Lab / Atelier d’outils libres pour la bande dessinée.
Programme conçu et développé par Simon Léturgie dans le cadre d’Eigrutel BD Academy.

[English](README-EN.md) · [Manuel français](docs/Manuel-Twins-FR.md) · [English manual](docs/Twins-User-Manual-EN.md)

<img src="Twins.png" alt="Twins / Eigrutel Lab" width="96">

## Dans la famille Morgue et Photo

Twins reprend le fond papier, le bleu sombre `#1F3A44`, le rouge `#7F2D30`, l’ocre `#C47A2C`, le choix FR/EN et la fenêtre d’aide de la famille Eigrutel Lab. L’icône de Morgue et Photo est reprise sans modification, sous les noms `Twins.ico` et `Twins.png`. Le correctif de barre des tâches Windows est adapté à une identité propre à Twins.

Twins est consacré aux doublons : il n’a pas besoin d’ouvrir Morgue ou Photo et ses préférences restent séparées. Le module historique `ui_common.py` n’est plus nécessaire.

## Fonctions conservées et améliorées

- Analyse d’un dossier, sous-dossiers en option ; JPEG, PNG, WebP, TIFF, BMP et GIF.
- Doublons exacts par SHA-256 et images proches par dHash, avec tolérance de 0 à 20.
- Deux aperçus, groupes et liste des images, navigation, échange de référence et métadonnées de base.
- Orientation EXIF et aperçus adaptés à la taille de la fenêtre.
- Ouverture de l’image par double-clic et accès à son emplacement.
- Mise de côté de l’image gauche ou droite dans un dossier Doublons configurable.
- Traitement des **seuls doublons exacts** en conservant le fichier le plus récent, le nom le plus court ou le nom le plus long.
- Analyse, recherche et déplacements en arrière-plan, arrêt avec Échap ou Arrêter.
- Contrôle des fichiers avant déplacement, copie vérifiée sans écrasement et journal local.
- Interface et manuels FR/EN ; préférences mémorisées.

Une ressemblance visuelle n’est pas une preuve d’identité. Ce mode reste limité aux images de même définition après orientation EXIF. Les couleurs ou de petits détails peuvent ne pas être distingués ; seul le premier cadre des formats animés ou multipages est comparé visuellement. La recherche exacte porte sur l’intégralité du fichier. Consultez le manuel avant un traitement en série.

## Lancer Twins depuis les sources

Extrayez **toute l’archive dans un nouveau dossier**. Python 3.10 ou ultérieur, Tkinter et Pillow sont nécessaires. Dans un terminal ouvert dans le dossier extrait :

```powershell
py -3 -m pip install -r requirements.txt
py -3 EigrutelTwins.py
```

Vous pouvez ensuite utiliser `Lancer_Twins.cmd`. Dans Visual Studio Code, ouvrez le dossier extrait avant d’ouvrir le terminal.

Conservez ensemble `EigrutelTwins.py`, les quatre modules `twins_core.py`, `twins_i18n.py`, `twins_ui.py`, `twins_windows_icon.py`, les deux icônes et `Manuel-Twins.html`.

Les anciennes versions de Twins et de `ui_common.py` ne doivent pas remplacer ces modules. L’ancien index `doublons_index.db` n’est ni modifié ni importé : une nouvelle analyse le remplace fonctionnellement sans toucher aux images.

## Construire un EXE Windows

Sur Windows, avec Python installé, double-cliquez sur **Construire_Twins.cmd**. Le script crée `.venv`, installe les dépendances de construction et produit :

```text
dist/Twins-1.0.0.exe
```

La première construction nécessite Internet pour télécharger les dépendances. L’usage de Twins fonctionne hors connexion. Le constructeur embarque les modules, les icônes et le manuel ; il vérifie les ressources d’icône de l’EXE. L’utilisateur final n’a pas besoin de Python.

**Aucun EXE précompilé n’est inclus.** La version Python a été testée et validée par Simon Léturgie. L’exécutable construit doit encore être essayé sous Windows. Remplacez les anciens raccourcis épinglés s’ils pointent vers un autre programme.

## Fichiers et données

Les fichiers écartés restent dans le dossier des doublons indiqué à l’écran. Pour un dossier source sur C:, la proposition initiale est Documents/Doublons ; pour un autre disque Windows, Doublons à sa racine. Vous pouvez choisir un autre dossier. Il n’est créé qu’au premier déplacement.

Un déplacement entre disques copie le fichier sans écrasement, vérifie son contenu, consigne ses chemins dans le journal, puis retire l’original. Les fichiers modifiés depuis l’analyse restent en place. Le traitement en série revérifie aussi le fichier conservé. Une interruption garde les déplacements déjà terminés ; il n’existe pas de bouton d’annulation automatique. Les chemins du journal permettent une remise en place manuelle.

Sous Windows, les données du programme se trouvent dans `%LOCALAPPDATA%\EigrutelLab\Twins` :

| Élément | Rôle |
| --- | --- |
| `settings.json` | Langue, dossier source, destination, sous-dossiers et tolérance |
| `twins_index.db` | Index SQLite local, recréé après une analyse complète |
| `moves.jsonl` | Journal des chemins d’origine et de destination |
| `manuals` | Copie de lecture du manuel hors connexion |
| `logs/twins-icons.log` | Diagnostic d’icône en cas d’erreur |

Une analyse est nécessaire à chaque lancement. Aucun compte ni collecte ; les images ne sont pas transmises à un serveur. Leurs noms et chemins ne sont pas traduits par le choix FR/EN. Les fichiers ne sont pas réencodés. Conservez vos sauvegardes et évitez les modifications simultanées dans un autre logiciel.

## Vérifications

```powershell
py -3 -m unittest discover -v
```

**30 tests automatisés réussis** dans l’environnement de préparation. Ils couvrent les doublons exacts, les limites du dHash, la recherche par distance, les fichiers corrompus, l’orientation EXIF, les collisions, l’annulation, les fichiers modifiés, les règles de conservation, l’échec du journal, l’index transactionnel et les icônes. Les appels Windows d’icône sont simulés ; ces tests ne remplacent pas un essai graphique sur Windows.

## Licences

Code : [GNU AGPL v3.0 ou ultérieure](LICENSE).
Documentation et modèles : [CC BY-SA 4.0](LICENSE-DOCS), sauf mention contraire.
Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab / Eigrutel BD Academy : réservés. Les icônes sont des éléments de marque, exclus de la licence documentaire. Les dépendances tierces conservent leurs licences respectives.

[Présentation Eigrutel Lab](https://www.stripmee.com/eigrutel-lab/) · [Logithèque](https://www.stripmee.com/logitheque/) · [Soutenir](https://tipeee.com/leturgie)
