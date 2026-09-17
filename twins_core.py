# Eigrutel Lab / Twins 1.0.0 / 17-09-2026
# Simon Léturgie / Code : GNU AGPL v3.0 ou ultérieure.
"""Image indexing, comparisons and verified moves. No Tk calls in this module."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from PIL import Image, ImageOps

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp', '.gif'}
IGNORED = {'doublons', '_doublons', '.git', '.venv'}


class Cancelled(Exception):
    """User requested interruption; completed moves remain valid."""


class ChangedFile(Exception):
    """The current file no longer matches the indexed file."""


def check_cancel(event):
    if event is not None and event.is_set():
        raise Cancelled()


def canonical(path):
    return os.path.normcase(os.path.abspath(path))


def is_inside(path, directory):
    try:
        return os.path.commonpath([canonical(path), canonical(directory)]) == canonical(directory)
    except ValueError:
        return False


def fingerprint(path):
    stat = os.stat(path, follow_symlinks=False)
    return stat.st_size, stat.st_mtime_ns, stat.st_dev, stat.st_ino


def sha256_file(path, cancel=None):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            check_cancel(cancel)
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def dhash(image, size=8):
    """64-bit luminance gradient; similarity is not proof of identical content."""
    with image.convert('L') as gray:
        with gray.resize((size + 1, size), Image.Resampling.LANCZOS) as small:
            pixels = small.tobytes()
    result = 0
    for y in range(size):
        for x in range(size):
            if pixels[y * (size + 1) + x] > pixels[y * (size + 1) + x + 1]:
                result |= 1 << (y * size + x)
    return result


@dataclass(frozen=True)
class Record:
    path: str
    size: int
    mtime_ns: int
    device: int
    inode: int
    width: int
    height: int
    sha256: str
    visual_hash: int

    @property
    def stamp(self):
        return self.size, self.mtime_ns, self.device, self.inode


def iter_images(folder, recursive=True, destination=None, cancel=None, errors=None):
    def on_error(error):
        if errors is not None:
            errors.append(str(error))
    for directory, subdirs, filenames in os.walk(folder, followlinks=False, onerror=on_error):
        check_cancel(cancel)
        subdirs[:] = sorted(d for d in subdirs
                            if d.casefold() not in IGNORED
                            and not Path(directory, d).is_symlink()
                            and not (destination and is_inside(Path(directory, d), destination)))
        for name in sorted(filenames, key=str.casefold):
            check_cancel(cancel)
            path = Path(directory, name)
            if (path.suffix.lower() in SUPPORTED and not path.is_symlink()
                    and path.is_file() and not (destination and is_inside(path, destination))):
                yield str(path.absolute())
        if not recursive:
            break


def scan_folder(folder, recursive=True, destination=None, cancel=None, progress=None):
    if not Path(folder).is_dir():
        raise FileNotFoundError(folder)
    records, errors = [], []
    for done, path in enumerate(iter_images(folder, recursive, destination, cancel, errors), 1):
        try:
            before = fingerprint(path)
            digest = sha256_file(path, cancel)
            with Image.open(path) as original:
                with ImageOps.exif_transpose(original) as oriented:
                    width, height = oriented.size
                    visual = dhash(oriented)
            after = fingerprint(path)
            if before != after:
                raise ChangedFile(path)
            records.append(Record(path, *before, width, height, digest, visual))
        except Cancelled:
            raise
        except (OSError, ValueError, SyntaxError, Image.DecompressionBombError, ChangedFile) as error:
            errors.append(f'{path}: {error}')
        if progress and (done == 1 or done % 10 == 0):
            progress(done, Path(path).name)
    check_cancel(cancel)
    return records, errors


def save_index(database, records, folder):
    """Atomically replace the old index only after a complete scan."""
    connection = sqlite3.connect(database)
    try:
        with connection:
            connection.execute(
                'CREATE TABLE IF NOT EXISTS images '
                '(path TEXT PRIMARY KEY, size INTEGER, mtime_ns INTEGER, device INTEGER, '
                'inode TEXT, width INTEGER, height INTEGER, sha256 TEXT, visual_hash TEXT)'
            )
            connection.execute(
                'CREATE TABLE IF NOT EXISTS metadata '
                '(key TEXT PRIMARY KEY, value TEXT)'
            )
            connection.execute('DELETE FROM images')
            connection.executemany(
                'INSERT INTO images VALUES (?,?,?,?,?,?,?,?,?)',
                [
                    (
                        r.path,
                        r.size,
                        r.mtime_ns,
                        r.device,
                        str(r.inode),
                        r.width,
                        r.height,
                        r.sha256,
                        f'{r.visual_hash:016x}',
                    )
                    for r in records
                ],
            )
            connection.execute(
                'INSERT OR REPLACE INTO metadata VALUES (?,?)',
                ('folder', folder),
            )
    finally:
        connection.close()


def exact_groups(records, cancel=None):
    groups = defaultdict(list)
    for record in records:
        check_cancel(cancel)
        groups[record.sha256].append(record)
    return sorted([sorted(g, key=lambda r: r.path.casefold()) for g in groups.values() if len(g) > 1],
                  key=lambda g: (-len(g), g[0].path.casefold()))


class HashTree:
    """Iterative BK tree for radius queries in Hamming distance."""
    def __init__(self):
        self.root = None

    def add(self, value, index):
        if self.root is None:
            self.root = [value, [index], {}]
            return
        node = self.root
        while True:
            distance = (value ^ node[0]).bit_count()
            if distance == 0:
                node[1].append(index)
                return
            if distance not in node[2]:
                node[2][distance] = [value, [index], {}]
                return
            node = node[2][distance]

    def near(self, value, threshold, cancel=None):
        stack = [self.root] if self.root else []
        result = []
        while stack:
            check_cancel(cancel)
            node = stack.pop()
            distance = (value ^ node[0]).bit_count()
            if distance <= threshold:
                result.extend(node[1])
            stack.extend(child for edge, child in node[2].items()
                         if distance - threshold <= edge <= distance + threshold)
        return result


def visual_groups(records, threshold=5, cancel=None, progress=None):
    if not 0 <= threshold <= 20:
        raise ValueError('0 <= threshold <= 20')
    rows = sorted(records, key=lambda r: r.path.casefold())
    trees = defaultdict(HashTree)
    for index, record in enumerate(rows):
        check_cancel(cancel)
        trees[(record.width, record.height)].add(record.visual_hash, index)
    used, groups = set(), []
    for index, record in enumerate(rows):
        check_cancel(cancel)
        if index in used:
            continue
        neighbors = trees[(record.width, record.height)].near(record.visual_hash, threshold, cancel)
        indexes = [index] + sorted(j for j in neighbors if j > index and j not in used)
        if len(indexes) > 1:
            groups.append([rows[j] for j in indexes])
            used.update(indexes)
        if progress and index % 100 == 0:
            progress(index + 1, '')
    return sorted(groups, key=lambda group: (-len(group), group[0].path.casefold()))


def choose_keeper(group, rule):
    if rule == 'recent':
        return min(group, key=lambda r: (-r.mtime_ns, r.path.casefold()))
    if rule == 'shortest':
        return min(group, key=lambda r: (len(Path(r.path).name), r.path.casefold()))
    if rule == 'longest':
        return min(group, key=lambda r: (-len(Path(r.path).name), r.path.casefold()))
    raise ValueError(rule)


def verify_record(record, cancel=None):
    path = Path(record.path)
    if path.is_symlink() or not path.is_file() or fingerprint(path) != record.stamp:
        raise ChangedFile(record.path)
    digest = sha256_file(path, cancel)
    if digest != record.sha256 or fingerprint(path) != record.stamp:
        raise ChangedFile(record.path)


def append_journal(journal, entry):
    entry = dict(entry, timestamp=datetime.now(timezone.utc).isoformat())
    with open(journal, 'a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def move_verified(record, destination, journal, cancel=None, keeper=None):
    """Copy exclusively, verify, journal, then remove the source; works across volumes.

    The retained exact duplicate is verified again immediately before removing
    its copy. A failed/cancelled copy leaves the source in place. The durable
    prepared journal entry records recovery paths even if final logging fails.
    """
    check_cancel(cancel)
    verify_record(record, cancel)
    if keeper:
        if canonical(keeper.path) == canonical(record.path) or keeper.sha256 != record.sha256:
            raise ValueError('Invalid retained duplicate')
        verify_record(keeper, cancel)
    source = Path(record.path)
    destination = Path(destination).absolute()
    if canonical(source.parent) == canonical(destination):
        raise ValueError('Source already in destination')
    destination.mkdir(parents=True, exist_ok=True)
    counter = 0
    while True:
        check_cancel(cancel)
        name = source.name if not counter else f'{source.stem}_{counter}{source.suffix}'
        target = destination / name
        try:
            output = target.open('xb')
            break
        except FileExistsError:
            counter += 1
    removed = False
    try:
        with output, source.open('rb') as stream:
            while True:
                check_cancel(cancel)
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        if sha256_file(target, cancel) != record.sha256:
            raise ChangedFile(str(target))
        if fingerprint(source) != record.stamp:
            raise ChangedFile(str(source))
        shutil.copystat(source, target, follow_symlinks=False)
        if keeper:
            verify_record(keeper, cancel)
        check_cancel(cancel)
        if fingerprint(source) != record.stamp:
            raise ChangedFile(str(source))
        entry = {'source': str(source), 'destination': str(target), 'sha256': record.sha256}
        append_journal(journal, dict(entry, status='prepared'))
        source.unlink()
        removed = True
        try:
            append_journal(journal, dict(entry, status='completed'))
        except OSError:
            # The durable prepared entry already contains the complete move.
            pass
        return str(target)
    finally:
        if not removed:
            target.unlink(missing_ok=True)
