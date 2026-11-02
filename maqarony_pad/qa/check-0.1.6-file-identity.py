#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.6 Audit Item 23 regression contract."""
from __future__ import annotations

import hashlib
import os
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import document_io  # noqa: E402
import settings_io  # noqa: E402

APP = (ROOT / "markopad.py").read_text(encoding="utf-8")
DOC_IO = (ROOT / "document_io.py").read_text(encoding="utf-8")

assert 'APP_VERSION = "0.1.6"' in APP

# Item 23 only: preserve the opened path entry separately from its regular-file
# target, and use that identity only for change detection / safe Save.
assert 'def absolute_user_path(' in DOC_IO
assert 'path_before = os.lstat(path)' in DOC_IO
assert 'target_before = os.fstat(descriptor)' in DOC_IO
assert 'def validated_symlink_target(path: Path, expected: FileState) -> Path:' in DOC_IO
assert 'if expected.state.is_symlink' in DOC_IO
assert 'self.backing_path: Path | None = None' in APP
assert 'source_path = self.backing_path or self.current_path' in APP
assert 'self.backing_path or self.current_path,' in APP

# Rename/Delete semantics are explicitly NOT redefined by Item 23. They continue
# on the historical resolved current_path and then discard any prior symlink seam.
assert 'self.current_path = target\n        self.backing_path = target' in APP
assert 'self.backing_path = self.current_path\n        self._set_backing_state("missing")' in APP

# Direct filesystem contract: an unchanged symlink is preserved while its regular
# target is atomically replaced; retargeting/replacement races are refused.
with tempfile.TemporaryDirectory(prefix="markopad-identity-qa-") as raw_root:
    root = Path(raw_root)
    regular = root / "regular.md"
    regular.write_text("alpha", encoding="utf-8")
    _data, regular_snapshot = document_io.read_regular_file(regular)
    saved_regular = document_io.safe_atomic_save(
        regular, "beta", expected=regular_snapshot
    )
    assert regular.read_text(encoding="utf-8") == "beta"
    assert saved_regular.state.is_symlink is False

    if hasattr(os, "symlink"):
        target = root / "target.md"
        link = root / "opened.md"
        target.write_text("one", encoding="utf-8")
        try:
            link.symlink_to(target.name)
        except (OSError, NotImplementedError):
            link = None
        if link is not None:
            original_link = os.lstat(link)
            payload, snapshot = document_io.read_regular_file(link)
            assert payload == b"one"
            assert snapshot.state.is_symlink
            assert snapshot.state.path_inode == original_link.st_ino
            assert snapshot.state.target_inode == os.stat(target).st_ino

            saved = document_io.safe_atomic_save(link, "two", expected=snapshot)
            assert link.is_symlink()
            assert os.lstat(link).st_ino == original_link.st_ino
            assert target.read_text(encoding="utf-8") == "two"
            assert saved.state.is_symlink

            # Retargeting the same path entry is a conflict; neither file is written.
            _payload, before_retarget = document_io.read_regular_file(link)
            other = root / "other.md"
            other.write_text("two", encoding="utf-8")
            link.unlink()
            link.symlink_to(other.name)
            try:
                document_io.safe_atomic_save(link, "three", expected=before_retarget)
            except document_io.FileStateChangedError:
                pass
            else:
                raise AssertionError("retargeted symlink was not rejected")
            assert target.read_text(encoding="utf-8") == "two"
            assert other.read_text(encoding="utf-8") == "two"

            # Replacing the target behind an unchanged symlink is also a conflict.
            link.unlink()
            link.symlink_to(target.name)
            _payload, before_replace = document_io.read_regular_file(link)
            old_target = root / "old-target.md"
            target.rename(old_target)
            target.write_text("two", encoding="utf-8")
            try:
                document_io.safe_atomic_save(link, "three", expected=before_replace)
            except document_io.FileStateChangedError:
                pass
            else:
                raise AssertionError("replaced symlink target was not rejected")
            assert target.read_text(encoding="utf-8") == "two"

# Protected Item 14 remains present.
assert 'self.editor.document().undoAvailable.connect(lambda _available: self._sync_undo_redo_state())' in APP
assert 'self.editor.document().redoAvailable.connect(lambda _available: self._sync_undo_redo_state())' in APP
assert 'self.undo_action.setEnabled(mutable and document.isUndoAvailable())' in APP
assert 'self.redo_action.setEnabled(mutable and document.isRedoAvailable())' in APP

# Protected Item 6: successful Delete still preserves the live editor.
assert '# Keep the live editor. It is now the only guaranteed surviving copy.' in APP
assert 'File deleted from disk; the open document is retained.' in APP

# Protected Item 16: no second Undo/Redo action ownership path was added.
assert APP.count('self.undo_action = self._action("Undo"') == 1
assert APP.count('self.redo_action = self._action("Redo"') == 1

# Protected Item 22: persistence helper is unchanged from 0.1.5 and still works.
assert hashlib.sha256((ROOT / 'settings_io.py').read_bytes()).hexdigest() == '9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159'
with tempfile.TemporaryDirectory(prefix="markopad-settings-carry-forward-") as raw_root:
    config = Path(raw_root) / "private" / "markopad.json"
    expected = {"theme": "system", "toolbar": "tabbed"}
    assert settings_io.save_settings(config, expected) is True
    assert settings_io.load_settings(config) == expected
    if os.name == "posix":
        assert stat.S_IMODE(os.lstat(config.parent).st_mode) == 0o700
        assert stat.S_IMODE(os.lstat(config).st_mode) == 0o600

# Protected editor/presentation modules are byte-for-byte unchanged from 0.1.5.
protected = {
    'source_editor.py': '0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327',
    'preview.py': 'e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965',
    'legacy_ricopad.py': '2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40',
}
for name, digest in protected.items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)

print('Markopad 0.1.6 path/target identity contract passed.')
