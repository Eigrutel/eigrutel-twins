# -*- coding: utf-8 -*-
"""
Eigrutel Lab - Atelier d'outils libres pour la bande dessinée
Programme conçu et développé par Simon Léturgie dans le cadre d'Eigrutel BD Academy.
Nom : Twins
Version : 1.0.0
Date : 17-09-2026
Code : GNU AGPL v3.0 ou version ultérieure.
Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab / Eigrutel BD Academy : réservés.

Run: python EigrutelTwins.py. Requires Python 3.10+, Tkinter and Pillow.
Keep the supplied twins_*.py modules and assets alongside this file.
"""
from __future__ import annotations

import json
import os
import queue
import sqlite3
import subprocess
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageOps, ImageTk
import twins_core as core
import twins_i18n as i18n
import twins_windows_icon
from twins_i18n import tr
from twins_ui import UI, apply_style, apply_app_icon

APP_VERSION = '1.0.0'


def app_dir():
    base = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share'))
    path = base / 'EigrutelLab' / 'Twins'
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_settings(path):
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_settings(path, values):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = stream.name
            json.dump(values, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def default_destination(folder):
    drive = os.path.splitdrive(os.path.abspath(folder))[0]
    if sys.platform == 'win32' and drive and drive.upper() != 'C:':
        return str(Path(drive + os.sep) / 'Doublons')
    documents = Path.home() / 'Documents'
    return str((documents if documents.is_dir() else Path.home()) / 'Doublons')


def format_size(size):
    for unit in ('octets', 'Ko', 'Mo', 'Go', 'To'):
        if size < 1024 or unit == 'To':
            return (f'{size:.0f}' if unit == 'octets' else f'{size:.1f}') + ' ' + tr(unit)
        size /= 1024


def open_path(path, select=False):
    if not Path(path).exists():
        raise FileNotFoundError(path)
    if sys.platform == 'win32':
        if select:
            subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
        else:
            os.startfile(path)
    else:
        target = str(Path(path).parent) if select else path
        subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', target])


class App:
    def __init__(self, root):
        self.root = root
        self.data = app_dir()
        self.settings_path = self.data / 'settings.json'
        self.settings = load_settings(self.settings_path)
        language = self.settings.get('language', 'fr')
        i18n.LANGUAGE = language if language in ('fr', 'en') else 'fr'
        self.folder = str(self.settings.get('folder', ''))
        self.custom_destination = bool(self.settings.get('custom_destination', False))
        self.destination = str(self.settings.get('destination') or default_destination(self.folder or str(Path.home())))
        self.recursive = tk.BooleanVar(value=bool(self.settings.get('recursive', True)))
        threshold = str(self.settings.get('threshold', 5))
        self.threshold = tk.StringVar(value=threshold if threshold.isdecimal() and 0 <= int(threshold) <= 20 else '5')
        self.records, self.groups, self.errors = [], [], []
        self.mode = 'exact'
        self.indexed_folder = ''
        self.group_index, self.left_index, self.right_index = 0, 0, 1
        self.busy, self.closing = False, False
        self.worker = None
        self.cancel = threading.Event()
        self.events = queue.Queue()
        self.pending_result = None
        self.static_text, self.controls = [], []
        self.preview_images = [None, None]
        self.photo_images = [None, None]
        self.status_key, self.status_values = 'Choisissez un dossier, puis lancez l’analyse.', {}
        root.title('Twins / Eigrutel Lab')
        root.geometry('1380x860')
        root.minsize(1120, 740)
        apply_style(root)
        style = ttk.Style(root)
        style.configure('Detect.TButton', background='#C47A2C', foreground='white', padding=8)
        style.map('Detect.TButton', background=[('active', '#7F2D30')], foreground=[('disabled', '#BBBBBB')])
        style.configure('SideTitle.TLabel', font=('Segoe UI', 10, 'bold'))
        self.build_ui()
        apply_app_icon(root)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.report_callback_exception = self.callback_error
        self.bind_keys()
        self.refresh()
        root.after(80, self.poll)
        if sys.platform == 'win32':
            root.state('zoomed')

    def callback_error(self, kind, error, traceback):
        messagebox.showerror(tr('Erreur'), str(error), parent=self.root)

    def label(self, parent, key, **kwargs):
        widget = ttk.Label(parent, text=tr(key), **kwargs)
        self.static_text.append((widget, key))
        return widget

    def button(self, parent, key, command, style='Side.TButton', locked=True, **kwargs):
        widget = ttk.Button(parent, text=tr(key), command=command, style=style, **kwargs)
        self.static_text.append((widget, key))
        if locked:
            self.controls.append(widget)
        return widget

    def build_ui(self):
        top = ttk.Frame(self.root, style='Topbar.TFrame', padding=(14, 8))
        top.pack(fill='x')
        ttk.Label(top, text='Twins', style='TopbarTitle.TLabel').pack(side='left', padx=(0, 20))
        self.button(top, 'Choisir dossier', self.choose_folder, 'Accent.TButton').pack(side='left', padx=(0, 10))
        check = ttk.Checkbutton(top, text=tr('Inclure sous-dossiers'), variable=self.recursive,
                                style='Topbar.TCheckbutton', command=self.persist)
        check.pack(side='left', padx=(0, 12))
        self.static_text.append((check, 'Inclure sous-dossiers'))
        self.controls.append(check)
        self.button(top, 'Analyser', self.scan, 'Accent.TButton').pack(side='left')
        self.stop = self.button(top, 'Arrêter', self.stop_task, locked=False)
        self.stop.pack(side='left', padx=8)
        ttk.Button(top, text='i', width=3, style='Side.TButton', command=self.help).pack(side='right', padx=(12, 0))
        self.language_buttons = {}
        for lang in ('en', 'fr'):
            button = ttk.Button(top, text=lang.upper(), width=4, command=lambda lang=lang: self.set_language(lang))
            button.pack(side='right', padx=2)
            self.controls.append(button)
            self.language_buttons[lang] = button
        bottom = ttk.Frame(self.root, padding=(12, 5))
        bottom.pack(side='bottom', fill='x')
        self.status = ttk.Label(bottom, anchor='w')
        self.status.pack(side='left', fill='x', expand=True)
        self.button(bottom, 'Afficher le rapport', self.report, locked=False).pack(side='right', padx=8)
        ttk.Label(bottom, text='Eigrutel Lab · Twins ' + APP_VERSION).pack(side='right')
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(side='bottom', fill='x')
        body = ttk.Frame(self.root, padding=10)
        body.pack(fill='both', expand=True)
        side = ttk.Frame(body, style='Side.TFrame', width=300, padding=10)
        side.pack(side='left', fill='y', padx=(0, 10))
        side.pack_propagate(False)
        self.label(side, 'Dossier', style='SideTitle.TLabel').pack(anchor='w')
        self.folder_label = ttk.Label(side, style='SideInfo.TLabel', wraplength=280)
        self.folder_label.pack(fill='x', pady=(3, 12))
        self.label(side, 'Détection', style='SideTitle.TLabel').pack(anchor='w')
        for mode, key in [('exact', 'Doublons exacts'), ('visual', 'Images proches')]:
            self.button(side, key, lambda mode=mode: self.detect(mode), 'Detect.TButton').pack(fill='x', pady=3)
        row = ttk.Frame(side, style='Side.TFrame')
        row.pack(fill='x', pady=(8, 3))
        self.label(row, 'Tolérance visuelle (0–20)', style='SideInfo.TLabel').pack(side='left')
        spin = ttk.Spinbox(row, from_=0, to=20, textvariable=self.threshold, width=4)
        spin.pack(side='right')
        self.controls.append(spin)
        self.label(side, 'Même définition • contrôle visuel nécessaire', style='SideInfo.TLabel', wraplength=280).pack(fill='x', pady=(0, 12))
        self.label(side, 'Dossier des doublons', style='SideTitle.TLabel').pack(anchor='w')
        self.destination_label = ttk.Label(side, style='SideInfo.TLabel', wraplength=280)
        self.destination_label.pack(fill='x', pady=3)
        actions = ttk.Frame(side, style='Side.TFrame')
        actions.pack(fill='x', pady=(0, 10))
        self.button(actions, 'Changer', self.choose_destination).pack(side='left', fill='x', expand=True, padx=(0, 4))
        self.button(actions, 'Ouvrir', lambda: self.open(self.destination)).pack(side='left', fill='x', expand=True)
        self.label(side, 'Groupes', style='SideTitle.TLabel').pack(anchor='w')
        self.group_list = self.listbox(side, 5)
        self.group_list.bind('<<ListboxSelect>>', self.select_group)
        self.label(side, 'Images du groupe', style='SideTitle.TLabel').pack(anchor='w', pady=(10, 0))
        self.image_list = self.listbox(side, 4, expand=True)
        self.image_list.bind('<<ListboxSelect>>', self.select_image)
        navigation = ttk.Frame(side, style='Side.TFrame')
        navigation.pack(fill='x', pady=(8, 0))
        self.button(navigation, '◀ Précédent', lambda: self.navigate_group(-1)).pack(side='left', fill='x', expand=True, padx=(0, 4))
        self.button(navigation, 'Suivant ▶', lambda: self.navigate_group(1)).pack(side='left', fill='x', expand=True)
        center = ttk.Frame(body)
        center.pack(side='left', fill='both', expand=True)
        toolbar = ttk.Frame(center)
        toolbar.pack(fill='x', pady=(0, 10))
        self.button(toolbar, 'Échanger gauche / droite', self.swap).pack(side='left')
        self.button(toolbar, 'Traiter les doublons exacts', self.batch_dialog, 'Accent.TButton').pack(side='right')
        self.group_label = ttk.Label(center, anchor='w')
        self.group_label.pack(fill='x', pady=(0, 8))
        panels = ttk.Frame(center)
        panels.pack(fill='both', expand=True)
        panels.columnconfigure((0, 1), weight=1, uniform='preview')
        panels.rowconfigure(0, weight=1)
        self.canvases, self.info = [], []
        for index, key in enumerate(('Référence', 'Comparaison')):
            panel = ttk.Frame(panels)
            panel.grid(row=0, column=index, sticky='nsew', padx=(0, 5) if index == 0 else (5, 0))
            panel.columnconfigure(0, weight=1)
            panel.rowconfigure(2, weight=1)
            self.label(panel, key, font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 6))
            nav = ttk.Frame(panel, height=40)
            nav.grid(row=1, column=0, sticky='ew', pady=(0, 6))
            nav.pack_propagate(False)
            if index == 1:
                self.button(nav, '▲ Précédente', lambda: self.navigate_image(-1)).pack(side='left', expand=True, fill='x', padx=(0, 4))
                self.button(nav, '▼ Suivante', lambda: self.navigate_image(1)).pack(side='left', expand=True, fill='x')
            canvas = tk.Canvas(panel, background=UI.STRUCT_30, highlightthickness=0, width=200, height=300)
            canvas.grid(row=2, column=0, sticky='nsew')
            canvas.bind('<Configure>', lambda event, i=index: self.draw(i))
            canvas.bind('<Double-1>', lambda event, i=index: self.open_image(i))
            self.canvases.append(canvas)
            info = tk.Text(panel, height=5, width=20, wrap='word', relief='flat', padx=8, pady=8,
                           background=UI.PANEL, foreground=UI.TEXT_DARK, state='disabled')
            info.grid(row=3, column=0, sticky='ew', pady=6)
            self.info.append(info)
            actions = ttk.Frame(panel)
            actions.grid(row=4, column=0, sticky='ew')
            self.button(actions, 'Ouvrir l’image', lambda i=index: self.open_image(i)).pack(side='left', expand=True, fill='x', padx=(0, 4))
            self.button(actions, 'Emplacement', lambda i=index: self.open_image(i, True)).pack(side='left', expand=True, fill='x')
            self.button(panel, 'Déplacer dans Doublons', lambda i=index: self.move_one(i), 'Accent.TButton').grid(row=5, column=0, sticky='ew', pady=(8, 0))

    def listbox(self, parent, height, expand=False):
        frame = ttk.Frame(parent)
        frame.pack(fill='both' if expand else 'x', expand=expand, pady=3)
        box = tk.Listbox(frame, height=height, exportselection=False, background=UI.PANEL,
                         foreground=UI.TEXT_DARK, selectbackground=UI.ACCENT_10,
                         selectforeground='white', relief='flat', highlightthickness=0)
        vertical = ttk.Scrollbar(frame, command=box.yview)
        vertical.pack(side='right', fill='y')
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=box.xview)
        horizontal.pack(side='bottom', fill='x')
        box.pack(side='left', fill='both', expand=True)
        box.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        box.bindtags((str(box), str(self.root), box.winfo_class(), 'all'))
        self.controls.append(box)
        return box

    def persist(self):
        self.settings.update(language=i18n.LANGUAGE, folder=self.folder, destination=self.destination,
                             custom_destination=self.custom_destination, recursive=self.recursive.get(),
                             threshold=self.threshold.get())
        save_settings(self.settings_path, self.settings)

    def set_language(self, language):
        if self.busy:
            return
        i18n.LANGUAGE = language
        for widget, key in self.static_text:
            widget.configure(text=tr(key))
        self.persist()
        self.refresh()

    def set_status(self, key, **values):
        self.status_key, self.status_values = key, values
        self.status.configure(text=tr(key, **values))

    def choose_folder(self):
        if self.busy:
            return
        folder = filedialog.askdirectory(parent=self.root, initialdir=self.folder or str(Path.home()))
        if not folder:
            return
        destination = self.destination if self.custom_destination else default_destination(folder)
        if core.is_inside(folder, destination):
            messagebox.showerror(tr('Erreur'), tr('Le dossier analysé ne peut pas se trouver dans le dossier des doublons.'), parent=self.root)
            return
        self.folder, self.destination = folder, destination
        self.records, self.groups, self.errors = [], [], []
        self.indexed_folder = ''
        self.persist()
        self.set_status('Choisissez un dossier, puis lancez l’analyse.')
        self.refresh()

    def choose_destination(self):
        if self.busy:
            return
        destination = filedialog.askdirectory(parent=self.root, initialdir=self.destination if Path(self.destination).is_dir() else str(Path.home()))
        if not destination:
            return
        if self.folder and core.is_inside(self.folder, destination):
            messagebox.showerror(tr('Erreur'), tr('Le dossier analysé ne peut pas se trouver dans le dossier des doublons.'), parent=self.root)
            return
        self.destination, self.custom_destination = destination, True
        self.records = [r for r in self.records if not core.is_inside(r.path, destination)]
        self.filter_groups()
        self.persist()
        self.refresh()

    def start_task(self, kind, task):
        if self.busy:
            return
        self.busy = True
        self.cancel.clear()
        self.pending_result = None
        for control in self.controls:
            control.configure(state='disabled')
        self.stop.configure(state='normal')
        self.progress.start(12)
        def progress(count, name='', total=0):
            self.events.put(('progress', (kind, count, total)))
        def run():
            try:
                result = task(progress)
                self.events.put(('done', (kind, result)))
            except core.Cancelled:
                self.events.put(('cancelled', (kind, None)))
            except Exception as error:
                self.events.put(('error', (kind, str(error))))
        self.worker = threading.Thread(target=run, name='Twins-' + kind, daemon=False)
        self.worker.start()

    def poll(self):
        for _ in range(100):
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == 'progress':
                kind, count, total = payload
                if not self.closing and not self.cancel.is_set():
                    key = {'scan': 'Analyse en cours : {count} fichiers', 'detect': 'Recherche en cours : {count} images',
                           'move': 'Déplacement : {count}/{total}'}[kind]
                    self.set_status(key, count=count, total=total)
            else:
                self.pending_result = (event, payload)
        if self.pending_result and self.worker and not self.worker.is_alive():
            event, (kind, result) = self.pending_result
            self.pending_result, self.worker, self.busy = None, None, False
            self.progress.stop()
            for control in self.controls:
                control.configure(state='normal')
            self.stop.configure(state='disabled')
            if self.closing:
                if self.destroy():
                    return
                self.root.after(80, self.poll)
                return
            if event == 'done':
                self.finish(kind, result)
            elif event == 'cancelled':
                self.set_status('Traitement interrompu.')
                self.refresh()
            else:
                self.errors = [result]
                self.set_status('Erreur')
                self.refresh()
                messagebox.showerror(tr('Erreur'), result, parent=self.root)
        self.root.after(80, self.poll)

    def stop_task(self):
        if self.busy:
            self.cancel.set()
            self.set_status('Arrêt demandé…')

    def scan(self):
        if self.busy:
            return
        if not self.folder:
            messagebox.showinfo(tr('Dossier'), tr('Choisissez d’abord un dossier.'), parent=self.root)
            return
        folder, recursive, destination = self.folder, self.recursive.get(), self.destination
        if core.is_inside(folder, destination):
            messagebox.showerror(tr('Erreur'), tr('Le dossier analysé ne peut pas se trouver dans le dossier des doublons.'), parent=self.root)
            return
        self.persist()
        self.set_status('Analyse en cours : {count} fichiers', count=0)
        def task(progress):
            records, errors = core.scan_folder(folder, recursive, destination, self.cancel, progress)
            groups = core.exact_groups(records, self.cancel)
            core.check_cancel(self.cancel)
            core.save_index(self.data / 'twins_index.db', records, folder)
            return records, groups, errors, folder
        self.start_task('scan', task)

    def detect(self, mode):
        if self.busy:
            return
        if not self.indexed_folder:
            messagebox.showinfo(tr('Informations'), tr('Lancez une analyse avant la détection.'), parent=self.root)
            return
        try:
            threshold = int(self.threshold.get())
            if not 0 <= threshold <= 20:
                raise ValueError()
        except ValueError:
            messagebox.showerror(tr('Erreur'), tr('La tolérance doit être un entier compris entre 0 et 20.'), parent=self.root)
            return
        records = list(self.records)
        self.persist()
        self.set_status('Recherche en cours : {count} images', count=0)
        def task(progress):
            groups = core.exact_groups(records, self.cancel) if mode == 'exact' else core.visual_groups(records, threshold, self.cancel, progress)
            return mode, groups
        self.start_task('detect', task)

    def finish(self, kind, result):
        if kind == 'scan':
            self.records, self.groups, self.errors, self.indexed_folder = result
            self.mode = 'exact'
            self.group_index, self.left_index, self.right_index = 0, 0, 1
            self.set_status('Analyse terminée : {count} images • {errors} erreurs.', count=len(self.records), errors=len(self.errors))
        elif kind == 'detect':
            self.mode, self.groups = result
            self.group_index, self.left_index, self.right_index = 0, 0, 1
            self.set_status('{count} images indexées • {groups} groupes', count=len(self.records), groups=len(self.groups))
        elif kind == 'move':
            moved, errors, cancelled = result
            removed = set(moved)
            self.records = [r for r in self.records if r.path not in removed]
            self.filter_groups()
            self.errors = errors
            if cancelled:
                self.set_status('Traitement interrompu.')
            else:
                self.set_status('Déplacements terminés : {count} fichiers • {errors} erreurs.', count=len(moved), errors=len(errors))
        self.refresh()
        if kind in ('scan', 'move') and self.errors:
            self.report()

    def filter_groups(self):
        available = {r.path for r in self.records}
        self.groups = [[r for r in group if r.path in available] for group in self.groups]
        self.groups = [group for group in self.groups if len(group) > 1]
        self.group_index = min(self.group_index, max(0, len(self.groups) - 1))
        self.left_index, self.right_index = 0, 1

    def current_group(self):
        return self.groups[self.group_index] if self.groups else []

    def current_record(self, panel):
        group = self.current_group()
        index = self.left_index if panel == 0 else self.right_index
        return group[index] if 0 <= index < len(group) else None

    def refresh(self):
        self.folder_label.configure(text=self.folder or tr('Aucun dossier choisi'))
        self.destination_label.configure(text=self.destination)
        self.status.configure(text=tr(self.status_key, **self.status_values))
        self.stop.configure(state='normal' if self.busy else 'disabled')
        for lang, button in self.language_buttons.items():
            button.configure(style='Accent.TButton' if lang == i18n.LANGUAGE else 'Side.TButton')
        self.group_list.delete(0, 'end')
        for index, group in enumerate(self.groups):
            self.group_list.insert('end', f'{index + 1:03d} | {"EXACT" if self.mode == "exact" else tr("VISUEL")} | {len(group)}')
        if self.groups:
            self.group_list.selection_set(self.group_index)
            self.group_list.see(self.group_index)
        else:
            self.group_list.insert('end', tr('Aucun groupe'))
        self.image_list.delete(0, 'end')
        group = self.current_group()
        for index, record in enumerate(group):
            marker = tr('G') if index == self.left_index else tr('D') if index == self.right_index else ''
            self.image_list.insert('end', f'{index + 1}. [{marker}] {Path(record.path).name} | {format_size(record.size)}')
        if group:
            self.image_list.selection_set(self.right_index)
            self.image_list.see(self.right_index)
            self.group_label.configure(text=tr('Doublons exacts' if self.mode == 'exact' else 'Images proches') + ' · ' +
                tr('{count} images • groupe {current}/{total}', count=len(group), current=self.group_index + 1, total=len(self.groups)))
        else:
            self.group_label.configure(text=tr('Aucun résultat dans ce mode' if self.indexed_folder else 'Analyse requise'))
        for panel in (0, 1):
            record = self.current_record(panel)
            if self.preview_images[panel] is not None:
                self.preview_images[panel].close()
            self.preview_images[panel] = None
            self.canvases[panel].preview_error = ''
            text = ''
            if record:
                text = tr('Nom : {name}\nDimensions : {width} × {height} px • Poids : {size}\n{path}',
                          name=Path(record.path).name, width=record.width, height=record.height,
                          size=format_size(record.size), path=record.path)
                try:
                    with Image.open(record.path) as image:
                        with ImageOps.exif_transpose(image) as oriented:
                            oriented.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                            self.preview_images[panel] = oriented.convert('RGBA')
                except (OSError, ValueError, Image.DecompressionBombError) as error:
                    self.canvases[panel].preview_error = str(error)
            widget = self.info[panel]
            widget.configure(state='normal')
            widget.delete('1.0', 'end')
            widget.insert('1.0', text)
            widget.configure(state='disabled')
            self.draw(panel)

    def draw(self, panel):
        canvas = self.canvases[panel]
        canvas.delete('all')
        width, height = max(1, canvas.winfo_width()), max(1, canvas.winfo_height())
        source = self.preview_images[panel]
        if source:
            with source.copy() as image:
                image.thumbnail((max(1, width - 20), max(1, height - 20)), Image.Resampling.LANCZOS)
                self.photo_images[panel] = ImageTk.PhotoImage(image)
            canvas.create_image(width // 2, height // 2, image=self.photo_images[panel])
        else:
            self.photo_images[panel] = None
            error = getattr(canvas, 'preview_error', '')
            text = tr('Aperçu indisponible\n{error}', error=error) if error else tr('Aucun résultat dans ce mode' if self.indexed_folder else 'Analyse requise')
            canvas.create_text(width // 2, height // 2, text=text, fill='white', width=max(1, width - 24), justify='center')

    def select_group(self, event):
        if self.busy:
            return
        selection = self.group_list.curselection()
        if selection and selection[0] < len(self.groups) and selection[0] != self.group_index:
            self.group_index, self.left_index, self.right_index = selection[0], 0, 1
            self.refresh()

    def select_image(self, event):
        if self.busy:
            return
        selection = self.image_list.curselection()
        if selection and selection[0] < len(self.current_group()) and selection[0] not in (self.left_index, self.right_index):
            self.right_index = selection[0]
            self.refresh()

    def navigate_group(self, delta):
        if self.busy or not self.groups:
            return
        self.group_index = max(0, min(len(self.groups) - 1, self.group_index + delta))
        self.left_index, self.right_index = 0, 1
        self.refresh()

    def navigate_image(self, delta):
        if self.busy or not self.current_group():
            return
        count = len(self.current_group())
        index = (self.right_index + delta) % count
        if index == self.left_index:
            index = (index + delta) % count
        self.right_index = index
        self.refresh()

    def swap(self):
        if not self.busy and self.current_group():
            self.left_index, self.right_index = self.right_index, self.left_index
            self.refresh()

    def open(self, path, select=False):
        try:
            open_path(str(path), select)
        except OSError as error:
            messagebox.showerror(tr('Erreur'), str(error), parent=self.root)

    def open_image(self, panel, select=False):
        record = self.current_record(panel)
        if record and not self.busy:
            self.open(record.path, select)

    def move_one(self, panel):
        if self.busy:
            return
        record = self.current_record(panel)
        if record:
            self.move_plan([(record, None)])

    def move_plan(self, plan):
        destination, records, folder = self.destination, list(self.records), self.indexed_folder
        self.set_status('Déplacement : {count}/{total}', count=0, total=len(plan))
        def task(progress):
            moved, errors = [], []
            for index, (record, keeper) in enumerate(plan):
                if self.cancel.is_set():
                    break
                try:
                    core.move_verified(record, destination, self.data / 'moves.jsonl', self.cancel, keeper)
                    moved.append(record.path)
                except core.Cancelled:
                    break
                except core.ChangedFile:
                    errors.append(record.path + ': ' + tr('Cette image a changé depuis l’analyse. Relancez l’analyse avant de la déplacer.'))
                except (OSError, ValueError) as error:
                    errors.append(f'{record.path}: {error}')
                progress(index + 1, total=len(plan))
            remaining = [record for record in records if record.path not in set(moved)]
            try:
                core.save_index(self.data / 'twins_index.db', remaining, folder)
            except (OSError, sqlite3.Error) as error:
                errors.append(str(error))
            return moved, errors, self.cancel.is_set()
        self.start_task('move', task)

    def batch_dialog(self):
        if self.busy:
            return
        groups = core.exact_groups(self.records)
        if not groups:
            messagebox.showinfo(tr('Informations'), tr('Aucun doublon exact à traiter.'), parent=self.root)
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(tr('Traiter les doublons exacts'))
        dialog.transient(self.root)
        apply_app_icon(dialog)
        dialog.resizable(False, False)
        box = ttk.Frame(dialog, padding=20)
        box.pack(fill='both', expand=True)
        ttk.Label(box, text=tr('Fichier à conserver dans chaque groupe'), font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 12))
        rule = tk.StringVar(value='recent')
        for value, label in [('recent', 'Le plus récent (date de modification)'), ('shortest', 'Le nom le plus court'), ('longest', 'Le nom le plus long')]:
            ttk.Radiobutton(box, text=tr(label), value=value, variable=rule).pack(anchor='w', pady=5)
        count = sum(len(group) - 1 for group in groups)
        ttk.Label(box, text=tr('{groups} groupes exacts.\n{count} fichiers seront déplacés ; un fichier restera dans chaque groupe.\n\nDestination :\n{destination}',
                              groups=len(groups), count=count, destination=self.destination), wraplength=530, justify='left').pack(anchor='w', pady=16)
        ttk.Label(box, text=tr('Le fichier conservé et chaque copie sont revérifiés avant déplacement.'), wraplength=530).pack(anchor='w', pady=(0, 16))
        actions = ttk.Frame(box)
        actions.pack(fill='x')
        def confirm():
            plan = []
            for group in groups:
                keeper = core.choose_keeper(group, rule.get())
                plan.extend((record, keeper) for record in group if record != keeper)
            dialog.destroy()
            self.move_plan(plan)
        ttk.Button(actions, text=tr('Annuler'), command=dialog.destroy).pack(side='right')
        ttk.Button(actions, text=tr('Confirmer le déplacement'), style='Accent.TButton', command=confirm).pack(side='right', padx=8)
        self.center_dialog(dialog)
        dialog.grab_set()

    def center_dialog(self, dialog):
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - dialog.winfo_width()) // 2)
        y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - dialog.winfo_height()) // 2)
        dialog.geometry(f'+{x}+{y}')

    def text_dialog(self, title, content, manual=False):
        dialog = tk.Toplevel(self.root)
        dialog.title(tr(title))
        dialog.geometry('730x660')
        dialog.transient(self.root)
        apply_app_icon(dialog)
        bottom = ttk.Frame(dialog, padding=12)
        bottom.pack(side='bottom', fill='x')
        ttk.Button(bottom, text=tr('Fermer'), command=dialog.destroy).pack(side='right')
        if manual:
            ttk.Button(bottom, text=tr('Manuel complet'), command=self.complete_manual).pack(side='left')
            ttk.Button(bottom, text=tr('Journal des déplacements'), command=lambda: self.open(self.data)).pack(side='left', padx=8)
        text = tk.Text(dialog, wrap='word', padx=18, pady=16, background=UI.PANEL, foreground=UI.TEXT_DARK, relief='flat')
        scroll = ttk.Scrollbar(dialog, command=text.yview)
        scroll.pack(side='right', fill='y')
        text.configure(yscrollcommand=scroll.set)
        text.pack(fill='both', expand=True)
        text.insert('1.0', content)
        text.configure(state='disabled')
        self.center_dialog(dialog)
        dialog.grab_set()

    def help(self):
        self.text_dialog('Twins / Manuel', i18n.MANUAL[i18n.LANGUAGE], True)

    def report(self):
        self.text_dialog('Rapport', '\n\n'.join(self.errors) if self.errors else tr('Aucune erreur signalée.'))

    def complete_manual(self):
        try:
            base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
            destination = self.data / 'manuals'
            destination.mkdir(exist_ok=True)
            path = destination / ('Manuel-Twins-' + APP_VERSION + '.html')
            path.write_bytes((base / 'Manuel-Twins.html').read_bytes())
            webbrowser.open(path.as_uri() + '#' + i18n.LANGUAGE)
        except OSError as error:
            messagebox.showerror(tr('Erreur'), str(error), parent=self.root)

    def bind_keys(self):
        def action(callback):
            def run(event):
                if self.busy or event.widget.winfo_toplevel() != self.root:
                    return None
                if isinstance(event.widget, (tk.Entry, ttk.Entry, tk.Text, tk.Spinbox, ttk.Spinbox)):
                    return None
                callback()
                return 'break'
            return run
        for key, callback in [('<Left>', lambda: self.navigate_group(-1)), ('<Right>', lambda: self.navigate_group(1)),
                              ('<Up>', lambda: self.navigate_image(-1)), ('<Down>', lambda: self.navigate_image(1)),
                              ('<Return>', self.swap), ('<Delete>', lambda: self.move_one(1)),
                              ('<Shift-Delete>', lambda: self.move_one(0)), ('1', lambda: self.move_one(0)),
                              ('3', lambda: self.move_one(1))]:
            self.root.bind(key, action(callback))
        self.root.bind('<Escape>', lambda event: self.stop_task())

    def close(self):
        if self.busy:
            self.closing = True
            self.stop_task()
        else:
            self.destroy()

    def destroy(self):
        try:
            self.persist()
        except OSError as error:
            self.closing = False
            messagebox.showerror(tr('Erreur'), str(error), parent=self.root)
            return False
        for image in self.preview_images:
            if image is not None:
                image.close()
        self.root.destroy()
        return True


def main():
    try:
        twins_windows_icon.prepare_identity()
    except (AttributeError, OSError) as error:
        twins_windows_icon.log_error(error)
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
