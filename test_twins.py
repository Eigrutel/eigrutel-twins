"""Tests of actual indexing and file operations on temporary images.
Eigrutel Lab / Simon Léturgie / AGPL-3.0-or-later.
"""
import dataclasses
import json
import os
import random
import shutil
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import twins_core as core
import twins_i18n as i18n
from EigrutelTwins import load_settings, save_settings


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        self.destination = self.base / 'Doublons'
        self.journal = self.base / 'moves.jsonl'
        self.first = self.source / 'first.png'
        Image.new('RGB', (32, 24), 'red').save(self.first)
        self.second = self.source / 'copy.png'
        shutil.copy2(self.first, self.second)

    def records(self):
        records, errors = core.scan_folder(self.source)
        self.assertFalse(errors)
        return records

    def test_exact_detection(self):
        records = self.records()
        groups = core.exact_groups(records)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)
        self.assertEqual(groups[0][0].sha256, groups[0][1].sha256)

    def test_visual_hash_not_proof_of_identity(self):
        Image.new('RGB', (32, 24), 'blue').save(self.second)
        records = self.records()
        self.assertEqual(core.exact_groups(records), [])
        self.assertEqual(len(core.visual_groups(records, 0)), 1)

    def test_visual_groups_keep_dimension_rule(self):
        Image.new('RGB', (64, 48), 'red').save(self.second)
        self.assertEqual(core.visual_groups(self.records(), 20), [])

    def test_hash_tree_matches_exhaustive_search(self):
        rng = random.Random(43)
        hashes = [rng.getrandbits(64) for _ in range(250)]
        hashes.extend([hashes[0], hashes[0] ^ 3])
        tree = core.HashTree()
        for index, value in enumerate(hashes):
            tree.add(value, index)
        for threshold in (0, 2, 5, 20):
            expected = {index for index, value in enumerate(hashes) if (hashes[0] ^ value).bit_count() <= threshold}
            self.assertEqual(set(tree.near(hashes[0], threshold)), expected)

    def test_visual_anchor_group_is_not_transitive(self):
        record = self.records()[0]
        rows = [dataclasses.replace(record, path=str(self.source / name), visual_hash=value)
                for name, value in [('a', 0), ('b', 1), ('c', 3)]]
        groups = core.visual_groups(rows, 1)
        self.assertEqual([[Path(r.path).name for r in g] for g in groups], [['a', 'b']])

    def test_exif_orientation(self):
        exif = Image.Exif()
        exif[274] = 6
        image = self.source / 'rotated.jpg'
        Image.new('RGB', (120, 80)).save(image, exif=exif)
        record = next(r for r in self.records() if r.path == str(image))
        self.assertEqual((record.width, record.height), (80, 120))

    def test_unsupported_and_unreadable_images(self):
        (self.source / 'not_an_image.jpg').write_text('broken')
        (self.source / 'notes.txt').write_text('not indexed')
        records, errors = core.scan_folder(self.source)
        self.assertEqual(len(records), 2)
        self.assertEqual(len(errors), 1)
        self.assertIn('not_an_image.jpg', errors[0])

    def test_recursive_scan_and_destination_exclusion(self):
        child = self.source / 'child'
        child.mkdir()
        shutil.copy2(self.first, child / 'other.png')
        ignored = self.source / 'Doublons'
        ignored.mkdir()
        shutil.copy2(self.first, ignored / 'old.png')
        destination = self.source / 'set_aside'
        destination.mkdir()
        shutil.copy2(self.first, destination / 'moved.png')
        rows, _ = core.scan_folder(self.source, destination=destination)
        self.assertEqual(len(rows), 3)
        rows, _ = core.scan_folder(self.source, recursive=False, destination=destination)
        self.assertEqual(len(rows), 2)

    def test_scan_cancelled(self):
        event = threading.Event()
        event.set()
        with self.assertRaises(core.Cancelled):
            core.scan_folder(self.source, cancel=event)

    def test_index_transaction_preserves_prior_index_on_failure(self):
        rows = self.records()
        db = self.base / 'index.db'
        core.save_index(db, rows, str(self.source))
        with self.assertRaises(sqlite3.IntegrityError):
            core.save_index(db, [rows[0], rows[0]], 'replacement')
        with sqlite3.connect(db) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM images').fetchone()[0], 2)
            self.assertEqual(connection.execute('SELECT value FROM metadata WHERE key="folder"').fetchone()[0], str(self.source))

    def test_move_preserves_bytes_and_writes_log(self):
        record = self.records()[0]
        source = Path(record.path)
        contents = source.read_bytes()
        target = Path(core.move_verified(record, self.destination, self.journal))
        self.assertFalse(source.exists())
        self.assertEqual(target.read_bytes(), contents)
        entries = [json.loads(line) for line in self.journal.read_text().splitlines()]
        self.assertEqual([r['status'] for r in entries], ['prepared', 'completed'])
        self.assertEqual(entries[0]['source'], str(source))
        self.assertEqual(entries[0]['destination'], str(target))

    def test_move_never_uses_cross_drive_rename(self):
        record = self.records()[0]
        with patch('os.rename', side_effect=OSError('EXDEV')), patch('os.replace', side_effect=OSError('EXDEV')):
            target = core.move_verified(record, self.destination, self.journal)
        self.assertTrue(Path(target).exists())

    def test_collision_uses_new_name(self):
        record = self.records()[0]
        self.destination.mkdir()
        original_target = self.destination / Path(record.path).name
        original_target.write_bytes(b'existing')
        target = Path(core.move_verified(record, self.destination, self.journal))
        self.assertNotEqual(target, original_target)
        self.assertEqual(original_target.read_bytes(), b'existing')
        self.assertEqual(core.sha256_file(target), record.sha256)

    def test_changed_source_stays_in_place(self):
        record = self.records()[0]
        Path(record.path).write_bytes(b'changed after indexing')
        with self.assertRaises(core.ChangedFile):
            core.move_verified(record, self.destination, self.journal)
        self.assertTrue(Path(record.path).exists())
        self.assertFalse(self.destination.exists())

    def test_changed_content_even_with_restored_timestamp_is_rejected(self):
        record = self.records()[0]
        path = Path(record.path)
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        os.utime(path, ns=(record.mtime_ns, record.mtime_ns))
        with self.assertRaises(core.ChangedFile):
            core.move_verified(record, self.destination, self.journal)
        self.assertTrue(path.exists())

    def test_changed_keeper_blocks_copy_removal(self):
        first, second = self.records()
        Path(first.path).write_bytes(b'changed reference')
        with self.assertRaises(core.ChangedFile):
            core.move_verified(second, self.destination, self.journal, keeper=first)
        self.assertTrue(Path(second.path).exists())

    def test_missing_keeper_blocks_copy_removal(self):
        keeper, record = self.records()
        Path(keeper.path).unlink()
        with self.assertRaises(core.ChangedFile):
            core.move_verified(record, self.destination, self.journal, keeper=keeper)
        self.assertTrue(Path(record.path).exists())

    def test_keep_rules_and_ties_are_deterministic(self):
        records = self.records()
        self.assertEqual(Path(core.choose_keeper(records, 'shortest').path).name, 'copy.png')
        self.assertEqual(Path(core.choose_keeper(records, 'longest').path).name, 'first.png')
        self.assertEqual(core.choose_keeper(records, 'recent'), core.choose_keeper(list(reversed(records)), 'recent'))

    def test_journal_failure_preserves_source(self):
        record = self.records()[0]
        with patch.object(core, 'append_journal', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                core.move_verified(record, self.destination, self.journal)
        self.assertTrue(Path(record.path).exists())
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_cancel_during_copy_keeps_source(self):
        record = self.records()[0]
        event = threading.Event()
        original = core.sha256_file
        def digest(path, cancel=None):
            value = original(path, cancel)
            if Path(path).parent == self.destination:
                event.set()
            return value
        with patch.object(core, 'sha256_file', side_effect=digest):
            with self.assertRaises(core.Cancelled):
                core.move_verified(record, self.destination, self.journal, event)
        self.assertTrue(Path(record.path).exists())
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_corrupt_copy_keeps_source(self):
        record = self.records()[0]
        original = core.sha256_file
        def digest(path, cancel=None):
            return 'wrong' if Path(path).parent == self.destination else original(path, cancel)
        with patch.object(core, 'sha256_file', side_effect=digest):
            with self.assertRaises(core.ChangedFile):
                core.move_verified(record, self.destination, self.journal)
        self.assertTrue(Path(record.path).exists())
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_settings_are_separate_and_unicode_safe(self):
        path = self.base / 'settings.json'
        save_settings(path, {'language': 'en', 'folder': 'été'})
        self.assertEqual(load_settings(path), {'language': 'en', 'folder': 'été'})
        path.write_text('broken')
        self.assertEqual(load_settings(path), {})

    def test_translations_and_manuals(self):
        with patch.object(i18n, 'LANGUAGE', 'en'):
            self.assertEqual(i18n.tr('Doublons exacts'), 'Exact duplicates')
            self.assertEqual(i18n.tr('mon-image.png'), 'mon-image.png')
            self.assertEqual(i18n.tr('Déplacement : {count}/{total}', count=1, total=2), 'Moving: 1/2')
        self.assertIn('SHA-256', i18n.MANUAL['fr'])
        self.assertIn('SHA-256', i18n.MANUAL['en'])


if __name__ == '__main__':
    unittest.main()
