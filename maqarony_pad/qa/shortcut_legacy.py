#!/usr/bin/env python3
"""Read original pure shortcut-helper prefix for historical regression fingerprints."""
from pathlib import Path


def legacy_read_bytes(root: Path, rel: str) -> bytes:
    if rel != 'widgets/shortcut_search.py':
        return (root/rel).read_bytes()
    source = (root/'widgets/keyboard_shortcuts.py').read_bytes()
    boundary = bytes([10]) + b'from PyQt6.QtCore import Qt'
    assert source.count(boundary) == 1, 'dialog module boundary moved'
    old = source.split(boundary,1)[0].rstrip() + bytes([10])
    return old
