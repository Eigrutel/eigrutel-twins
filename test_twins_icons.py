"""Icon encoding, PE resource validation and window icon regression checks."""
from pathlib import Path
import struct
import unittest
from unittest.mock import Mock, patch
from PIL import Image
import build_windows as build
import twins_ui as ui_common

BASE = Path(__file__).parent


class IconTests(unittest.TestCase):
    def test_nine_bitmap_sizes_decode(self):
        payloads = build.read_ico_payloads(BASE/'Twins.ico')
        self.assertEqual(len(payloads),9)
        self.assertTrue(all(struct.unpack_from('<I',p)[0] == 40 for p in payloads))
        with Image.open(BASE/'Twins.ico') as icon:
            sizes={(n,n) for n in (16,20,24,32,40,48,64,128,256)}
            self.assertEqual(icon.ico.sizes(),sizes)
            for size in sizes:
                self.assertEqual(icon.ico.getimage(size).size,size)

    def test_resource_group_must_contain_the_supplied_images(self):
        payloads=build.read_ico_payloads(BASE/'Twins.ico')
        directory=(BASE/'Twins.ico').read_bytes()
        group=directory[:6]+b''.join(directory[6+16*i:6+16*i+12]+struct.pack('<H',i+1) for i in range(len(payloads)))
        icons={i+1:p for i,p in enumerate(payloads)}
        self.assertTrue(build.matching_icon_group(payloads,icons,[group]))
        self.assertFalse(build.matching_icon_group(payloads,icons,[]))
        icons[1]=b'wrong icon'
        self.assertFalse(build.matching_icon_group(payloads,icons,[group]))

    def test_windows_sets_current_window_and_default(self):
        window=Mock()
        with patch.object(ui_common.sys,'platform','win32'), patch('twins_windows_icon.install'):
            self.assertTrue(ui_common.apply_app_icon(window))
        self.assertEqual(window.iconbitmap.call_count,2)
        self.assertTrue(window.iconbitmap.call_args_list[0].args[0].endswith('Twins.ico'))
        self.assertIn('default',window.iconbitmap.call_args_list[1].kwargs)
        window.iconphoto.assert_not_called()

    def test_failed_ico_uses_png_fallback(self):
        window=Mock()
        window.iconbitmap.side_effect=ui_common.tk.TclError('ICO rejected')
        with patch.object(ui_common.sys,'platform','win32'), patch('tkinter.PhotoImage',return_value=object()), patch('twins_windows_icon.install'):
            self.assertTrue(ui_common.apply_app_icon(window))
        self.assertIsNotNone(window._app_icon)
        window.iconphoto.assert_called_once()


class NativeTaskbarTests(unittest.TestCase):
    def api(self):
        api = Mock()
        api.GetAncestor.return_value = 500
        api.GetSystemMetrics.return_value = 32
        api.LoadImageW.side_effect = [1001,1002]
        stored = {}
        def message(hwnd, msg, kind, value):
            if msg == 0x80:
                stored[(hwnd,kind)] = value
                return 0
            return stored.get((hwnd,kind),0)
        api.SendMessageW.side_effect = message
        return api

    def test_small_and_large_icons_target_native_wrapper(self):
        from twins_windows_icon import WindowIcons
        api = self.api()
        icons = WindowIcons(api,'Twins.ico')
        icons.apply(123)
        api.GetAncestor.assert_called_once_with(123,2)
        api.SendMessageW.assert_any_call(500,0x80,0,1001)
        api.SendMessageW.assert_any_call(500,0x80,1,1002)

    def test_remapping_reuses_handles_and_shutdown_frees_them(self):
        from twins_windows_icon import WindowIcons
        api = self.api()
        icons = WindowIcons(api,'Twins.ico')
        icons.apply(123)
        icons.apply(123)
        self.assertEqual(api.LoadImageW.call_count,2)
        icons.close()
        icons.close()
        self.assertEqual(api.DestroyIcon.call_count,2)

    def test_partial_loading_failure_releases_allocated_icon(self):
        from twins_windows_icon import WindowIcons
        api = self.api()
        api.LoadImageW.side_effect = [1001,0]
        icons = WindowIcons(api,'Twins.ico')
        with self.assertRaises(OSError):
            icons.apply(123)
        api.DestroyIcon.assert_called_once_with(1001)
        self.assertEqual(icons.handles,[])


if __name__=='__main__':
    unittest.main()
