# Eigrutel Lab / Twins 1.0.0 / 17-09-2026
# Simon Léturgie / Code : GNU AGPL v3.0 ou ultérieure.
"""Local UI foundation matching Photo and Morgue; independent of ui_common.py."""
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import twins_windows_icon

class UI:
    """Palette commune Eigrutel Lab."""
    STRUCT_30 = '#1F3A44'
    TEXT_DARK = "#1F3A44"
    PANEL = '#F7F5F0'
    BORDER = '#D1D6D5'
    ACCENT_10 = '#7F2D30'

def apply_app_icon(window):
    """Shared Morgue icon, renamed Twins, with PNG fallback and native taskbar branding."""
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    success = False
    if sys.platform == 'win32' and (base / 'Twins.ico').is_file():
        try:
            window.iconbitmap(str(base / 'Twins.ico'))
            window.iconbitmap(default=str(base / 'Twins.ico'))
            success = True
        except tk.TclError as error:
            twins_windows_icon.log_error(error)
    if not success and (base / 'Twins.png').is_file():
        try:
            window._app_icon = tk.PhotoImage(file=str(base / 'Twins.png'))
            window.iconphoto(True, window._app_icon)
            success = True
        except tk.TclError as error:
            twins_windows_icon.log_error(error)
    twins_windows_icon.install(window)
    window.after_idle(lambda: twins_windows_icon.set_caption_color(window, UI.STRUCT_30))
    return success

def apply_style(root):
    root.configure(background=UI.PANEL)
    root.option_add('*Font', '{Segoe UI} 10')
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=UI.PANEL, foreground=UI.STRUCT_30, font=('Segoe UI', 10))
    for name in ('App', 'Panel'):
        style.configure(name + '.TFrame', background=UI.PANEL)
    for name in ('Topbar', 'Side'):
        style.configure(name + '.TFrame', background=UI.STRUCT_30)
    for name in ('Topbar', 'SideInfo', 'TopbarTitle', 'SideTitle'):
        style.configure(name + '.TLabel', background=UI.STRUCT_30, foreground='white')
    style.configure('TopbarTitle.TLabel', font=('Segoe UI', 17, 'bold'))
    for name, color in (('Accent', UI.ACCENT_10), ('Side', '#3C4F5F')):
        style.configure(name + '.TButton', background=color, foreground='white', padding=(10, 7), borderwidth=0)
        style.map(name + '.TButton', background=[('active', '#C47A2C')], foreground=[('disabled', '#AAAAAA')])
    style.configure('Topbar.TCheckbutton', background=UI.STRUCT_30, foreground='white')
    style.map('Topbar.TCheckbutton', background=[('active', UI.STRUCT_30)], foreground=[('active', 'white')])
    style.configure('Tag.TCheckbutton', background=UI.PANEL)
    style.configure('TEntry', fieldbackground='white', padding=4)
