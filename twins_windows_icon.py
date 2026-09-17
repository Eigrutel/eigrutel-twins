# Eigrutel Lab - Atelier d'outils libres pour la bande dessinée
# Programme conçu et développé par Simon Léturgie dans le cadre d'Eigrutel BD Academy.
# Nom : Twins | Version : 1.0.0 | Date : 17-09-2026
# Code : GNU AGPL v3.0 ou version ultérieure.
# Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
# Marques et logos Eigrutel / Eigrutel Lab / Eigrutel BD Academy : réservés.

"""Windows taskbar branding, applied to the native Tk wrapper after mapping.
Code: GNU AGPL v3 or later. Eigrutel Lab / Simon Léturgie.
"""
import sys
import os


def prepare_identity():
    if sys.platform != 'win32':
        return
    import ctypes
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    function = shell.SetCurrentProcessExplicitAppUserModelID
    function.argtypes = [ctypes.c_wchar_p]
    function.restype = ctypes.c_long
    if function('EigrutelLab.Twins.Desktop') < 0:
        raise OSError('Windows rejected the Twins application identity')


def windows_api():
    import ctypes
    from ctypes import wintypes
    api = ctypes.WinDLL('user32', use_last_error=True)
    api.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    api.GetAncestor.restype = wintypes.HWND
    api.GetSystemMetrics.argtypes = [ctypes.c_int]
    api.GetSystemMetrics.restype = ctypes.c_int
    api.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                              ctypes.c_int, ctypes.c_int, wintypes.UINT]
    api.LoadImageW.restype = wintypes.HANDLE
    api.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
    api.SendMessageW.restype = ctypes.c_ssize_t
    api.DestroyIcon.argtypes = [wintypes.HANDLE]
    api.DestroyIcon.restype = wintypes.BOOL
    return api


class WindowIcons:
    def __init__(self, api, path):
        self.api, self.path, self.handles = api, path, []

    def apply(self, tk_window_id):
        # GA_ROOT reaches the native top-level wrapper, not the Tk client widget.
        hwnd = self.api.GetAncestor(tk_window_id, 2)
        if not hwnd:
            raise OSError('Native Twins window not available')
        if not self.handles:
            try:
                for metric_x, metric_y in ((49,50),(11,12)):
                    handle = self.api.LoadImageW(None, self.path, 1,
                        max(16,self.api.GetSystemMetrics(metric_x)),
                        max(16,self.api.GetSystemMetrics(metric_y)), 0x10)
                    if not handle:
                        raise OSError('Windows could not load Twins.ico')
                    self.handles.append(handle)
            except OSError:
                self.close()
                raise
        for kind, handle in enumerate(self.handles):
            self.api.SendMessageW(hwnd, 0x80, kind, handle)  # WM_SETICON, small/big
            if self.api.SendMessageW(hwnd, 0x7F, kind, 0) != handle:  # WM_GETICON
                raise OSError('Windows did not retain the Twins icon')

    def close(self):
        for handle in self.handles:
            self.api.DestroyIcon(handle)
        self.handles.clear()


def log_error(error):
    try:
        directory = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~/.local/share')), 'EigrutelLab', 'Twins', 'logs')
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, 'twins-icons.log'), 'a', encoding='utf-8') as stream:
            stream.write('Taskbar: '+str(error)+'\n')
    except OSError:
        pass


def install(root):
    if sys.platform != 'win32':
        return
    path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), 'Twins.ico')
    try:
        icons = WindowIcons(windows_api(), path)
    except (AttributeError, OSError) as error:
        log_error(error)
        return
    root._native_twins_icons = icons
    queued = False
    closed = False
    def apply():
        nonlocal queued
        queued = False
        if closed:
            return
        try:
            icons.apply(root.winfo_id())
        except OSError as error:
            log_error(error)
    def schedule(event=None):
        nonlocal queued
        if closed or queued or (event is not None and event.widget is not root):
            return
        queued = True
        root.after_idle(apply)
    def cleanup(event):
        nonlocal closed
        if event.widget is root:
            closed = True
            icons.close()
    root.bind('<Map>', schedule, add='+')
    root.bind('<Destroy>', cleanup, add='+')
    schedule()


def colorref(hex_color):
    value = hex_color.lstrip('#')
    red, green, blue = (int(value[i:i+2],16) for i in (0,2,4))
    return red | (green << 8) | (blue << 16)


def set_caption_color(root, background):
    """Windows 11 native title bar; unsupported systems keep their own chrome."""
    if sys.platform != 'win32':
        return False
    import ctypes
    from ctypes import wintypes
    try:
        api = windows_api()
        hwnd = api.GetAncestor(root.winfo_id(),2)
        if not hwnd:
            return False
        dwm = ctypes.WinDLL('dwmapi',use_last_error=True)
        setter = dwm.DwmSetWindowAttribute
        setter.argtypes = [wintypes.HWND,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD]
        setter.restype = ctypes.c_long
        succeeded = True
        for attribute, value in ((20,1),(35,colorref(background)),(36,colorref('#FAFAF7')),
                                 (34,0xFFFFFFFE)):
            payload = wintypes.DWORD(value)
            result = setter(hwnd,attribute,ctypes.byref(payload),ctypes.sizeof(payload))
            succeeded = result >= 0 and succeeded
        return succeeded
    except (AttributeError,OSError):
        return False
